"""
Backend foundation tests for StudyPilot.

These tests verify:
  - The health endpoint responds correctly.
  - The /api/learn endpoint accepts valid requests.
  - Pydantic validation rejects invalid input with HTTP 422.
  - Optional fields can be omitted or set to null.
  - The response structure matches the approved contract.

Tests do NOT require Ollama to be running.
All tests run against the mock learning service.
"""

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# ─── Helpers ──────────────────────────────────────────────────────────────────

VALID_PAYLOAD = {
    "topic": "Explain recursion in Java",
    "knowledge_level": "beginner",
    "learning_goal": "exam_preparation",
}

VALID_PAYLOAD_FULL = {
    "topic": "Explain recursion in Java",
    "knowledge_level": "beginner",
    "learning_goal": "exam_preparation",
    "available_time": "30_minutes",
    "explanation_style": "example_based",
    "difficulty": "medium",
    "output_type": "complete_learning_session",
}


# ─── Health endpoint ──────────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_200(self):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_body(self):
        response = client.get("/api/health")
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "studypilot-backend"

    def test_health_has_exactly_two_keys(self):
        """No extra fields should leak into the health response."""
        response = client.get("/api/health")
        data = response.json()
        assert set(data.keys()) == {"status", "service"}


# ─── Valid requests ───────────────────────────────────────────────────────────

