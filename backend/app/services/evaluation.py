"""
Evaluation service for calculating transparent, rubric-based scores and verifying evaluations.
"""

import logging
from app.schemas.evaluation import EvaluationRequest, EvaluationResult

logger = logging.getLogger(__name__)


def calculate_evaluation(request: EvaluationRequest) -> EvaluationResult:
    """
    Calculate total score, maximum score, and percentage for an evaluation request.
    Strictly excludes N/A criteria from both numerator and denominator.
    """
    applicable_scores = [s.score for s in request.scores if not s.is_na and s.score is not None]
    applicable_max = [s.max_score for s in request.scores if not s.is_na]

    total_score = sum(applicable_scores)
    max_score = sum(applicable_max)

    percentage = round((total_score / max_score * 100.0), 1) if max_score > 0 else 0.0

    return EvaluationResult(
        total_score=total_score,
        max_score=max_score,
        percentage=percentage,
        scores=request.scores,
    )
