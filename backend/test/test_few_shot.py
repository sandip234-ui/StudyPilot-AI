"""
Tests for Few-Shot Prompting and the /api/few-shot-lab endpoint.

Covers:
  - Prompt Integrity (Zero-Shot vs Few-Shot differences, deterministic demonstrations, no topic leakage).
  - API Validation (422 gates for topic, knowledge_level, learning_goal).
  - API Execution (zero-shot and few-shot results returned, schema conformity).
  - Failure Isolation (failure in one run does not destroy the other).
  - Verification that existing PromptLab strategies and learning endpoints remain unaffected.
"""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import OllamaResponseError
from app.prompts.few_shot import (
    FEW_SHOT_DEMONSTRATION_EXAMPLE,
    build_few_shot_prompt,
    build_zero_shot_prompt,
)
from app.prompts.strategies import PromptStrategy
from app.schemas.request import KnowledgeLevel, LearnRequest, LearningGoal
from app.services.ollama import ollama_service
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


class TestFewShotPromptIntegrity:
    """Verify prompt construction properties for zero-shot vs few-shot."""

    @pytest.fixture
    def sample_request(self):
        return LearnRequest(
            topic="Explain recursion in Java",
            knowledge_level=KnowledgeLevel.beginner,
            learning_goal=LearningGoal.concept_understanding,
        )

    def test_zero_shot_contains_no_demonstration_examples(self, sample_request):
        result = build_zero_shot_prompt(sample_request)
        assert "DEMONSTRATION EXAMPLE" not in result.prompt
        assert "Variables in Java" not in result.prompt

    def test_few_shot_contains_demonstration_examples(self, sample_request):
        result = build_few_shot_prompt(sample_request)
        assert "DEMONSTRATION EXAMPLE" in result.prompt
        assert "Variables in Java" in result.prompt

    def test_demonstration_does_not_leak_target_topic(self, sample_request):
        # Target topic is recursion; demonstration must use an unrelated topic (Variables)
        assert "recursion" not in FEW_SHOT_DEMONSTRATION_EXAMPLE.lower()

    def test_both_prompts_contain_same_target_topic(self, sample_request):
        zero = build_zero_shot_prompt(sample_request)
        few = build_few_shot_prompt(sample_request)
        assert sample_request.topic in zero.prompt
        assert sample_request.topic in few.prompt

    def test_both_prompts_contain_same_student_context(self, sample_request):
        zero = build_zero_shot_prompt(sample_request)
        few = build_few_shot_prompt(sample_request)
        assert "Knowledge level: Beginner" in zero.prompt
        assert "Knowledge level: Beginner" in few.prompt
        assert "Learning goal: Concept Understanding" in zero.prompt
        assert "Learning goal: Concept Understanding" in few.prompt

    def test_demonstration_examples_are_deterministic(self, sample_request):
        res1 = build_few_shot_prompt(sample_request)
        res2 = build_few_shot_prompt(sample_request)
        assert res1.prompt == res2.prompt
        assert FEW_SHOT_DEMONSTRATION_EXAMPLE in res1.prompt

    def test_existing_strategies_are_unaffected(self):
        assert len(PromptStrategy) == 4
        assert [s.value for s in PromptStrategy] == [
            "baseline",
            "role",
            "personalized",
            "structured",
        ]


class TestFewShotLabValidation:
    """Validation tests for POST /api/few-shot-lab."""

    def test_missing_topic_returns_422(self):
        payload = {
            "knowledge_level": "beginner",
            "learning_goal": "concept_understanding",
        }
        res = client.post("/api/few-shot-lab", json=payload)
        assert res.status_code == 422

    def test_short_topic_returns_422(self):
        payload = {
            "topic": "ab",
            "knowledge_level": "beginner",
            "learning_goal": "concept_understanding",
        }
        res = client.post("/api/few-shot-lab", json=payload)
        assert res.status_code == 422

    def test_missing_knowledge_level_returns_422(self):
        payload = {
            "topic": "Explain recursion in Java",
            "learning_goal": "concept_understanding",
        }
        res = client.post("/api/few-shot-lab", json=payload)
        assert res.status_code == 422

    def test_missing_learning_goal_returns_422(self):
        payload = {
            "topic": "Explain recursion in Java",
            "knowledge_level": "beginner",
        }
        res = client.post("/api/few-shot-lab", json=payload)
        assert res.status_code == 422

    def test_invalid_optional_field_returns_422(self):
        payload = {
            **_MINIMAL_PAYLOAD,
            "available_time": "5_days",
        }
        res = client.post("/api/few-shot-lab", json=payload)
        assert res.status_code == 422


class TestFewShotLabExecution:
    """Execution and response structure tests for POST /api/few-shot-lab."""

    def test_valid_request_returns_200(self):
        res = client.post("/api/few-shot-lab", json=_FULL_PAYLOAD)
        assert res.status_code == 200
        data = res.json()
        assert "model_used" in data
        assert "request_context" in data
        assert "results" in data

    def test_returns_both_zero_shot_and_few_shot(self):
        res = client.post("/api/few-shot-lab", json=_FULL_PAYLOAD)
        assert res.status_code == 200
        results = res.json()["results"]
        assert len(results) == 2
        strategies = [r["strategy"] for r in results]
        assert strategies == ["zero_shot", "few_shot"]

    def test_few_shot_includes_demonstration_examples_metadata(self):
        res = client.post("/api/few-shot-lab", json=_FULL_PAYLOAD)
        assert res.status_code == 200
        results = res.json()["results"]
        zero_shot = results[0]
        few_shot = results[1]

        assert zero_shot["demonstration_examples"] is None
        assert few_shot["demonstration_examples"] is not None
        assert "Variables in Java" in few_shot["demonstration_examples"]

    def test_request_context_preserves_optional_nulls(self):
        res = client.post("/api/few-shot-lab", json=_MINIMAL_PAYLOAD)
        assert res.status_code == 200
        ctx = res.json()["request_context"]
        assert ctx["knowledge_level"] == "beginner"
        assert ctx["learning_goal"] == "concept_understanding"
        assert ctx["available_time"] is None
        assert ctx["explanation_style"] is None
        assert ctx["difficulty"] is None
        assert ctx["output_type"] is None

    def test_each_result_contains_conforming_response(self):
        res = client.post("/api/few-shot-lab", json=_FULL_PAYLOAD)
        assert res.status_code == 200
        for item in res.json()["results"]:
            assert item["success"] is True
            assert item["error"] is None
            assert item["response"] is not None
            assert "title" in item["response"]
            assert "concept_explanation" in item["response"]
            assert len(item["techniques"]) > 0


class TestFewShotLabFailureIsolation:
    """Verify that failure in one run does not fail the other."""

    def test_zero_shot_failure_does_not_crash_few_shot(self):
        call_count = 0
        original_generate = ollama_service.generate

        async def conditional_generate(prompt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # Fail the first call (zero_shot)
                raise OllamaResponseError("Simulated Ollama response failure on zero-shot")
            return await original_generate(prompt)

        with patch.object(ollama_service, "generate", side_effect=conditional_generate):
            res = client.post("/api/few-shot-lab", json=_FULL_PAYLOAD)
            assert res.status_code == 200
            results = res.json()["results"]
            assert len(results) == 2

            # Zero-shot failed gracefully
            assert results[0]["strategy"] == "zero_shot"
            assert results[0]["success"] is False
            assert results[0]["response"] is None
            assert "Simulated Ollama response failure" in results[0]["error"]

            # Few-shot succeeded
            assert results[1]["strategy"] == "few_shot"
            assert results[1]["success"] is True
            assert results[1]["response"] is not None
