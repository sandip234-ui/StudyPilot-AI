"""
Prompt Engineering Lab service.

Executes all four prompt strategies (baseline, role, personalized, structured)
sequentially on the exact same student request context and collects comparative results.

Failure Isolation
-----------------
If one strategy fails (Ollama timeout, JSON error, parsing failure), the other
strategies continue executing. The failed strategy reports success=False and an
error message in the response without failing the whole experiment.
"""

import logging
import time
from app.core.config import settings
from app.prompts.engine import build_learning_prompt
from app.prompts.strategies import PromptStrategy
from app.schemas.request import LearnRequest
from app.schemas.prompt_lab import PromptLabResponse, PromptLabStrategyResult
from app.services.learning import _JSON_OUTPUT_INSTRUCTION, _build_context_used, _generation_time_ms
from app.services.ollama import OllamaRawResponse, ollama_service
from app.services.response_parser import parse_learning_session

logger = logging.getLogger(__name__)

_STRATEGIES = [
    PromptStrategy.baseline,
    PromptStrategy.role,
    PromptStrategy.personalized,
    PromptStrategy.structured,
]


async def run_prompt_lab(request: LearnRequest) -> PromptLabResponse:
    """
    Run the Prompt Engineering Lab experiment across all four prompt strategies.

    Parameters
    ----------
    request : Validated LearnRequest.

    Returns
    -------
    PromptLabResponse containing comparative results for each strategy.
    """
    context_used = _build_context_used(request)
    model_name = settings.OLLAMA_MODEL or "unknown"
    results: list[PromptLabStrategyResult] = []

    logger.info("Starting Prompt Lab experiment for topic: %r", request.topic)
    total_start = time.perf_counter()

    for strategy in _STRATEGIES:
        strategy_start = time.perf_counter()
        prompt_result = build_learning_prompt(request, strategy)
        pure_prompt = prompt_result.prompt
        augmented_prompt = pure_prompt + _JSON_OUTPUT_INSTRUCTION

        logger.info("Prompt Lab: executing strategy %s", strategy.value)

        try:
            raw: OllamaRawResponse = await ollama_service.generate(augmented_prompt)
            learning_session = parse_learning_session(raw.text)
            model_name = raw.model
            gen_ms = _generation_time_ms(raw)
            strategy_elapsed = int((time.perf_counter() - strategy_start) * 1000)

            logger.info(
                "Prompt Lab: strategy %s completed in %d ms (eval_ms=%s, tokens=%s)",
                strategy.value,
                strategy_elapsed,
                gen_ms,
                raw.eval_count,
            )

            results.append(
                PromptLabStrategyResult(
                    strategy=strategy.value,
                    prompt=pure_prompt,
                    techniques=list(prompt_result.techniques),
                    purpose=prompt_result.purpose,
                    response=learning_session,
                    generation_time_ms=gen_ms,
                    tokens_used=raw.eval_count,
                    success=True,
                    error=None,
                )
            )
        except Exception as exc:
            logger.warning(
                "Prompt Lab: strategy %s failed: %s", strategy.value, exc
            )
            results.append(
                PromptLabStrategyResult(
                    strategy=strategy.value,
                    prompt=pure_prompt,
                    techniques=list(prompt_result.techniques),
                    purpose=prompt_result.purpose,
                    response=None,
                    generation_time_ms=None,
                    tokens_used=None,
                    success=False,
                    error=str(exc),
                )
            )

    total_elapsed = int((time.perf_counter() - total_start) * 1000)
    logger.info(
        "Prompt Lab: all %d strategies completed in %d ms total",
        len(_STRATEGIES),
        total_elapsed,
    )

    return PromptLabResponse(
        model_used=model_name,
        request_context=context_used,
        results=results,
    )
