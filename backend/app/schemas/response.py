"""
Pydantic response schemas for the /api/learn endpoint.

The structure is designed to:
  1. Validate the mock response returned in this phase.
  2. Later validate actual LLM-generated output without schema changes.

All section fields in LearningSession are Optional so the frontend
can render gracefully if the model skips a section.
"""

import re
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator


# ── Sub-models for LearningSession sections ───────────────────────────────────

class TopicBreakdownItem(BaseModel):
    heading: str
    content: str


class Example(BaseModel):
    title: str
    code: Optional[str] = None      # Not every example involves code
    explanation: str


class QuizQuestion(BaseModel):
    question: str
    options: list[str]              # Exactly 4 options
    correct_index: int              # 0-based index into options[]
    explanation: str
    correct_answer: Optional[str] = None  # Optional deterministic self-consistency anchor

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: list[str]) -> list[str]:
        if len(v) != 4:
            raise ValueError(f"Quiz question must have exactly 4 options, got {len(v)}")
        if any(not isinstance(opt, str) or not opt.strip() for opt in v):
            raise ValueError("All quiz options must be non-empty strings")
        return v

    @model_validator(mode="after")
    def validate_quiz_consistency(self) -> "QuizQuestion":
        if self.correct_index < 0 or self.correct_index >= len(self.options):
            raise ValueError(
                f"correct_index {self.correct_index} is out of bounds for {len(self.options)} options"
            )

        # Deterministic internal consistency check if correct_answer is provided
        if self.correct_answer is not None and self.correct_answer.strip():
            prefix_pattern = r"^[A-Da-d][.:)\-\s]+"
            norm_selected = re.sub(prefix_pattern, "", self.options[self.correct_index]).strip().lower()
            norm_correct = re.sub(prefix_pattern, "", self.correct_answer).strip().lower()

            matches = (
                norm_selected == norm_correct
                or self.options[self.correct_index].strip().lower() == self.correct_answer.strip().lower()
                or norm_selected in norm_correct
                or norm_correct in norm_selected
            )

            if not matches:
                raise ValueError(
                    f"Quiz question contradiction: options[{self.correct_index}] "
                    f"({self.options[self.correct_index]!r}) does not match correct_answer={self.correct_answer!r}"
                )

        return self


# ── Primary content model ─────────────────────────────────────────────────────

class LearningSession(BaseModel):
    title: str
    learning_objectives: list[str]
    concept_explanation: str
    topic_breakdown: list[TopicBreakdownItem]
    examples: Optional[list[Example]] = None
    analogy: Optional[str] = None
    practice_questions: Optional[list[str]] = None
    quiz: Optional[list[QuizQuestion]] = None
    revision_checklist: list[str]


# ── Response envelope ─────────────────────────────────────────────────────────

class ContextUsed(BaseModel):
    """
    Echoes back the student context that was used to build the prompt.
    Optional fields mirror the request — null means the field was not provided.
    """
    knowledge_level: str
    learning_goal: str
    available_time: Optional[str] = None
    explanation_style: Optional[str] = None
    difficulty: Optional[str] = None
    output_type: Optional[str] = None


class GenerationMeta(BaseModel):
    """
    Metadata about how the response was generated.
    Both fields are null in this phase (mock response).
    Will be populated once Ollama integration is complete.
    """
    tokens_used: Optional[int] = None
    generation_time_ms: Optional[int] = None


class LearnResponse(BaseModel):
    """
    Top-level response returned by POST /api/learn.
    model_used and prompt_strategy are informational fields
    that will support the Prompt Engineering Lab in a future phase.
    """
    # Suppress Pydantic's protected namespace warning for model_ fields.
    model_config = {"protected_namespaces": ()}

    session_id: str
    topic: str
    model_used: str
    prompt_strategy: str
    context_used: ContextUsed
    learning_session: LearningSession
    generation_meta: GenerationMeta
