"""
Response parser.

Converts raw Ollama model output into a validated LearningSession.

Pipeline
--------
    raw text (from Ollama 'response' field)
        ↓
    _strip_code_fences()          — remove ```json ... ``` wrappers if present
        ↓
    json.loads()                  — parse to Python dict
        ↓
    _normalize_model_output()     — fix double-encoded nested JSON strings
        ↓
    _coerce_string_list_fields()  — fix dicts accidentally placed in string-list fields
        ↓
    LearningSession.model_validate()  — Pydantic validation
        ↓
    LearningSession

All failures raise OllamaResponseError with a safe user-facing message.
Internal details (tracebacks, raw JSON) are logged server-side only.

Normalization
-------------
Small models (1B parameters) exhibit two known quirks:

1. Double-encoded nested fields:
   "topic_breakdown": "[{\"heading\": \"...\"}]"   (string, not array)
   → _normalize_model_output() decodes with json.loads

2. Wrong type in string-list fields:
   "practice_questions": [{"question": "..."}, ...]  (dicts, not strings)
   "revision_checklist": [{"heading": "..."}, ...]
   → _coerce_string_list_fields() extracts the first string value from the dict

eval() is NEVER called.
"""

import json
import logging
import re

from app.core.exceptions import OllamaResponseError
from app.schemas.response import LearningSession

logger = logging.getLogger(__name__)

# Fields that must contain lists of strings (not dicts)
_STRING_LIST_FIELDS = {
    "learning_objectives",
    "practice_questions",
    "revision_checklist",
}


def parse_learning_session(raw_text: str) -> LearningSession:
    """
    Parse and validate raw model output into a LearningSession.

    Parameters
    ----------
    raw_text : The 'response' string from Ollama's generate output.

    Returns
    -------
    A fully validated LearningSession instance.

    Raises
    ------
    OllamaResponseError — if the text is not valid JSON, is not a dict,
                          or fails Pydantic validation after normalization.
    """
    cleaned = _strip_code_fences(raw_text.strip())

    # ── 1. JSON parse ─────────────────────────────────────────────────────────
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error(
            "JSON parse failed: %s\nFirst 300 chars of raw text: %.300s",
            exc, raw_text,
        )
        raise OllamaResponseError(
            "StudyPilot received an unexpected response from the AI model. "
            "Please try again."
        ) from exc

    # ── 2. Type guard ─────────────────────────────────────────────────────────
    if not isinstance(data, dict):
        logger.error(
            "Model output parsed to %s instead of dict. Raw: %.300s",
            type(data).__name__, raw_text,
        )
        raise OllamaResponseError(
            "StudyPilot received an unexpected response from the AI model. "
            "Please try again."
        )

    # ── 3. Normalise double-encoded nested fields ─────────────────────────────
    # Small models (1B) sometimes return nested arrays/objects as JSON strings.
    data = _normalize_model_output(data)

    # ── 4. Coerce string-list fields ──────────────────────────────────────────
    # Small models sometimes put dicts in fields that should contain strings.
    data = _coerce_string_list_fields(data)

    # ── 4.5. Filter inconsistent quiz items ──────────────────────────────────
    # If a model emits a quiz item where options[correct_index] != correct_answer
    # or options count != 4, drop that item rather than displaying a contradiction.
    data = _filter_inconsistent_quiz_items(data)

    # ── 5. Pydantic validation ────────────────────────────────────────────────
    try:
        return LearningSession.model_validate(data)
    except Exception as exc:
        logger.error(
            "Pydantic validation failed: %s\nData keys: %s",
            exc, list(data.keys()),
        )
        raise OllamaResponseError(
            "StudyPilot received an unexpected response from the AI model. "
            "Please try again."
        ) from exc


# ── Helpers ───────────────────────────────────────────────────────────────────

def _strip_code_fences(text: str) -> str:
    """
    Remove Markdown code-fence wrappers that a model may emit around JSON.

    Handles:
        ```json\\n{...}\\n```
        ```\\n{...}\\n```
        ```{...}```     (no newline after fence)
        {plain JSON without fences}

    Does NOT use eval(). Only string stripping and regex.
    """
    # Opening fence: ``` optionally followed by a language tag and optional newline
    text = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.IGNORECASE)
    # Closing fence: optional whitespace then ```
    text = re.sub(r'\s*```\s*$', '', text)
    return text.strip()


