"""
Learning service.

Owns the production data flow:

    LearnRequest
        → build_learning_prompt(request, PromptStrategy.personalized)
        → augment prompt with JSON output instruction
        → ollama_service.generate(prompt)
        → parse_learning_session(raw_text)
        → LearnResponse

Key design decisions
--------------------
1.  Strategy is fixed to PromptStrategy.personalized for the main endpoint.
    The Prompt Engineering Lab (future phase) will expose all four strategies.

2.  The JSON output instruction is appended at this layer (not inside the
    prompt engine) because it is an integration concern, not a prompt strategy
    concern.  The prompt engine strategies remain pure and independently testable.

3.  Generation timing uses Ollama's eval_duration (nanoseconds) when reported.
    If Ollama does not report it (e.g. mock), generation_time_ms is None.

4.  This module does NOT handle HTTP retries or partial results — those are
    the responsibility of ollama.py.
"""

import logging
import uuid

from app.core.exceptions import OllamaResponseError
from app.prompts.engine import build_learning_prompt
from app.prompts.strategies import PromptStrategy
from app.schemas.request import LearnRequest
from app.schemas.response import ContextUsed, GenerationMeta, LearnResponse, LearningSession
from app.services.ollama import OllamaRawResponse, ollama_service
from app.services.response_parser import parse_learning_session

logger = logging.getLogger(__name__)


# ── JSON output instruction ───────────────────────────────────────────────────
# Appended to the prompt before sending to Ollama.
# Tells the model exactly what JSON structure to produce.
# Kept separate from the prompt engine so strategies remain format-agnostic.

_JSON_OUTPUT_INSTRUCTION = """

QUIZ GENERATION RULES:
1. Every quiz question must test a concrete technical fact explicitly explained in the generated learning content above.
2. Do NOT invent unrelated trivia, ambiguous questions, or ask about concepts not directly taught in this session.
3. Every quiz question must have exactly one objectively true and unambiguous correct answer.
4. Determine the correct answer first before writing the 3 plausible but clearly incorrect distractors.
5. "options" must contain exactly 4 options. Do NOT include option letter prefixes like "A." or "B." in the option text.
6. "correct_answer" must be the exact text of the correct option matching one of the items in "options".
7. "correct_index" must be the integer index (0, 1, 2, or 3) of that correct option in "options" such that options[correct_index] == correct_answer.
8. "explanation" must directly explain why that specific option is correct based on the lesson, without contradicting the answer.
9. Avoid ambiguous terminology, subjective questions, or vague comparisons (e.g. avoid asking which is "better" or "more secure" unless explicitly established in the lesson). Prefer simple, directly verifiable technical facts.
10. Before returning the final JSON, internally verify:
    - Is the selected answer actually the intended correct answer?
    - Does correct_index point to that answer?
    - Does the explanation support that answer?
    - Is exactly one option correct?
11. Do NOT expose internal reasoning; return ONLY the valid JSON object.

Respond with a single valid JSON object only.
Do not include any prose, markdown, or code fences before or after the JSON.
Use exactly this structure:

{
  "title": "string — title of the learning session",
  "learning_objectives": ["string", "..."],
  "concept_explanation": "string — clear conceptual explanation",
  "topic_breakdown": [
    {"heading": "string", "content": "string"}
  ],
  "examples": [
    {"title": "string", "code": null, "explanation": "string"}
  ],
  "analogy": "string — a real-world analogy",
  "practice_questions": ["string", "..."],
  "quiz": [
    {
      "question": "string — factual question directly testing a concept explained in this lesson",
      "options": [
        "Option 1",
        "Option 2",
        "Option 3",
        "Option 4"
      ],
      "correct_answer": "exact text matching one of the options above",
      "correct_index": 0,
      "explanation": "string — factual explanation confirming why correct_answer is correct"
    }
  ],
  "revision_checklist": ["string", "..."]
}"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_context_used(request: LearnRequest) -> ContextUsed:
    """Build the ContextUsed section from the incoming request."""
    return ContextUsed(
        knowledge_level=request.knowledge_level.value,
        learning_goal=request.learning_goal.value,
        available_time=request.available_time.value if request.available_time else None,
        explanation_style=request.explanation_style.value if request.explanation_style else None,
        difficulty=request.difficulty.value if request.difficulty else None,
        output_type=request.output_type.value if request.output_type else None,
    )


def _generation_time_ms(raw: OllamaRawResponse) -> int | None:
    """
    Convert Ollama's eval_duration (nanoseconds) to milliseconds.
    Returns None when Ollama did not report a duration (e.g. in mock mode).
    """
    if raw.eval_duration is None:
        return None
    return raw.eval_duration // 1_000_000


# ── Production entry point ────────────────────────────────────────────────────

async def generate_learning_session(request: LearnRequest) -> LearnResponse:
    """
    Generate a real AI-powered learning session using local Ollama.

    Parameters
    ----------
    request : Validated LearnRequest from the API layer.

    Returns
    -------
    A fully populated LearnResponse.

    Raises
    ------
    OllamaConfigError           — model not configured
    OllamaUnavailableError      — Ollama not running
    OllamaModelUnavailableError — model not installed
    OllamaTimeoutError          — generation timed out
    OllamaResponseError         — empty/invalid/unvalidatable model output
    """
    strategy = PromptStrategy.personalized

    # Build and augment the prompt
    prompt_result = build_learning_prompt(request, strategy)
    augmented_prompt = prompt_result.prompt + _JSON_OUTPUT_INSTRUCTION

    logger.info(
        "Generating session — topic=%r  strategy=%s  prompt_len=%d",
        request.topic, strategy.value, len(augmented_prompt),
    )

    # Call Ollama
    raw: OllamaRawResponse = await ollama_service.generate(augmented_prompt)

    # Parse and validate the model's JSON output
    learning_session: LearningSession = parse_learning_session(raw.text)

    logger.info(
        "Session generated — model=%s  tokens=%s  duration_ms=%s",
        raw.model, raw.eval_count, _generation_time_ms(raw),
    )

    return LearnResponse(
        session_id=str(uuid.uuid4()),
        topic=request.topic,
        model_used=raw.model,
        prompt_strategy=strategy.value,
        context_used=_build_context_used(request),
        learning_session=learning_session,
        generation_meta=GenerationMeta(
            tokens_used=raw.eval_count,
            generation_time_ms=_generation_time_ms(raw),
        ),
    )