class TestValidRequests:
    def test_minimal_valid_request_returns_200(self):
        """Only required fields — all optionals absent."""
        response = client.post("/api/learn", json=VALID_PAYLOAD)
        assert response.status_code == 200

    def test_full_valid_request_returns_200(self):
        """All fields provided."""
        response = client.post("/api/learn", json=VALID_PAYLOAD_FULL)
        assert response.status_code == 200

    def test_optional_fields_as_null_returns_200(self):
        """Optional fields explicitly set to null — must be accepted."""
        payload = {
            **VALID_PAYLOAD,
            "available_time": None,
            "explanation_style": None,
            "difficulty": None,
            "output_type": None,
        }
        response = client.post("/api/learn", json=payload)
        assert response.status_code == 200

    def test_topic_whitespace_is_stripped(self):
        """Leading/trailing whitespace on topic should be stripped, not rejected."""
        payload = {**VALID_PAYLOAD, "topic": "  Explain recursion in Java  "}
        response = client.post("/api/learn", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["topic"] == "Explain recursion in Java"

    def test_all_knowledge_levels_accepted(self):
        for level in ["beginner", "intermediate", "advanced"]:
            payload = {**VALID_PAYLOAD, "knowledge_level": level}
            response = client.post("/api/learn", json=payload)
            assert response.status_code == 200, f"Failed for knowledge_level={level!r}"

    def test_all_learning_goals_accepted(self):
        for goal in [
            "concept_understanding",
            "exam_preparation",
            "interview_preparation",
            "assignment",
            "practice",
        ]:
            payload = {**VALID_PAYLOAD, "learning_goal": goal}
            response = client.post("/api/learn", json=payload)
            assert response.status_code == 200, f"Failed for learning_goal={goal!r}"

    def test_all_optional_available_times_accepted(self):
        for time in ["15_minutes", "30_minutes", "1_hour", "2_plus_hours"]:
            payload = {**VALID_PAYLOAD, "available_time": time}
            response = client.post("/api/learn", json=payload)
            assert response.status_code == 200, f"Failed for available_time={time!r}"

    def test_all_optional_explanation_styles_accepted(self):
        for style in ["simple", "step_by_step", "example_based", "analogy_based", "detailed"]:
            payload = {**VALID_PAYLOAD, "explanation_style": style}
            response = client.post("/api/learn", json=payload)
            assert response.status_code == 200, f"Failed for explanation_style={style!r}"

    def test_all_optional_difficulties_accepted(self):
        for diff in ["easy", "medium", "hard"]:
            payload = {**VALID_PAYLOAD, "difficulty": diff}
            response = client.post("/api/learn", json=payload)
            assert response.status_code == 200, f"Failed for difficulty={diff!r}"

    def test_all_optional_output_types_accepted(self):
        for otype in [
            "explanation",
            "study_notes",
            "practice_questions",
            "quiz",
            "complete_learning_session",
        ]:
            payload = {**VALID_PAYLOAD, "output_type": otype}
            response = client.post("/api/learn", json=payload)
            assert response.status_code == 200, f"Failed for output_type={otype!r}"


# ─── Topic validation ─────────────────────────────────────────────────────────

class TestTopicValidation:
    def test_missing_topic_returns_422(self):
        payload = {"knowledge_level": "beginner", "learning_goal": "exam_preparation"}
        response = client.post("/api/learn", json=payload)
        assert response.status_code == 422

    def test_empty_topic_returns_422(self):
        response = client.post("/api/learn", json={**VALID_PAYLOAD, "topic": ""})
        assert response.status_code == 422

    def test_whitespace_only_topic_returns_422(self):
        response = client.post("/api/learn", json={**VALID_PAYLOAD, "topic": "   "})
        assert response.status_code == 422

    def test_topic_two_characters_returns_422(self):
        """Exactly 2 chars — below the minimum of 3."""
        response = client.post("/api/learn", json={**VALID_PAYLOAD, "topic": "ab"})
        assert response.status_code == 422

    def test_topic_three_characters_accepted(self):
        """Exactly 3 chars — the minimum."""
        response = client.post("/api/learn", json={**VALID_PAYLOAD, "topic": "abc"})
        assert response.status_code == 200

    def test_topic_500_characters_accepted(self):
        response = client.post("/api/learn", json={**VALID_PAYLOAD, "topic": "a" * 500})
        assert response.status_code == 200

    def test_topic_501_characters_returns_422(self):
        response = client.post("/api/learn", json={**VALID_PAYLOAD, "topic": "a" * 501})
        assert response.status_code == 422


# ─── Knowledge level validation ───────────────────────────────────────────────

class TestKnowledgeLevelValidation:
    def test_missing_knowledge_level_returns_422(self):
        payload = {"topic": "Explain recursion", "learning_goal": "exam_preparation"}
        response = client.post("/api/learn", json=payload)
        assert response.status_code == 422

    def test_invalid_knowledge_level_returns_422(self):
        payload = {**VALID_PAYLOAD, "knowledge_level": "expert"}
        response = client.post("/api/learn", json=payload)
        assert response.status_code == 422

    def test_knowledge_level_case_sensitive(self):
        """Enum values are lowercase — uppercase must be rejected."""
        payload = {**VALID_PAYLOAD, "knowledge_level": "Beginner"}
        response = client.post("/api/learn", json=payload)
        assert response.status_code == 422

    def test_empty_knowledge_level_returns_422(self):
        payload = {**VALID_PAYLOAD, "knowledge_level": ""}
        response = client.post("/api/learn", json=payload)
        assert response.status_code == 422


# ─── Learning goal validation ─────────────────────────────────────────────────

class TestLearningGoalValidation:
    def test_missing_learning_goal_returns_422(self):
        payload = {"topic": "Explain recursion", "knowledge_level": "beginner"}
        response = client.post("/api/learn", json=payload)
        assert response.status_code == 422

    def test_invalid_learning_goal_returns_422(self):
        payload = {**VALID_PAYLOAD, "learning_goal": "entertainment"}
        response = client.post("/api/learn", json=payload)
        assert response.status_code == 422

    def test_learning_goal_case_sensitive(self):
        payload = {**VALID_PAYLOAD, "learning_goal": "Exam_Preparation"}
        response = client.post("/api/learn", json=payload)
        assert response.status_code == 422

    def test_empty_learning_goal_returns_422(self):
        payload = {**VALID_PAYLOAD, "learning_goal": ""}
        response = client.post("/api/learn", json=payload)
        assert response.status_code == 422


# ─── Optional field validation ────────────────────────────────────────────────

class TestOptionalFieldValidation:
    def test_invalid_available_time_returns_422(self):
        payload = {**VALID_PAYLOAD, "available_time": "5_minutes"}
        response = client.post("/api/learn", json=payload)
        assert response.status_code == 422

    def test_invalid_explanation_style_returns_422(self):
        payload = {**VALID_PAYLOAD, "explanation_style": "visual"}
        response = client.post("/api/learn", json=payload)
        assert response.status_code == 422

    def test_invalid_difficulty_returns_422(self):
        payload = {**VALID_PAYLOAD, "difficulty": "extreme"}
        response = client.post("/api/learn", json=payload)
        assert response.status_code == 422

    def test_invalid_output_type_returns_422(self):
        payload = {**VALID_PAYLOAD, "output_type": "video"}
        response = client.post("/api/learn", json=payload)
        assert response.status_code == 422


# ─── Response structure ───────────────────────────────────────────────────────

class TestResponseStructure:
    def test_response_has_session_id(self):
        response = client.post("/api/learn", json=VALID_PAYLOAD)
        data = response.json()
        assert "session_id" in data
        assert isinstance(data["session_id"], str)
        assert len(data["session_id"]) > 0

    def test_response_echoes_topic(self):
        response = client.post("/api/learn", json=VALID_PAYLOAD)
        data = response.json()
        assert data["topic"] == VALID_PAYLOAD["topic"]

    def test_response_model_used_is_mock(self):
        response = client.post("/api/learn", json=VALID_PAYLOAD)
        data = response.json()
        assert data["model_used"] == "mock"

    def test_response_context_used_reflects_request(self):
        response = client.post("/api/learn", json=VALID_PAYLOAD_FULL)
        data = response.json()
        ctx = data["context_used"]
        assert ctx["knowledge_level"] == "beginner"
        assert ctx["learning_goal"] == "exam_preparation"
        assert ctx["available_time"] == "30_minutes"
        assert ctx["explanation_style"] == "example_based"
        assert ctx["difficulty"] == "medium"
        assert ctx["output_type"] == "complete_learning_session"

    def test_response_context_optional_fields_null_when_omitted(self):
        response = client.post("/api/learn", json=VALID_PAYLOAD)
        data = response.json()
        ctx = data["context_used"]
        assert ctx["available_time"] is None
        assert ctx["explanation_style"] is None
        assert ctx["difficulty"] is None
        assert ctx["output_type"] is None

    def test_response_generation_meta_tokens_null(self):
        response = client.post("/api/learn", json=VALID_PAYLOAD)
        data = response.json()
        assert data["generation_meta"]["tokens_used"] is None

    def test_response_generation_meta_time_null(self):
        response = client.post("/api/learn", json=VALID_PAYLOAD)
        data = response.json()
        assert data["generation_meta"]["generation_time_ms"] is None

    def test_learning_session_has_required_keys(self):
        response = client.post("/api/learn", json=VALID_PAYLOAD)
        session = response.json()["learning_session"]
        required_keys = {
            "title",
            "learning_objectives",
            "concept_explanation",
            "topic_breakdown",
            "revision_checklist",
        }
        for key in required_keys:
            assert key in session, f"Missing key: {key}"

    def test_unique_session_ids_per_request(self):
        """Each request should get a unique session_id."""
        r1 = client.post("/api/learn", json=VALID_PAYLOAD).json()
        r2 = client.post("/api/learn", json=VALID_PAYLOAD).json()
        assert r1["session_id"] != r2["session_id"]
