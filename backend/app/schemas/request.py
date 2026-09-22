"""
Pydantic request schema for the /api/learn endpoint.

Design contract (from approved product design):
    Required  → topic, knowledge_level, learning_goal
    Optional  → available_time, explanation_style, difficulty, output_type

Optional fields must be sent as null (not omitted) if unused.
The backend never invents a value for an unset optional field.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ── Enums ─────────────────────────────────────────────────────────────────────
# Using str + Enum so values serialize to their string representation
# and FastAPI can display them correctly in the generated OpenAPI docs.

class KnowledgeLevel(str, Enum):
    beginner     = "beginner"
    intermediate = "intermediate"
    advanced     = "advanced"


class LearningGoal(str, Enum):
    concept_understanding  = "concept_understanding"
    exam_preparation       = "exam_preparation"
    interview_preparation  = "interview_preparation"
    assignment             = "assignment"
    practice               = "practice"


class AvailableTime(str, Enum):
    fifteen_minutes  = "15_minutes"
    thirty_minutes   = "30_minutes"
    one_hour         = "1_hour"
    two_plus_hours   = "2_plus_hours"


class ExplanationStyle(str, Enum):
    simple       = "simple"
    step_by_step = "step_by_step"
    example_based = "example_based"
    analogy_based = "analogy_based"
    detailed      = "detailed"


class Difficulty(str, Enum):
    easy   = "easy"
    medium = "medium"
    hard   = "hard"


class OutputType(str, Enum):
    explanation              = "explanation"
    study_notes              = "study_notes"
    practice_questions       = "practice_questions"
    quiz                     = "quiz"
    complete_learning_session = "complete_learning_session"


# ── Request model ─────────────────────────────────────────────────────────────

class LearnRequest(BaseModel):
    """
    The canonical request body for POST /api/learn.

    Required fields gate the endpoint — a request without topic,
    knowledge_level, or learning_goal is rejected with HTTP 422.

    Optional fields are explicitly Optional[Enum] = None.
    Pydantic will reject an invalid enum string with HTTP 422
    rather than silently coercing it to a valid value.
    """

    # ── Required ──────────────────────────────────────────────────────────────
    topic: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="The subject or question the student wants to learn.",
        examples=["Explain recursion in Java", "What is the water cycle?"],
    )
    knowledge_level: KnowledgeLevel = Field(
        ...,
        description="Student's current knowledge level on this topic.",
    )
    learning_goal: LearningGoal = Field(
        ...,
        description="Why the student is learning this topic.",
    )

    # ── Optional ──────────────────────────────────────────────────────────────
    available_time: Optional[AvailableTime] = Field(
        default=None,
        description="How long the student has available. Null → model decides depth.",
    )
    explanation_style: Optional[ExplanationStyle] = Field(
        default=None,
        description="Preferred explanation style. Null → model chooses.",
    )
    difficulty: Optional[Difficulty] = Field(
        default=None,
        description="Requested difficulty level. Null → inferred from knowledge_level.",
    )
    output_type: Optional[OutputType] = Field(
        default=None,
        description="Desired output format. Null → complete learning session.",
    )

    # ── Validation ────────────────────────────────────────────────────────────

    @field_validator("topic")
    @classmethod
    def topic_must_not_be_blank(cls, value: str) -> str:
        """Strip whitespace and reject empty or whitespace-only topics."""
        stripped = value.strip()
        if not stripped:
            raise ValueError(
                "Topic cannot be empty or contain only whitespace."
            )
        if len(stripped) < 3:
            raise ValueError(
                "Topic must be at least 3 characters after stripping whitespace."
            )
        return stripped

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "topic": "Explain recursion in Java",
                    "knowledge_level": "beginner",
                    "learning_goal": "exam_preparation",
                    "available_time": "30_minutes",
                    "explanation_style": "example_based",
                    "difficulty": None,
                    "output_type": None,
                }
            ]
        }
    }
