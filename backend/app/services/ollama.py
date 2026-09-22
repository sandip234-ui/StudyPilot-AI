"""
Ollama HTTP client.

Public interface
----------------
    ollama_service.generate(prompt: str) -> OllamaRawResponse

Responsibilities
----------------
- Validate OLLAMA_MODEL is configured before making any HTTP call.
- POST to the Ollama /api/generate endpoint with stream=False, format="json".
- Translate httpx / HTTP errors into StudyPilot domain exceptions.
- Return raw text and token-count metadata; never parse the model's output.

This module does NOT parse or validate the model's JSON output.
That responsibility belongs to app.services.response_parser.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx

from app.core.config import settings
from app.core.exceptions import (
    OllamaConfigError,
    OllamaModelUnavailableError,
    OllamaResponseError,
    OllamaTimeoutError,
    OllamaUnavailableError,
)

logger = logging.getLogger(__name__)


# ── Response type ─────────────────────────────────────────────────────────────

@dataclass
class OllamaRawResponse:
    """
    Raw, unparsed result from Ollama.

    Attributes
    ----------
    text          : The model-generated text (content of the 'response' key).
    model         : The model name as reported by Ollama.
    eval_count    : Number of tokens evaluated (None if Ollama did not report it).
    eval_duration : Total generation time in nanoseconds (None if not reported).
                    Divide by 1_000_000 to convert to milliseconds.
    """
    text: str
    model: str
    eval_count: Optional[int] = field(default=None)
    eval_duration: Optional[int] = field(default=None)


# ── Service ───────────────────────────────────────────────────────────────────

class OllamaService:
    """
    Async HTTP client for the local Ollama server.

    All configuration (base URL, model, timeout) is read from
    app.core.config.settings at call time, so changes to settings
    during testing are reflected without reinstantiating the service.
    """

    async def generate(self, prompt: str) -> OllamaRawResponse:
        """
        Send a prompt to Ollama and return the raw model response.

        Parameters
        ----------
        prompt : The full prompt string, already assembled by the prompt engine.

        Returns
        -------
        OllamaRawResponse with the generated text and metadata.

        Raises
        ------
        OllamaConfigError           — OLLAMA_MODEL is not set in .env
        OllamaUnavailableError      — daemon is not running or returned an HTTP error
        OllamaModelUnavailableError — model is not installed in Ollama
        OllamaTimeoutError          — generation exceeded OLLAMA_TIMEOUT seconds
        OllamaResponseError         — Ollama returned an empty or error response body
        """
        model = settings.OLLAMA_MODEL
        if not model or not model.strip():
            raise OllamaConfigError(
                "The AI model is not configured. "
                "Set OLLAMA_MODEL in your .env file (e.g. OLLAMA_MODEL=llama3.2:1b) "
                "and restart the server."
            )

        url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }

        logger.debug("POST %s  model=%s  prompt_len=%d", url, model, len(prompt))

        # ── HTTP call ─────────────────────────────────────────────────────────
        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
                resp = await client.post(url, json=payload)

        except httpx.ConnectError as exc:
            logger.error("Ollama connection refused: %s", exc)
            raise OllamaUnavailableError(
                "StudyPilot could not connect to Ollama. "
                "Make sure Ollama is running (run `ollama serve`) and try again."
            ) from exc

        except httpx.TimeoutException as exc:
            logger.error("Ollama timed out after %ss: %s", settings.OLLAMA_TIMEOUT, exc)
            raise OllamaTimeoutError(
                "The AI model took too long to respond. Please try again. "
                f"(Timeout: {int(settings.OLLAMA_TIMEOUT)}s)"
            ) from exc

        http_elapsed = int((time.perf_counter() - start_time) * 1000)

        # ── HTTP status ───────────────────────────────────────────────────────
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error("Ollama HTTP %d: %s", resp.status_code, exc)
            if resp.status_code == 404:
                raise OllamaModelUnavailableError(
                    f"The configured AI model '{model}' is not available in Ollama. "
                    "Please check the model name and your Ollama installation "
                    f"(run `ollama pull {model}` to install it)."
                ) from exc
            raise OllamaUnavailableError(
                "Ollama returned an unexpected error. Please try again."
            ) from exc

        # ── Response body ─────────────────────────────────────────────────────
        data: dict = resp.json()

        # Ollama reports model-not-found or similar errors inside the JSON body
        # (200 status with an "error" key) in some versions.
        if "error" in data:
            error_msg = str(data["error"])
            logger.error("Ollama error body: %s", error_msg)
            if "model" in error_msg.lower():
                raise OllamaModelUnavailableError(
                    f"The configured AI model '{model}' is not available in Ollama. "
                    "Please check the model name and your Ollama installation."
                )
            raise OllamaUnavailableError(
                "Ollama returned an error. Please try again."
            )

        text: str = data.get("response", "").strip()
        if not text:
            logger.error("Ollama returned an empty 'response' field. Body keys: %s", list(data))
            raise OllamaResponseError(
                "StudyPilot received an empty response from the AI model. "
                "Please try again."
            )

        logger.info(
            "Ollama HTTP response received in %d ms: model=%s  eval_count=%s  eval_duration_ms=%s  text_len=%d",
            http_elapsed,
            data.get("model", model),
            data.get("eval_count"),
            (data.get("eval_duration") or 0) // 1_000_000,
            len(text),
        )

        return OllamaRawResponse(
            text=text,
            model=data.get("model", model),
            eval_count=data.get("eval_count"),
            eval_duration=data.get("eval_duration"),
        )


# ── Module-level singleton ────────────────────────────────────────────────────
# Imported and used by app.services.learning.
# In tests, patch app.services.ollama.ollama_service.generate with AsyncMock.

ollama_service = OllamaService()
