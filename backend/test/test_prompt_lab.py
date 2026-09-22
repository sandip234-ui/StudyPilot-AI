"""
Tests for the /api/prompt-lab endpoint and service.

Covers:
  - Valid experiment request returns 200 and all four strategies.
  - Required validation gates (missing/invalid topic, missing/invalid required context).
  - Optional fields serialized properly (null when omitted).
  - Prompt integrity: all four strategies produce distinct prompts for the same context.
  - Failure isolation: failure in one strategy does not break the whole experiment.
  - Response structure conformity with PromptLabResponse.
"""

from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import OllamaResponseError
from app.services.ollama import OllamaRawResponse, ollama_service
from main import app

client = TestClient(app)

_MINIMAL_PAYLOAD = {
    "topic": "Explain recursion in Java",
    "knowledge_level": "beginner",
    "learning_goal": "concept_understanding",
}

_FULL_PAYLOAD = {
    "topic": "Explain recursion in Java",
    "knowledge_level": "beginner",
    "learning_goal": "concept_understanding",
    "available_time": "30_minutes",
    "explanation_style": "step_by_step",
    "difficulty": "easy",
    "output_type": "explanation",
}


class TestPromptLabValidation:
    """Validation tests for POST /api/prompt-lab reusing LearnRequest validation."""

    def test_missing_topic_returns_422(self):
        payload = {
            "knowledge_level": "beginner",
            "learning_goal": "concept_understanding",
        }
        res = client.post("/api/prompt-lab", json=payload)
        assert res.status_code == 422

    def test_empty_topic_returns_422(self):
        payload = {
            "topic": "   ",
            "knowledge_level": "beginner",
            "learning_goal": "concept_understanding",
        }
        res = client.post("/api/prompt-lab", json=payload)
        assert res.status_code == 422

    def test_short_topic_returns_422(self):
        payload = {
            "topic": "ab",
            "knowledge_level": "beginner",
            "learning_goal": "concept_understanding",
        }
        res = client.post("/api/prompt-lab", json=payload)
        assert res.status_code == 422

    def test_missing_knowledge_level_returns_422(self):
        payload = {
            "topic": "Explain recursion in Java",
            "learning_goal": "concept_understanding",
        }
        res = client.post("/api/prompt-lab", json=payload)
        assert res.status_code == 422

    def test_invalid_knowledge_level_returns_422(self):
        payload = {
            "topic": "Explain recursion in Java",
            "knowledge_level": "expert",
            "learning_goal": "concept_understanding",
        }
        res = client.post("/api/prompt-lab", json=payload)
        assert res.status_code == 422

    def test_missing_learning_goal_returns_422(self):
        payload = {
            "topic": "Explain recursion in Java",
            "knowledge_level": "beginner",
        }
        res = client.post("/api/prompt-lab", json=payload)
        assert res.status_code == 422

    def test_invalid_learning_goal_returns_422(self):
        payload = {
            "topic": "Explain recursion in Java",
            "knowledge_level": "beginner",
            "learning_goal": "cramming",
        }
        res = client.post("/api/prompt-lab", json=payload)
        assert res.status_code == 422

    def test_invalid_optional_field_returns_422(self):
        payload = {
            **_MINIMAL_PAYLOAD,
            "difficulty": "insane",
        }
        res = client.post("/api/prompt-lab", json=payload)
        assert res.status_code == 422


class TestPromptLabExecution:
    """Execution and response structure tests for POST /api/prompt-lab."""

    def test_valid_request_returns_200(self):
        res = client.post("/api/prompt-lab", json=_FULL_PAYLOAD)
        assert res.status_code == 200
        data = res.json()
        assert "model_used" in data
        assert "request_context" in data
        assert "results" in data

    def test_executes_all_four_strategies(self):
        res = client.post("/api/prompt-lab", json=_FULL_PAYLOAD)
        assert res.status_code == 200
        results = res.json()["results"]
        assert len(results) == 4
        strategy_names = [r["strategy"] for r in results]
        assert strategy_names == ["baseline", "role", "personalized", "structured"]

    def test_prompt_integrity_all_four_prompts_are_distinct(self):
        res = client.post("/api/prompt-lab", json=_FULL_PAYLOAD)
        assert res.status_code == 200
        results = res.json()["results"]
        prompts = [r["prompt"] for r in results]
        # All 4 prompts must be unique
        assert len(set(prompts)) == 4
        # Prompts must not be empty
        for p in prompts:
            assert len(p) > 0

    def test_request_context_preserves_optional_nulls(self):
        res = client.post("/api/prompt-lab", json=_MINIMAL_PAYLOAD)
        assert res.status_code == 200
        ctx = res.json()["request_context"]
        assert ctx["knowledge_level"] == "beginner"
        assert ctx["learning_goal"] == "concept_understanding"
        assert ctx["available_time"] is None
        assert ctx["explanation_style"] is None
        assert ctx["difficulty"] is None
        assert ctx["output_type"] is None

    def test_each_result_contains_required_fields(self):
        res = client.post("/api/prompt-lab", json=_FULL_PAYLOAD)
        assert res.status_code == 200
        for item in res.json()["results"]:
            assert "strategy" in item
            assert "prompt" in item
            assert "techniques" in item
            assert isinstance(item["techniques"], list)
            assert len(item["techniques"]) > 0
            assert "purpose" in item
            assert isinstance(item["purpose"], str)
            assert "success" in item
            assert item["success"] is True
            assert item["error"] is None
            assert item["response"] is not None
            assert "title" in item["response"]
            assert "concept_explanation" in item["response"]


class TestPromptLabFailureIsolation:
    """Verify that failure in one strategy does not crash the entire experiment."""

    def test_single_strategy_failure_is_isolated(self):
        # We simulate a failure on the 3rd strategy ("personalized")
        call_count = 0

        original_generate = ollama_service.generate

        async def conditional_generate(prompt):
            nonlocal call_count
            call_count += 1
            if call_count == 3:
                raise OllamaResponseError("Simulated Ollama response failure on 3rd strategy")
            return await original_generate(prompt)

        with patch.object(ollama_service, "generate", side_effect=conditional_generate):
            res = client.post("/api/prompt-lab", json=_FULL_PAYLOAD)
            assert res.status_code == 200
            data = res.json()
            results = data["results"]
            assert len(results) == 4

            # Strategy 1 (baseline) succeeded
            assert results[0]["strategy"] == "baseline"
            assert results[0]["success"] is True
            assert results[0]["response"] is not None

            # Strategy 2 (role) succeeded
            assert results[1]["strategy"] == "role"
            assert results[1]["success"] is True
            assert results[1]["response"] is not None

            # Strategy 3 (personalized) failed in isolation
            assert results[2]["strategy"] == "personalized"
            assert results[2]["success"] is False
            assert results[2]["response"] is None
            assert "Simulated Ollama response failure" in results[2]["error"]

            # Strategy 4 (structured) still succeeded
            assert results[3]["strategy"] == "structured"
            assert results[3]["success"] is True
            assert results[3]["response"] is not None
