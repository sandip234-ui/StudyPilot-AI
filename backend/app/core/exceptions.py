"""
StudyPilot application-level exceptions.

All exceptions that cross a service boundary should be one of these types.
The route handler converts them to appropriate HTTP status codes so that
raw Python exceptions never reach the frontend.

Exception hierarchy
-------------------
StudyPilotError
└── OllamaError
    ├── OllamaConfigError          → 503  (OLLAMA_MODEL not set)
    ├── OllamaUnavailableError     → 503  (daemon not reachable / HTTP error)
    ├── OllamaModelUnavailableError→ 503  (model not installed in Ollama)
    ├── OllamaTimeoutError         → 504  (generation timed out)
    └── OllamaResponseError        → 502  (empty / invalid / unvalidatable response)
"""


class StudyPilotError(Exception):
    """Base class for all StudyPilot application errors."""


class OllamaError(StudyPilotError):
    """Base class for all Ollama-related errors."""


class OllamaConfigError(OllamaError):
    """
    OLLAMA_MODEL is not configured.

    HTTP mapping: 503 Service Unavailable
    User message: The AI model is not configured — set OLLAMA_MODEL in .env.
    """


class OllamaUnavailableError(OllamaError):
    """
    The Ollama daemon cannot be reached (ConnectError or unexpected HTTP error).

    HTTP mapping: 503 Service Unavailable
    User message: StudyPilot could not connect to Ollama.
    """


class OllamaModelUnavailableError(OllamaError):
    """
    The configured model is not installed in Ollama.

    HTTP mapping: 503 Service Unavailable
    User message: The configured AI model is not available in Ollama.
    """


class OllamaTimeoutError(OllamaError):
    """
    The Ollama generate call exceeded the configured timeout.

    HTTP mapping: 504 Gateway Timeout
    User message: The AI model took too long to respond.
    """


class OllamaResponseError(OllamaError):
    """
    Ollama returned an empty, non-JSON, or structurally invalid response.

    HTTP mapping: 502 Bad Gateway
    User message: StudyPilot received an unexpected response from the AI model.
    """
