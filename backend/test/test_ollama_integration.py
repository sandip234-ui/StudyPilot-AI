"""
Ollama integration tests.

These tests verify the full /api/learn → OllamaService → ResponseParser →
LearnResponse stack, with the Ollama HTTP call mocked at the service boundary.

No running Ollama server is required.

Each test class or test function sets up its own AsyncMock of
ollama_service.generate (conftest.py deliberately does NOT auto-mock for
files named test_ollama_integration.py).

Coverage
--------
  TestSuccessfulGeneration   — valid response → HTTP 200 + full LearnResponse
  TestMarkdownJSONParsing    — code-fenced JSON → parsed correctly
  TestInvalidJSON            — malformed JSON → HTTP 502
  TestMissingRequiredFields  — JSON missing required keys → HTTP 502
  TestEmptyModelResponse     — empty Ollama response → HTTP 502
  TestOllamaConnectionFailure— ConnectError → HTTP 503
  TestOllamaTimeout          — TimeoutException → HTTP 504
  TestModelUnavailable       — 404 / error body → HTTP 503
  TestModelNotConfigured     — OllamaConfigError → HTTP 503
  TestResponseMetadata       — model_used, prompt_strategy, tokens, timing
  TestPromptStrategyVerification — prompt passed to Ollama uses personalized strategy
  TestResponseParser         — _strip_code_fences() and parse_learning_session() in isolation
"""

import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import (
    OllamaConfigError,
    OllamaModelUnavailableError,
    OllamaResponseError,
    OllamaTimeoutError,
    OllamaUnavailableError,
)
from app.services.ollama import OllamaRawResponse, ollama_service
from app.services.response_parser import _strip_code_fences, parse_learning_session
from main import app

client = TestClient(app)


# ── Shared fixtures and constants ─────────────────────────────────────────────

VALID_PAYLOAD = {
    "topic": "Explain recursion in Java",
    "knowledge_level": "beginner",
    "learning_goal": "exam_preparation",
    "available_time": "30_minutes",
    "explanation_style": "example_based",
    "difficulty": "medium",
    "output_type": "complete_learning_session",
}

VALID_SESSION_DATA = {
    "title": "Recursion in Java",
    "learning_objectives": [
        "Define recursion and explain how it works.",
        "Identify the base case and recursive case.",
        "Trace a recursive call stack.",
    ],
    "concept_explanation": (
        "Recursion is when a method calls itself to solve a smaller version "
        "of the same problem."
    ),
    "topic_breakdown": [
        {"heading": "What is Recursion?", "content": "A method that calls itself."},
        {"heading": "Base Case", "content": "The condition that stops the recursion."},
        {"heading": "Recursive Case", "content": "The part that calls itself."},
    ],
    "examples": [
        {
            "title": "Factorial",
            "code": "int factorial(int n) { return n == 0 ? 1 : n * factorial(n-1); }",
            "explanation": "Calls itself with n-1 until n reaches 0.",
        },
    ],
    "analogy": "Recursion is like looking at yourself between two mirrors.",
    "practice_questions": [
        "What is the base case of a recursive function?",
        "What happens if there is no base case?",
    ],
    "quiz": [
        {
            "question": "What prevents infinite recursion?",
            "options": ["A loop", "A base case", "A try-catch block", "A return type"],
            "correct_index": 1,
            "explanation": "The base case stops the recursive calls.",
        },
    ],
    "revision_checklist": [
        "I can define recursion.",
        "I can write a simple recursive function.",
        "I can identify the base case.",
    ],
}

VALID_OLLAMA_RESPONSE = OllamaRawResponse(
    text=json.dumps(VALID_SESSION_DATA),
    model="llama3.2:1b",
    eval_count=220,
    eval_duration=8_500_000_000,  # 8.5 seconds in nanoseconds
)


@pytest.fixture()
def mock_ollama():
    """Per-test AsyncMock for ollama_service.generate."""
    with patch.object(ollama_service, "generate", new_callable=AsyncMock) as m:
        yield m


# ── TestSuccessfulGeneration ──────────────────────────────────────────────────

