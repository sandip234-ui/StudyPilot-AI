"""
Prompt Engineering — core types.

PromptStrategy: the four strategies supported by the engine.
PromptBuildResult: the immutable result returned by build_learning_prompt().
"""

from dataclasses import dataclass
from enum import Enum


class PromptStrategy(str, Enum):
    """
    The four prompt construction strategies supported by StudyPilot.

    Each strategy is a deliberate, named technique rather than an arbitrary
    string so the codebase has a single source of truth.

    baseline    — minimal prompt; control condition for comparison
    role        — adds a tutor role; no student context
    personalized — role + full student context (only provided fields)
    structured  — personalized + explicit task definition, constraints,
                  and output structure instructions
    """
    baseline     = "baseline"
    role         = "role"
    personalized = "personalized"
    structured   = "structured"


@dataclass(frozen=True)
class PromptBuildResult:
    """
    The result of building a prompt for a given strategy.

    Attributes
    ----------
    prompt      : The complete prompt string ready to be sent to a model.
    strategy    : The strategy name (matches PromptStrategy.value).
    techniques  : Human-readable list of prompt engineering techniques used.
    purpose     : One-sentence description of what this strategy demonstrates.
    """
    prompt: str
    strategy: str
    techniques: tuple[str, ...]
    purpose: str

    def techniques_list(self) -> list[str]:
        """Return techniques as a plain list (for JSON serialisation)."""
        return list(self.techniques)