def _normalize_model_output(data: dict) -> dict:
    """
    Decode any top-level value that is a string but contains JSON.

    Small models (1B) may return a field like:
        "topic_breakdown": "[{\"heading\": \"...\"}]"
    instead of the proper:
        "topic_breakdown": [{"heading": "..."}]

    This function detects that pattern and decodes the string with json.loads.
    Only dict values are touched — keys are never modified.
    eval() is NEVER called.
    """
    normalized: dict = {}
    for key, value in data.items():
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith(('[', '{')):
                try:
                    decoded = json.loads(stripped)
                    normalized[key] = decoded
                    logger.debug(
                        "Normalised double-encoded field '%s': str → %s",
                        key, type(decoded).__name__,
                    )
                    continue
                except json.JSONDecodeError:
                    pass  # Not valid JSON — leave the value as-is
        normalized[key] = value
    return normalized


def _coerce_string_list_fields(data: dict) -> dict:
    """
    Ensure that fields which must contain list[str] actually do.

    Small models sometimes populate string-list fields with dicts or mixed
    types.  For example:
        "practice_questions": [{"question": "What is X?"}, ...]
        "revision_checklist": [{"heading": "Topic", "content": "..."}, ...]

    This function extracts a readable string from each item:
        - str   → kept as-is
        - dict  → join the values as a single string; fall back to the first value
        - other → convert with str()

    Fields processed: learning_objectives, practice_questions, revision_checklist
    """
    result = dict(data)
    for field in _STRING_LIST_FIELDS:
        if field not in result:
            continue
        raw_list = result[field]
        if not isinstance(raw_list, list):
            continue
        coerced: list[str] = []
        for item in raw_list:
            if isinstance(item, str):
                coerced.append(item)
            elif isinstance(item, dict):
                values = [str(v) for v in item.values() if v is not None]
                if values:
                    # Use "heading: content" format when there are two keys
                    if len(values) == 2:
                        coerced.append(f"{values[0]}: {values[1]}")
                    else:
                        coerced.append(". ".join(values))
                    logger.debug(
                        "Coerced dict → str in field '%s': %s", field, coerced[-1][:80]
                    )
            else:
                coerced.append(str(item))
        result[field] = coerced
    return result


def _filter_inconsistent_quiz_items(data: dict) -> dict:
    """
    Validate and filter quiz items for structural and deterministic consistency.

    If a quiz item has options[correct_index] != correct_answer or invalid options count,
    it is dropped rather than silently displaying a contradictory question.
    """
    if "quiz" not in data or not isinstance(data["quiz"], list):
        return data

    result = dict(data)
    valid_quiz: list[dict] = []
    prefix_pattern = r"^[A-Da-d][.:)\-\s]+"

    for item in data["quiz"]:
        if not isinstance(item, dict):
            continue

        # Check required fields
        if "question" not in item or "options" not in item or "correct_index" not in item:
            logger.warning("Dropping malformed quiz item missing required fields: %s", item)
            continue

        options = item.get("options")
        if not isinstance(options, list) or len(options) != 4:
            logger.warning("Dropping quiz item without exactly 4 options: %s", item)
            continue

        if any(not isinstance(opt, str) or not opt.strip() for opt in options):
            logger.warning("Dropping quiz item with blank option: %s", item)
            continue

        correct_index = item.get("correct_index")
        if not isinstance(correct_index, int) or correct_index < 0 or correct_index >= 4:
            logger.warning("Dropping quiz item with invalid correct_index: %s", item)
            continue

        # Deterministic consistency check if correct_answer is provided
        correct_answer = item.get("correct_answer")
        if correct_answer is not None and isinstance(correct_answer, str) and correct_answer.strip():
            norm_selected = re.sub(prefix_pattern, "", options[correct_index]).strip().lower()
            norm_correct = re.sub(prefix_pattern, "", correct_answer).strip().lower()

            matches = (
                norm_selected == norm_correct
                or options[correct_index].strip().lower() == correct_answer.strip().lower()
                or norm_selected in norm_correct
                or norm_correct in norm_selected
            )

            if not matches:
                logger.warning(
                    "Dropping contradictory quiz item: options[%d]=%r does not match correct_answer=%r (Question: %r)",
                    correct_index,
                    options[correct_index],
                    correct_answer,
                    item.get("question"),
                )
                continue

        valid_quiz.append(item)

    result["quiz"] = valid_quiz if valid_quiz else None
    return result
