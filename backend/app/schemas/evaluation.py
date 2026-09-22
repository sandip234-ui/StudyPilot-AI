"""
Pydantic schemas and constants for the StudyPilot Evaluation Framework.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class CriterionType(str, Enum):
    RELEVANCE = "relevance"
    PERSONALIZATION = "personalization"
    INSTRUCTION_ADHERENCE = "instruction_adherence"
    CLARITY = "clarity"
    COMPLETENESS = "completeness"
    DIFFICULTY_ALIGNMENT = "difficulty_alignment"
    TIME_ALIGNMENT = "time_alignment"
    STRUCTURE_SCHEMA_QUALITY = "structure_schema_quality"


# Canonical rubric descriptions for all 8 criteria
RUBRIC_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    CriterionType.RELEVANCE.value: {
        "title": "Relevance",
        "description": "Measures whether the response directly addresses the requested topic and learning goal.",
        "supports_na": False,
        "rubric": {
            1: "Mostly unrelated or misses the requested topic.",
            2: "Partially relevant but contains substantial unrelated content.",
            3: "Generally relevant but includes some unnecessary content.",
            4: "Clearly addresses the requested topic and goal.",
            5: "Highly focused and directly aligned with the requested topic and goal.",
        },
    },
    CriterionType.PERSONALIZATION.value: {
        "title": "Personalization",
        "description": "Measures whether the response appropriately reflects the supplied learner context (no penalty for null optional fields).",
        "supports_na": False,
        "rubric": {
            1: "Ignores the learner context.",
            2: "Uses very little of the available context.",
            3: "Uses some relevant context.",
            4: "Clearly adapts to most applicable learner preferences.",
            5: "Strongly and appropriately adapts to all applicable learner context.",
        },
    },
    CriterionType.INSTRUCTION_ADHERENCE.value: {
        "title": "Instruction Adherence",
        "description": "Measures whether the response follows requested style, output type, goal, and explicit task constraints.",
        "supports_na": False,
        "rubric": {
            1: "Fails to follow the instructions.",
            2: "Follows only a small portion.",
            3: "Generally follows instructions with noticeable deviations.",
            4: "Follows instructions well.",
            5: "Follows all applicable instructions precisely.",
        },
    },
    CriterionType.CLARITY.value: {
        "title": "Clarity",
        "description": "Measures how understandable and well-organized the explanation is for the specified learner level.",
        "supports_na": False,
        "rubric": {
            1: "Very difficult to understand.",
            2: "Often unclear or confusing.",
            3: "Understandable but inconsistent.",
            4: "Clear and well organized.",
            5: "Exceptionally clear and easy to follow for the target learner.",
        },
    },
    CriterionType.COMPLETENESS.value: {
        "title": "Completeness",
        "description": "Measures whether the response covers the essential knowledge requirements for the requested task without superfluous padding.",
        "supports_na": False,
        "rubric": {
            1: "Major required information missing.",
            2: "Several important omissions.",
            3: "Covers the main idea but misses some useful information.",
            4: "Covers the important requirements.",
            5: "Thoroughly covers the relevant learning requirements without unnecessary content.",
        },
    },
    CriterionType.DIFFICULTY_ALIGNMENT.value: {
        "title": "Difficulty Alignment",
        "description": "Measures whether the conceptual depth and complexity match the selected learner level and difficulty.",
        "supports_na": False,
        "rubric": {
            1: "Severely mismatched.",
            2: "Significantly mismatched.",
            3: "Mostly appropriate with some mismatch.",
            4: "Well aligned.",
            5: "Precisely aligned with the learner's requested difficulty and level.",
        },
    },
    CriterionType.TIME_ALIGNMENT.value: {
        "title": "Time Alignment",
        "description": "Measures whether the response is reasonably scoped for the selected study time (mark N/A if time was not specified).",
        "supports_na": True,
        "rubric": {
            1: "Clearly impractical for the available time.",
            2: "Significantly over/under scoped.",
            3: "Reasonably usable but imperfectly scoped.",
            4: "Well scoped for the available time.",
            5: "Very well optimized for the available study time.",
        },
    },
    CriterionType.STRUCTURE_SCHEMA_QUALITY.value: {
        "title": "Structure / Schema Quality",
        "description": "Measures whether the response conforms to the expected structured format (objectives, breakdown, code examples, analogy, quiz, checklist).",
        "supports_na": False,
        "rubric": {
            1: "Severely malformed.",
            2: "Multiple structural problems.",
            3: "Mostly valid but contains notable structural issues.",
            4: "Valid and well structured.",
            5: "Fully valid, complete, and consistently structured.",
        },
    },
}


class CriterionScore(BaseModel):
    criterion: str = Field(..., description="Criterion identifier, e.g. 'relevance'")
    score: Optional[int] = Field(None, ge=1, le=5, description="Rubric score 1-5 or null if N/A")
    max_score: int = Field(5, ge=0, le=5, description="Maximum possible score (5 or 0 if N/A)")
    is_na: bool = Field(False, description="Whether this criterion is marked Not Applicable")
    justification: str = Field("", description="Factual justification for the assigned score")

    @model_validator(mode="after")
    def validate_na_consistency(self) -> "CriterionScore":
        if self.is_na:
            self.score = None
            self.max_score = 0
        else:
            self.max_score = 5
            if self.score is None:
                raise ValueError(f"Score is required for criterion '{self.criterion}' when not marked N/A.")
            if not (1 <= self.score <= 5):
                raise ValueError(f"Score must be between 1 and 5 for '{self.criterion}', got {self.score}.")
        return self


class EvaluationRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    topic: str = Field(..., min_length=1, description="Topic of the evaluated session")
    strategy: Optional[str] = Field(None, description="Strategy name e.g. baseline, role, personalized, structured, few_shot")
    model_used: Optional[str] = Field(None, description="Model used for generation")
    context_used: Optional[Dict[str, Any]] = Field(None, description="Student context used for the session")
    generated_response: Optional[Any] = Field(None, description="Unmodified response that was evaluated")
    scores: List[CriterionScore] = Field(..., min_length=1, description="List of criterion evaluations")


class EvaluationResult(BaseModel):
    total_score: int = Field(..., description="Sum of applicable scores")
    max_score: int = Field(..., description="Sum of applicable maximum scores")
    percentage: float = Field(..., description="Calculated percentage (total_score / max_score) * 100")
    scores: List[CriterionScore] = Field(..., description="Per-criterion evaluation scores and justifications")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
