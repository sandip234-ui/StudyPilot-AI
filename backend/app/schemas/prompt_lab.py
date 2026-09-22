"""
Pydantic schemas for the /api/prompt-lab endpoint.

Supports experimental comparison of all four prompt strategies on the same
student request.
"""

from typing import Optional
from pydantic import BaseModel

from app.schemas.response import ContextUsed, LearningSession


class PromptLabStrategyResult(BaseModel):
    """Result of running a single prompt engineering strategy."""
    strategy: str
    prompt: str
    techniques: list[str]
    purpose: str
    response: Optional[LearningSession] = None
    generation_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    success: bool
    error: Optional[str] = None


class PromptLabResponse(BaseModel):
    """Top-level response returned by POST /api/prompt-lab."""
    # Suppress Pydantic protected namespace warning for model_ fields
    model_config = {"protected_namespaces": ()}

    model_used: str
    request_context: ContextUsed
    results: list[PromptLabStrategyResult]