class TestSuccessfulGeneration:
    def test_returns_http_200(self, mock_ollama):
        mock_ollama.return_value = VALID_OLLAMA_RESPONSE
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 200

    def test_response_is_valid_json(self, mock_ollama):
        mock_ollama.return_value = VALID_OLLAMA_RESPONSE
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        data = resp.json()  # raises if invalid
        assert isinstance(data, dict)

    def test_learning_session_title_present(self, mock_ollama):
        mock_ollama.return_value = VALID_OLLAMA_RESPONSE
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        session = resp.json()["learning_session"]
        assert session["title"] == "Recursion in Java"

    def test_learning_session_objectives_present(self, mock_ollama):
        mock_ollama.return_value = VALID_OLLAMA_RESPONSE
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        session = resp.json()["learning_session"]
        assert len(session["learning_objectives"]) == 3

    def test_learning_session_required_sections_present(self, mock_ollama):
        mock_ollama.return_value = VALID_OLLAMA_RESPONSE
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        session = resp.json()["learning_session"]
        for key in [
            "title", "learning_objectives", "concept_explanation",
            "topic_breakdown", "revision_checklist",
        ]:
            assert key in session, f"Required key missing: {key}"

    def test_context_used_reflects_request(self, mock_ollama):
        mock_ollama.return_value = VALID_OLLAMA_RESPONSE
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        ctx = resp.json()["context_used"]
        assert ctx["knowledge_level"] == "beginner"
        assert ctx["learning_goal"] == "exam_preparation"
        assert ctx["available_time"] == "30_minutes"
        assert ctx["explanation_style"] == "example_based"
        assert ctx["difficulty"] == "medium"
        assert ctx["output_type"] == "complete_learning_session"

    def test_topic_echoed_in_response(self, mock_ollama):
        mock_ollama.return_value = VALID_OLLAMA_RESPONSE
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.json()["topic"] == VALID_PAYLOAD["topic"]

    def test_session_id_is_non_empty_string(self, mock_ollama):
        mock_ollama.return_value = VALID_OLLAMA_RESPONSE
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        sid = resp.json()["session_id"]
        assert isinstance(sid, str) and len(sid) > 0

    def test_session_ids_are_unique(self, mock_ollama):
        mock_ollama.return_value = VALID_OLLAMA_RESPONSE
        ids = {client.post("/api/learn", json=VALID_PAYLOAD).json()["session_id"] for _ in range(3)}
        assert len(ids) == 3

    def test_ollama_was_called_once(self, mock_ollama):
        mock_ollama.return_value = VALID_OLLAMA_RESPONSE
        client.post("/api/learn", json=VALID_PAYLOAD)
        mock_ollama.assert_called_once()


# ── TestMarkdownJSONParsing ───────────────────────────────────────────────────

class TestMarkdownJSONParsing:
    """Verify that markdown-wrapped JSON from the model is handled correctly."""

    def _ollama_with_text(self, text: str) -> OllamaRawResponse:
        return OllamaRawResponse(
            text=text,
            model="llama3.2:1b",
            eval_count=None,
            eval_duration=None,
        )

    def test_json_code_fence_with_language_tag(self, mock_ollama):
        fenced = f"```json\n{json.dumps(VALID_SESSION_DATA)}\n```"
        mock_ollama.return_value = self._ollama_with_text(fenced)
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 200

    def test_json_code_fence_without_language_tag(self, mock_ollama):
        fenced = f"```\n{json.dumps(VALID_SESSION_DATA)}\n```"
        mock_ollama.return_value = self._ollama_with_text(fenced)
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 200

    def test_plain_json_without_fences(self, mock_ollama):
        mock_ollama.return_value = self._ollama_with_text(json.dumps(VALID_SESSION_DATA))
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 200

    def test_json_with_surrounding_whitespace(self, mock_ollama):
        padded = f"\n\n  {json.dumps(VALID_SESSION_DATA)}  \n\n"
        mock_ollama.return_value = self._ollama_with_text(padded)
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 200

    def test_parsed_session_is_correct_after_fence_strip(self, mock_ollama):
        fenced = f"```json\n{json.dumps(VALID_SESSION_DATA)}\n```"
        mock_ollama.return_value = self._ollama_with_text(fenced)
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.json()["learning_session"]["title"] == VALID_SESSION_DATA["title"]


# ── TestInvalidJSON ───────────────────────────────────────────────────────────

