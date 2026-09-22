"""
Unit and integration tests for Phase 9: Evaluation Framework.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.routes import router
from app.schemas.evaluation import (
    RUBRIC_DEFINITIONS,
    CriterionScore,
    CriterionType,
    EvaluationRequest,
    EvaluationResult,
)
from app.services.evaluation import calculate_evaluation
from main import app

client = TestClient(app)

ALL_CRITERIA = [c.value for c in CriterionType]


class TestRubricDefinitions:
    def test_rubric_contains_all_eight_criteria(self):
        assert len(RUBRIC_DEFINITIONS) == 8
        for criterion in ALL_CRITERIA:
            assert criterion in RUBRIC_DEFINITIONS
            def_obj = RUBRIC_DEFINITIONS[criterion]
            assert "title" in def_obj
            assert "description" in def_obj
            assert "rubric" in def_obj
            # Every rubric scale must have 1, 2, 3, 4, 5
            for score in [1, 2, 3, 4, 5]:
                assert score in def_obj["rubric"]
                assert isinstance(def_obj["rubric"][score], str)
                assert len(def_obj["rubric"][score]) > 5

    def test_only_time_alignment_supports_na(self):
        assert RUBRIC_DEFINITIONS[CriterionType.TIME_ALIGNMENT.value]["supports_na"] is True
        for crit in ALL_CRITERIA:
            if crit != CriterionType.TIME_ALIGNMENT.value:
                assert RUBRIC_DEFINITIONS[crit]["supports_na"] is False


class TestCriterionScoreValidation:
    def test_valid_score_1_to_5(self):
        for val in [1, 2, 3, 4, 5]:
            score = CriterionScore(criterion="relevance", score=val, justification="Test")
            assert score.score == val
            assert score.max_score == 5
            assert score.is_na is False

    def test_score_below_1_raises_validation_error(self):
        with pytest.raises(ValidationError):
            CriterionScore(criterion="relevance", score=0, justification="Test")

    def test_score_above_5_raises_validation_error(self):
        with pytest.raises(ValidationError):
            CriterionScore(criterion="relevance", score=6, justification="Test")

    def test_missing_score_when_not_na_raises_validation_error(self):
        with pytest.raises(ValidationError):
            CriterionScore(criterion="relevance", score=None, is_na=False, justification="Test")

    def test_na_criterion_sets_max_score_to_zero_and_score_none(self):
        score = CriterionScore(
            criterion="time_alignment",
            score=4,  # Even if passed, validator overrides to None
            is_na=True,
            justification="Learner specified no available time",
        )
        assert score.is_na is True
        assert score.score is None
        assert score.max_score == 0


class TestEvaluationScoringCalculation:
    def test_all_eight_criteria_scored_perfect(self):
        scores = [
            CriterionScore(criterion=c, score=5, justification="Excellent")
            for c in ALL_CRITERIA
        ]
        req = EvaluationRequest(topic="Recursion", scores=scores)
        result = calculate_evaluation(req)

        assert result.total_score == 40
        assert result.max_score == 40
        assert result.percentage == 100.0
        assert len(result.scores) == 8

    def test_all_eight_criteria_scored_minimum(self):
        scores = [
            CriterionScore(criterion=c, score=1, justification="Poor")
            for c in ALL_CRITERIA
        ]
        req = EvaluationRequest(topic="Recursion", scores=scores)
        result = calculate_evaluation(req)

        assert result.total_score == 8
        assert result.max_score == 40
        assert result.percentage == 20.0

    def test_time_alignment_na_excluded_from_denominator(self):
        scores = []
        for c in ALL_CRITERIA:
            if c == CriterionType.TIME_ALIGNMENT.value:
                scores.append(CriterionScore(criterion=c, is_na=True, justification="No time provided"))
            else:
                scores.append(CriterionScore(criterion=c, score=4, justification="Good"))

        req = EvaluationRequest(topic="Recursion", scores=scores)
        result = calculate_evaluation(req)

        # 7 applicable criteria * 4 = 28
        # 7 applicable max * 5 = 35
        # 28 / 35 * 100 = 80.0%
        assert result.total_score == 28
        assert result.max_score == 35
        assert result.percentage == 80.0

    def test_justifications_preserved(self):
        scores = [
            CriterionScore(criterion="relevance", score=4, justification="Directly explains Java recursion."),
            CriterionScore(criterion="clarity", score=5, justification="Crystal clear analogies."),
        ]
        req = EvaluationRequest(topic="Recursion in Java", scores=scores)
        result = calculate_evaluation(req)

        assert result.scores[0].justification == "Directly explains Java recursion."
        assert result.scores[1].justification == "Crystal clear analogies."


class TestEvaluationAPIEndpoint:
    def test_evaluate_endpoint_returns_200_with_valid_payload(self):
        payload = {
            "topic": "Explain recursion in Java",
            "strategy": "personalized",
            "model_used": "llama3.2:3b",
            "scores": [
                {
                    "criterion": "relevance",
                    "score": 4,
                    "is_na": False,
                    "justification": "Directly explains Java recursion.",
                },
                {
                    "criterion": "personalization",
                    "score": 4,
                    "is_na": False,
                    "justification": "Respects beginner knowledge level.",
                },
                {
                    "criterion": "instruction_adherence",
                    "score": 5,
                    "is_na": False,
                    "justification": "Adheres to all instructions.",
                },
                {
                    "criterion": "clarity",
                    "score": 4,
                    "is_na": False,
                    "justification": "Very understandable.",
                },
                {
                    "criterion": "completeness",
                    "score": 4,
                    "is_na": False,
                    "justification": "Has all essential components.",
                },
                {
                    "criterion": "difficulty_alignment",
                    "score": 4,
                    "is_na": False,
                    "justification": "Matches beginner level.",
                },
                {
                    "criterion": "time_alignment",
                    "score": None,
                    "is_na": True,
                    "justification": "No time limit provided.",
                },
                {
                    "criterion": "structure_schema_quality",
                    "score": 5,
                    "is_na": False,
                    "justification": "Valid schema format.",
                },
            ],
        }

        response = client.post("/api/evaluate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["total_score"] == 30
        assert data["max_score"] == 35
        # 30 / 35 * 100 = 85.7%
        assert data["percentage"] == 85.7
        assert len(data["scores"]) == 8

    def test_evaluate_endpoint_rejects_out_of_bound_score(self):
        payload = {
            "topic": "Recursion",
            "scores": [
                {
                    "criterion": "relevance",
                    "score": 10,  # Invalid
                    "is_na": False,
                    "justification": "Invalid score",
                }
            ],
        }
        response = client.post("/api/evaluate", json=payload)
        assert response.status_code == 422

    def test_evaluate_endpoint_rejects_empty_scores(self):
        payload = {
            "topic": "Recursion",
            "scores": [],
        }
        response = client.post("/api/evaluate", json=payload)
        assert response.status_code == 422
