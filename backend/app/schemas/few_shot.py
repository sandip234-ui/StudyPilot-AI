"""
Pydantic schemas for the /api/few-shot-lab endpoint.

Supports experimental comparison between Zero-Shot and Few-Shot prompting.
"""

from typing import Optional
from pydantic import BaseModel

from app.schemas.response import ContextUsed, LearningSession


class FewShotStrategyResult(BaseModel):
    """Result of running either Zero-Shot or Few-Shot prompting."""
    strategy: str
    prompt: str
    demonstration_examples: Optional[str] = None
    techniques: list[str]
    purpose: str
    response: Optional[LearningSession] = None
    generation_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    success: bool
    error: Optional[str] = None


class FewShotLabResponse(BaseModel):
    """Top-level response returned by POST /api/few-shot-lab."""
    # Suppress Pydantic protected namespace warning for model_ fields
    model_config = {"protected_namespaces": ()}

    model_used: str
    request_context: ContextUsed
    results: list[FewShotStrategyResult]