class TestInvalidJSON:
    def test_non_json_text_returns_502(self, mock_ollama):
        mock_ollama.return_value = OllamaRawResponse(
            text="This is plain prose, not JSON at all.",
            model="llama3.2:1b",
            eval_count=None,
            eval_duration=None,
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 502

    def test_truncated_json_returns_502(self, mock_ollama):
        mock_ollama.return_value = OllamaRawResponse(
            text='{"title": "Recursion", "learning_objectives": [',  # truncated
            model="llama3.2:1b",
            eval_count=None,
            eval_duration=None,
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 502

    def test_json_array_not_object_returns_502(self, mock_ollama):
        mock_ollama.return_value = OllamaRawResponse(
            text=json.dumps(["item1", "item2"]),
            model="llama3.2:1b",
            eval_count=None,
            eval_duration=None,
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 502

    def test_502_detail_is_safe_user_message(self, mock_ollama):
        """Detail must not expose stack traces or internal error details."""
        mock_ollama.return_value = OllamaRawResponse(
            text="not json",
            model="llama3.2:1b",
            eval_count=None,
            eval_duration=None,
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        detail = resp.json()["detail"]
        assert "Traceback" not in detail
        assert "JSONDecodeError" not in detail
        assert "StudyPilot" in detail  # safe user-facing message


# ── TestMissingRequiredFields ─────────────────────────────────────────────────

class TestMissingRequiredFields:
    def _build_session_without(self, *remove_keys) -> str:
        data = {k: v for k, v in VALID_SESSION_DATA.items() if k not in remove_keys}
        return json.dumps(data)

    def test_missing_title_returns_502(self, mock_ollama):
        mock_ollama.return_value = OllamaRawResponse(
            text=self._build_session_without("title"),
            model="llama3.2:1b",
            eval_count=None,
            eval_duration=None,
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 502

    def test_missing_learning_objectives_returns_502(self, mock_ollama):
        mock_ollama.return_value = OllamaRawResponse(
            text=self._build_session_without("learning_objectives"),
            model="llama3.2:1b",
            eval_count=None,
            eval_duration=None,
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 502

    def test_missing_concept_explanation_returns_502(self, mock_ollama):
        mock_ollama.return_value = OllamaRawResponse(
            text=self._build_session_without("concept_explanation"),
            model="llama3.2:1b",
            eval_count=None,
            eval_duration=None,
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 502

    def test_missing_revision_checklist_returns_502(self, mock_ollama):
        mock_ollama.return_value = OllamaRawResponse(
            text=self._build_session_without("revision_checklist"),
            model="llama3.2:1b",
            eval_count=None,
            eval_duration=None,
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 502

    def test_optional_fields_absent_is_ok(self, mock_ollama):
        """quiz, practice_questions, examples, analogy are optional."""
        data = {k: v for k, v in VALID_SESSION_DATA.items()
                if k not in ("quiz", "practice_questions", "examples", "analogy")}
        mock_ollama.return_value = OllamaRawResponse(
            text=json.dumps(data),
            model="llama3.2:1b",
            eval_count=None,
            eval_duration=None,
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 200


# ── TestEmptyModelResponse ────────────────────────────────────────────────────

class TestEmptyModelResponse:
    def test_empty_response_from_ollama_returns_502(self, mock_ollama):
        mock_ollama.side_effect = OllamaResponseError(
            "StudyPilot received an empty response from the AI model. Please try again."
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 502

    def test_502_detail_present(self, mock_ollama):
        mock_ollama.side_effect = OllamaResponseError("Empty response.")
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.json()["detail"]


# ── TestOllamaConnectionFailure ───────────────────────────────────────────────

class TestOllamaConnectionFailure:
    def test_connect_error_returns_503(self, mock_ollama):
        mock_ollama.side_effect = OllamaUnavailableError(
            "StudyPilot could not connect to Ollama. Make sure Ollama is running."
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 503

    def test_503_detail_is_user_friendly(self, mock_ollama):
        mock_ollama.side_effect = OllamaUnavailableError(
            "StudyPilot could not connect to Ollama. Make sure Ollama is running."
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        detail = resp.json()["detail"]
        assert "Ollama" in detail
        assert "Traceback" not in detail

    def test_health_endpoint_still_works_when_ollama_down(self, mock_ollama):
        """Health check does not call Ollama."""
        mock_ollama.side_effect = OllamaUnavailableError("Ollama down")
        resp = client.get("/api/health")
        assert resp.status_code == 200


# ── TestOllamaTimeout ─────────────────────────────────────────────────────────

class TestOllamaTimeout:
    def test_timeout_returns_504(self, mock_ollama):
        mock_ollama.side_effect = OllamaTimeoutError(
            "The AI model took too long to respond. Please try again."
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 504

    def test_504_detail_is_user_friendly(self, mock_ollama):
        mock_ollama.side_effect = OllamaTimeoutError(
            "The AI model took too long to respond. Please try again."
        )
        detail = client.post("/api/learn", json=VALID_PAYLOAD).json()["detail"]
        assert "too long" in detail or "timed out" in detail.lower() or "took" in detail


# ── TestModelUnavailable ──────────────────────────────────────────────────────

class TestModelUnavailable:
    def test_model_not_found_returns_503(self, mock_ollama):
        mock_ollama.side_effect = OllamaModelUnavailableError(
            "The configured AI model 'bad-model' is not available in Ollama."
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 503

    def test_503_detail_mentions_model(self, mock_ollama):
        mock_ollama.side_effect = OllamaModelUnavailableError(
            "The configured AI model 'bad-model' is not available in Ollama."
        )
        detail = client.post("/api/learn", json=VALID_PAYLOAD).json()["detail"]
        assert "model" in detail.lower()


# ── TestModelNotConfigured ────────────────────────────────────────────────────

class TestModelNotConfigured:
    def test_config_error_returns_503(self, mock_ollama):
        mock_ollama.side_effect = OllamaConfigError(
            "The AI model is not configured. Set OLLAMA_MODEL in .env."
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.status_code == 503

    def test_503_detail_mentions_ollama_model(self, mock_ollama):
        mock_ollama.side_effect = OllamaConfigError(
            "The AI model is not configured. Set OLLAMA_MODEL in .env."
        )
        detail = client.post("/api/learn", json=VALID_PAYLOAD).json()["detail"]
        assert "OLLAMA_MODEL" in detail or "model" in detail.lower()


# ── TestResponseMetadata ──────────────────────────────────────────────────────

class TestResponseMetadata:
    def test_model_used_comes_from_ollama_response(self, mock_ollama):
        """model_used must reflect what Ollama reports, not a hard-coded value."""
        mock_ollama.return_value = OllamaRawResponse(
            text=json.dumps(VALID_SESSION_DATA),
            model="llama3.2:1b",
            eval_count=None,
            eval_duration=None,
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.json()["model_used"] == "llama3.2:1b"

    def test_model_used_different_model_name(self, mock_ollama):
        mock_ollama.return_value = OllamaRawResponse(
            text=json.dumps(VALID_SESSION_DATA),
            model="gemma3:1b",
            eval_count=None,
            eval_duration=None,
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.json()["model_used"] == "gemma3:1b"

    def test_prompt_strategy_is_personalized(self, mock_ollama):
        mock_ollama.return_value = VALID_OLLAMA_RESPONSE
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.json()["prompt_strategy"] == "personalized"

    def test_tokens_used_populated_when_reported(self, mock_ollama):
        mock_ollama.return_value = OllamaRawResponse(
            text=json.dumps(VALID_SESSION_DATA),
            model="llama3.2:1b",
            eval_count=220,
            eval_duration=None,
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.json()["generation_meta"]["tokens_used"] == 220

    def test_tokens_used_is_none_when_not_reported(self, mock_ollama):
        mock_ollama.return_value = OllamaRawResponse(
            text=json.dumps(VALID_SESSION_DATA),
            model="llama3.2:1b",
            eval_count=None,
            eval_duration=None,
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.json()["generation_meta"]["tokens_used"] is None

    def test_generation_time_ms_from_eval_duration(self, mock_ollama):
        """8_500_000_000 ns → 8500 ms."""
        mock_ollama.return_value = OllamaRawResponse(
            text=json.dumps(VALID_SESSION_DATA),
            model="llama3.2:1b",
            eval_count=220,
            eval_duration=8_500_000_000,
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.json()["generation_meta"]["generation_time_ms"] == 8500

    def test_generation_time_ms_is_none_when_not_reported(self, mock_ollama):
        mock_ollama.return_value = OllamaRawResponse(
            text=json.dumps(VALID_SESSION_DATA),
            model="llama3.2:1b",
            eval_count=None,
            eval_duration=None,
        )
        resp = client.post("/api/learn", json=VALID_PAYLOAD)
        assert resp.json()["generation_meta"]["generation_time_ms"] is None


# ── TestPromptStrategyVerification ────────────────────────────────────────────

class TestPromptStrategyVerification:
    """
    Verify that the prompt passed to Ollama is built by the personalized strategy.
    """

    def _get_prompt_sent_to_ollama(self, mock_ollama) -> str:
        mock_ollama.return_value = VALID_OLLAMA_RESPONSE
        client.post("/api/learn", json=VALID_PAYLOAD)
        mock_ollama.assert_called_once()
        # generate(prompt) — first positional arg
        return mock_ollama.call_args[0][0]

    def test_prompt_contains_topic(self, mock_ollama):
        prompt = self._get_prompt_sent_to_ollama(mock_ollama)
        assert VALID_PAYLOAD["topic"] in prompt

    def test_prompt_contains_personalized_role(self, mock_ollama):
        prompt = self._get_prompt_sent_to_ollama(mock_ollama)
        assert "AI tutor" in prompt

    def test_prompt_contains_knowledge_level(self, mock_ollama):
        prompt = self._get_prompt_sent_to_ollama(mock_ollama)
        assert "Knowledge level" in prompt

    def test_prompt_contains_learning_goal(self, mock_ollama):
        prompt = self._get_prompt_sent_to_ollama(mock_ollama)
        assert "Learning goal" in prompt

    def test_prompt_contains_json_instruction(self, mock_ollama):
        """The integration layer must append the JSON output instruction."""
        prompt = self._get_prompt_sent_to_ollama(mock_ollama)
        assert "JSON" in prompt

    def test_prompt_does_not_contain_structured_headers(self, mock_ollama):
        """The main endpoint uses personalized, not structured."""
        prompt = self._get_prompt_sent_to_ollama(mock_ollama)
        assert "STUDENT CONTEXT" not in prompt
        assert "INSTRUCTIONS\n------------" not in prompt

    def test_prompt_contains_available_time_when_provided(self, mock_ollama):
        prompt = self._get_prompt_sent_to_ollama(mock_ollama)
        assert "30 minutes" in prompt  # from available_time=30_minutes


# ── TestResponseParser (unit tests, no HTTP) ──────────────────────────────────

class TestResponseParser:
    """Unit tests for the parser module — no HTTP, no Ollama."""

    # _strip_code_fences
    def test_strip_json_fence_with_language(self):
        raw = f"```json\n{json.dumps(VALID_SESSION_DATA)}\n```"
        result = _strip_code_fences(raw)
        assert result == json.dumps(VALID_SESSION_DATA)

    def test_strip_fence_without_language(self):
        raw = f"```\n{json.dumps(VALID_SESSION_DATA)}\n```"
        result = _strip_code_fences(raw)
        assert result == json.dumps(VALID_SESSION_DATA)

    def test_plain_json_unchanged(self):
        raw = json.dumps(VALID_SESSION_DATA)
        result = _strip_code_fences(raw)
        assert result == raw

    def test_whitespace_stripped(self):
        raw = f"  \n  {json.dumps(VALID_SESSION_DATA)}  \n  "
        result = _strip_code_fences(raw.strip())
        assert result == json.dumps(VALID_SESSION_DATA)

    # parse_learning_session
    def test_valid_json_returns_learning_session(self):
        from app.schemas.response import LearningSession
        result = parse_learning_session(json.dumps(VALID_SESSION_DATA))
        assert isinstance(result, LearningSession)

    def test_valid_json_title_matches(self):
        result = parse_learning_session(json.dumps(VALID_SESSION_DATA))
        assert result.title == VALID_SESSION_DATA["title"]

    def test_invalid_json_raises_ollama_response_error(self):
        from app.core.exceptions import OllamaResponseError
        with pytest.raises(OllamaResponseError):
            parse_learning_session("not json at all")

    def test_json_array_raises_ollama_response_error(self):
        from app.core.exceptions import OllamaResponseError
        with pytest.raises(OllamaResponseError):
            parse_learning_session(json.dumps(["item1", "item2"]))

    def test_missing_required_field_raises_ollama_response_error(self):
        from app.core.exceptions import OllamaResponseError
        bad = {k: v for k, v in VALID_SESSION_DATA.items() if k != "title"}
        with pytest.raises(OllamaResponseError):
            parse_learning_session(json.dumps(bad))

    def test_optional_fields_absent_does_not_raise(self):
        data = {k: v for k, v in VALID_SESSION_DATA.items()
                if k not in ("analogy", "practice_questions", "quiz")}
        result = parse_learning_session(json.dumps(data))
        assert result.analogy is None
        assert result.practice_questions is None
        assert result.quiz is None

    def test_code_fenced_json_is_parsed_correctly(self):
        fenced = f"```json\n{json.dumps(VALID_SESSION_DATA)}\n```"
        result = parse_learning_session(fenced)
        assert result.title == VALID_SESSION_DATA["title"]

    def test_error_message_is_user_safe(self):
        """OllamaResponseError message must not leak internal exception details."""
        from app.core.exceptions import OllamaResponseError
        try:
            parse_learning_session("not json")
        except OllamaResponseError as exc:
            assert "Traceback" not in str(exc)
            assert "JSONDecodeError" not in str(exc)
            assert "StudyPilot" in str(exc)
