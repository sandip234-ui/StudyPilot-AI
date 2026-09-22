"""
Shared pytest configuration for the StudyPilot backend test suite.

Ollama mock strategy
--------------------
All tests EXCEPT those in test_ollama_integration.py run with
ollama_service.generate patched to an AsyncMock that returns a valid
OllamaRawResponse.

This ensures:
  1. No test requires a running Ollama server.
  2. All existing test_routes.py tests continue to pass unchanged.
  3. test_ollama_integration.py manages its own per-test mocks.

Mock response design
--------------------
The mock OllamaRawResponse uses:
  model       = "mock"        → satisfies test_response_model_used_is_mock
  eval_count  = None          → satisfies test_response_generation_meta_tokens_null
  eval_duration = None        → satisfies test_response_generation_meta_time_null
  text        = valid JSON    → parse_learning_session() succeeds
                                → LearningSession has all required fields
"""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.services.ollama import OllamaRawResponse, ollama_service


# ── Canonical mock session data ───────────────────────────────────────────────
# Must be a dict that passes LearningSession.model_validate() without error.
# Keep in sync with app/schemas/response.py.

MOCK_SESSION_DATA: dict = {
    "title": "Mock Learning Session",
    "learning_objectives": [
        "Understand the core concept and its purpose.",
        "Recognise key terms and how they relate.",
        "Apply the concept to a practical example.",
    ],
    "concept_explanation": (
        "[MOCK] This is a placeholder explanation. "
        "Real AI-generated content appears when Ollama is configured."
    ),
    "topic_breakdown": [
        {"heading": "Introduction", "content": "[MOCK] A brief introduction to the topic."},
        {"heading": "Core Concepts", "content": "[MOCK] The main ideas and principles."},
        {"heading": "Practical Application", "content": "[MOCK] How this concept is used."},
    ],
    "examples": [
        {
            "title": "[MOCK] Example 1",
            "code": None,
            "explanation": "[MOCK] A practical example will appear here.",
        },
    ],
    "analogy": "[MOCK] A real-world analogy that makes this concept intuitive.",
    "practice_questions": [
        "[MOCK] What is the main purpose of this concept?",
        "[MOCK] Can you describe this in your own words?",
        "[MOCK] When would you use this in a real project?",
    ],
    "quiz": [
        {
            "question": "[MOCK] What does this topic primarily address?",
            "options": [
                "Option A — correct answer placeholder",
                "Option B — distractor",
                "Option C — distractor",
                "Option D — distractor",
            ],
            "correct_index": 0,
            "explanation": "[MOCK] Option A is correct.",
        },
    ],
    "revision_checklist": [
        "I can define the concept in my own words.",
        "I can identify at least one practical use case.",
        "I can explain the concept to someone else.",
    ],
}

MOCK_OLLAMA_RESPONSE = OllamaRawResponse(
    text=json.dumps(MOCK_SESSION_DATA),
    model="mock",
    eval_count=None,
    eval_duration=None,
)


# ── Auto-use fixture ──────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _mock_ollama_for_non_integration_tests(request):
    """
    Patch ollama_service.generate for every test EXCEPT those in
    test_ollama_integration.py (which manage their own mocks explicitly).

    The fixture is transparent to tests that don't request it — the mock
    runs in the background and tests never need to declare it as a parameter.
    """
    test_file: str = str(request.fspath)

    if "test_ollama_integration" in test_file:
        # Integration tests control their own Ollama mock — don't interfere.
        yield
        return

    with patch.object(
        ollama_service,
        "generate",
        new_callable=AsyncMock,
    ) as mock_generate:
        mock_generate.return_value = MOCK_OLLAMA_RESPONSE
        yield mock_generate
