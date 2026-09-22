"""
API route handlers.

Rule: Keep handlers thin.
  Route → validates request (Pydantic, FastAPI)
        → delegates to service
        → catches domain exceptions → HTTP errors
        → returns response

No business logic lives here.  See app/services/learning.py.

Error HTTP status mapping
-------------------------
OllamaConfigError           → 503  (model not configured)
OllamaUnavailableError      → 503  (daemon not running)
OllamaModelUnavailableError → 503  (model not installed)
OllamaTimeoutError          → 504  (generation timed out)
OllamaResponseError         → 502  (empty / invalid model output)
"""

import logging

from fastapi import APIRouter, HTTPException

from app.core.exceptions import (
    OllamaConfigError,
    OllamaModelUnavailableError,
    OllamaResponseError,
    OllamaTimeoutError,
    OllamaUnavailableError,
)
from app.schemas.evaluation import EvaluationRequest, EvaluationResult
from app.schemas.few_shot import FewShotLabResponse
from app.schemas.prompt_lab import PromptLabResponse
from app.schemas.request import LearnRequest
from app.schemas.response import LearnResponse
from app.services.evaluation import calculate_evaluation
from app.services.few_shot import run_few_shot_lab
from app.services.learning import generate_learning_session
from app.services.prompt_lab import run_prompt_lab

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check():
    """
    Confirm the API server is running.
    Does not check Ollama — the Ollama check is performed lazily on /api/learn.
    """
    return {"status": "ok", "service": "studypilot-backend"}


@router.post("/learn", response_model=LearnResponse, tags=["learning"])
async def learn(request: LearnRequest) -> LearnResponse:
    """
    Generate a personalised AI learning session.

    Required body fields : topic, knowledge_level, learning_goal
    Optional body fields : available_time, explanation_style, difficulty, output_type

    Prompt strategy used : personalized
    Model                : configured via OLLAMA_MODEL in .env
    """
    try:
        return await generate_learning_session(request)

    except OllamaConfigError as exc:
        logger.error("Ollama config error: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    except OllamaModelUnavailableError as exc:
        logger.error("Ollama model unavailable: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    except OllamaUnavailableError as exc:
        logger.error("Ollama unavailable: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    except OllamaTimeoutError as exc:
        logger.error("Ollama timeout: %s", exc)
        raise HTTPException(status_code=504, detail=str(exc)) from exc

    except OllamaResponseError as exc:
        logger.error("Ollama response error: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/prompt-lab", response_model=PromptLabResponse, tags=["prompt-lab"])
async def prompt_lab(request: LearnRequest) -> PromptLabResponse:
    """
    Run an experimental comparison across all four prompt strategies.

    Executes baseline, role, personalized, and structured strategies sequentially
    using the exact same request context and returns comparative results.
    """
    return await run_prompt_lab(request)


@router.post("/few-shot-lab", response_model=FewShotLabResponse, tags=["few-shot-lab"])
async def few_shot_lab(request: LearnRequest) -> FewShotLabResponse:
    """
    Run an experimental comparison between Zero-Shot and Few-Shot prompting.

    Executes zero-shot and few-shot sequentially on the exact same student context
    and returns comparative results.
    """
    return await run_few_shot_lab(request)


@router.post("/evaluate", response_model=EvaluationResult, tags=["evaluation"])
async def evaluate_response(request: EvaluationRequest) -> EvaluationResult:
    """
    Verify and calculate transparent rubric-based scores for an evaluation request.
    Strictly excludes N/A criteria from both numerator and denominator.
    """
    return calculate_evaluation(request)


