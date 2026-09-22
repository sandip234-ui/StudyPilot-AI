"""
Few-Shot Prompt Engineering Lab service.

Executes Zero-Shot and Few-Shot prompting sequentially on the exact same student
request context and collects comparative results.

Failure Isolation
-----------------
If one generation fails (timeout, JSON error, parsing failure), the other continues
executing. The failed run reports success=False and an error message in the response
without failing the entire HTTP request.
"""

import logging
from app.core.config import settings
from app.prompts.few_shot import (
    FEW_SHOT_DEMONSTRATION_EXAMPLE,
    build_few_shot_prompt,
    build_zero_shot_prompt,
)
from app.schemas.few_shot import FewShotLabResponse, FewShotStrategyResult
from app.schemas.request import LearnRequest
from app.services.learning import _JSON_OUTPUT_INSTRUCTION, _build_context_used, _generation_time_ms
from app.services.ollama import OllamaRawResponse, ollama_service
from app.services.response_parser import parse_learning_session

logger = logging.getLogger(__name__)


async def run_few_shot_lab(request: LearnRequest) -> FewShotLabResponse:
    """
    Run the Few-Shot Lab experiment comparing Zero-Shot vs Few-Shot.

    Parameters
    ----------
    request : Validated LearnRequest.

    Returns
    -------
    FewShotLabResponse containing comparative results for zero-shot and few-shot.
    """
    context_used = _build_context_used(request)
    model_name = settings.OLLAMA_MODEL or "unknown"
    results: list[FewShotStrategyResult] = []

    logger.info("Starting Few-Shot Lab experiment for topic: %r", request.topic)

    experiments = [
        ("zero_shot", build_zero_shot_prompt, None),
        ("few_shot", build_few_shot_prompt, FEW_SHOT_DEMONSTRATION_EXAMPLE),
    ]

    for strat_name, builder_func, demo_examples in experiments:
        prompt_result = builder_func(request)
        pure_prompt = prompt_result.prompt
        augmented_prompt = pure_prompt + _JSON_OUTPUT_INSTRUCTION

        logger.info("Few-Shot Lab: executing %s", strat_name)

        try:
            raw: OllamaRawResponse = await ollama_service.generate(augmented_prompt)
            learning_session = parse_learning_session(raw.text)
            model_name = raw.model

            results.append(
                FewShotStrategyResult(
                    strategy=strat_name,
                    prompt=pure_prompt,
                    demonstration_examples=demo_examples,
                    techniques=list(prompt_result.techniques),
                    purpose=prompt_result.purpose,
                    response=learning_session,
                    generation_time_ms=_generation_time_ms(raw),
                    tokens_used=raw.eval_count,
                    success=True,
                    error=None,
                )
            )
        except Exception as exc:
            logger.warning("Few-Shot Lab: %s failed: %s", strat_name, exc)
            results.append(
                FewShotStrategyResult(
                    strategy=strat_name,
                    prompt=pure_prompt,
                    demonstration_examples=demo_examples,
                    techniques=list(prompt_result.techniques),
                    purpose=prompt_result.purpose,
                    response=None,
                    generation_time_ms=None,
                    tokens_used=None,
                    success=False,
                    error=str(exc),
                )
            )

    return FewShotLabResponse(
        model_used=model_name,
        request_context=context_used,
        results=results,
    )
