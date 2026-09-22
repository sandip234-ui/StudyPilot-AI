"""
Prompt Engineering Engine.

Public interface
----------------
    build_learning_prompt(request, strategy) -> PromptBuildResult

Internal structure
------------------
    _build_baseline(request)     → PromptBuildResult
    _build_role(request)         → PromptBuildResult
    _build_personalized(request) → PromptBuildResult
    _build_structured(request)   → PromptBuildResult

Each private builder is self-contained and easy to inspect independently.
The goal is that a reviewer can open this file and immediately read exactly
what each strategy sends to the model.

This module DOES NOT call Ollama. It only constructs prompt strings.
"""

from app.prompts.strategies import PromptBuildResult, PromptStrategy
from app.prompts.helpers import (
    LABEL_LEVEL,
    build_context_section,
    level_article,
)
from app.schemas.request import LearnRequest


# ── Public entry point ────────────────────────────────────────────────────────

def build_learning_prompt(
    request: LearnRequest,
    strategy: PromptStrategy,
) -> PromptBuildResult:
    """
    Construct a learning prompt for the given strategy.

    Parameters
    ----------
    request  : Validated LearnRequest from the API layer.
    strategy : One of PromptStrategy.{baseline, role, personalized, structured}.

    Returns
    -------
    PromptBuildResult containing the prompt string and strategy metadata.

    Raises
    ------
    ValueError if an unknown strategy is passed (should not happen with the enum).
    """
    builders = {
        PromptStrategy.baseline:     _build_baseline,
        PromptStrategy.role:         _build_role,
        PromptStrategy.personalized: _build_personalized,
        PromptStrategy.structured:   _build_structured,
    }
    builder = builders.get(strategy)
    if builder is None:
        raise ValueError(f"Unknown prompt strategy: {strategy!r}")
    return builder(request)


# ── Strategy 1: BASELINE ──────────────────────────────────────────────────────
#
# Deliberately minimal. The prompt contains only the topic and nothing else.
# This is the control condition — it measures what a model produces without
# any prompt engineering applied.
#
# Technique demonstrated: direct instruction

def _build_baseline(request: LearnRequest) -> PromptBuildResult:
    """
    Baseline prompt — minimal, topic only.

    What the model receives:
    ------------------------
        {topic}.

    What this demonstrates:
    -----------------------
    The unguided starting point. By comparing other strategies against this,
    we can measure the improvement (or change) that each technique introduces.
    """
    prompt = f"{request.topic}."

    return PromptBuildResult(
        prompt=prompt,
        strategy=PromptStrategy.baseline.value,
        techniques=("direct instruction",),
        purpose="Establish a minimal-prompt baseline for comparison.",
    )


# ── Strategy 2: ROLE ──────────────────────────────────────────────────────────
#
# Introduces role prompting. The model is told it is an expert tutor before
# receiving the topic. No student context is added yet.
#
# Technique demonstrated: role prompting

def _build_role(request: LearnRequest) -> PromptBuildResult:
    """
    Role prompt — adds an instructional persona, topic only.

    What the model receives:
    ------------------------
        You are an expert computer science tutor.

        Explain the following topic clearly and accurately:

        {topic}

    What this demonstrates:
    -----------------------
    Whether assigning a clear instructional role changes the model's tone,
    depth, and approach — before any student context is introduced.
    """
    prompt = (
        "You are an expert computer science tutor.\n\n"
        "Explain the following topic clearly and accurately:\n\n"
        f"{request.topic}"
    )

    return PromptBuildResult(
        prompt=prompt,
        strategy=PromptStrategy.role.value,
        techniques=("role prompting",),
        purpose=(
            "Test whether assigning an instructional role improves the response "
            "compared to the minimal baseline."
        ),
    )


# ── Strategy 3: PERSONALIZED ──────────────────────────────────────────────────
#
# Adds the student's actual context on top of the role.
# Only fields the student actually provided appear in the prompt —
# null fields are silently omitted. No invented defaults.
#
# Techniques demonstrated: role prompting, context injection, learner personalisation

def _build_personalized(request: LearnRequest) -> PromptBuildResult:
    """
    Personalized prompt — role + student context (provided fields only).

    What the model receives (all fields provided):
    ------------------------------------------------
        You are an AI tutor.

        Teach the following topic to a beginner:

        Topic:
        {topic}

        Student context:
        Knowledge level: Beginner
        Learning goal: Exam Preparation
        Available study time: 30 minutes        ← only if provided
        Explanation style: Example-based        ← only if provided
        Difficulty: Medium                      ← only if provided
        Desired output: Complete Learning Session ← only if provided

        Adapt the explanation to this student's context.

    What this demonstrates:
    -----------------------
    How injecting learner-specific context changes the model's output
    compared to a generic role prompt.
    """
    article = level_article(request)
    level_label = LABEL_LEVEL[request.knowledge_level.value]
    context_block = build_context_section(request)

    prompt = (
        f"You are an AI tutor.\n\n"
        f"Teach the following topic to {article} {request.knowledge_level.value}:\n\n"
        f"Topic:\n{request.topic}\n\n"
        f"Student context:\n{context_block}\n\n"
        f"Adapt the explanation to this student's context."
    )

    return PromptBuildResult(
        prompt=prompt,
        strategy=PromptStrategy.personalized.value,
        techniques=(
            "role prompting",
            "context injection",
            "learner personalisation",
        ),
        purpose="Adapt the response to the individual learner's context and needs.",
    )


# ── Strategy 4: STRUCTURED ───────────────────────────────────────────────────
#
# The most explicit strategy. Combines role, student context, a numbered
# instruction set, and an explicit output structure.
#
# This strategy gives the model the clearest possible specification of both
# HOW to reason and WHAT to produce — without asking it to reveal reasoning.
#
# Techniques demonstrated: role prompting, context injection, explicit task
# definition, constraints, structured output instructions.

_INSTRUCTIONS = """\
1. Adapt the explanation to the student's knowledge level.
2. Align the content with the student's learning goal.
3. Respect the available study time if provided.
4. Follow the requested explanation style if provided.
5. Set the difficulty appropriately.
6. Focus on conceptual clarity.
7. Use relevant, concrete examples.
8. Avoid unnecessary information.
9. Base all quiz questions strictly on facts explicitly explained in this lesson, ensuring exactly one objectively correct answer."""

_OUTPUT_STRUCTURE = """\
Return the learning session using these sections:

1. Title
2. Learning Objectives
3. Concept Explanation
4. Topic Breakdown
5. Examples
6. Analogy
7. Practice Questions
8. Quiz
9. Revision Checklist"""

def _build_structured(request: LearnRequest) -> PromptBuildResult:
    """
    Structured prompt — role + context + explicit task definition + output structure.

    What the model receives:
    ------------------------
        You are an expert AI tutor specialising in personalised education.

        Your task is to teach the student the requested topic.

        STUDENT CONTEXT
        ---------------
        Knowledge level: Beginner
        Learning goal: Exam Preparation
        Available study time: 30 minutes    ← only if provided
        Explanation style: Example-based    ← only if provided
        Difficulty: Medium                  ← only if provided
        Desired output: Complete Learning Session ← only if provided

        TOPIC
        -----
        {topic}

        INSTRUCTIONS
        ------------
        1. Adapt the explanation to the student's knowledge level.
        2. Align the content with the student's learning goal.
        ...

        OUTPUT STRUCTURE
        ----------------
        Return the learning session using these sections:
        1. Title
        ...

    What this demonstrates:
    -----------------------
    How structured instructions and an explicit output contract affect
    the completeness and consistency of the model's response.
    """
    context_block = build_context_section(request)

    prompt = (
        "You are an expert AI tutor specialising in personalised education.\n\n"
        "Your task is to teach the student the requested topic.\n\n"
        "STUDENT CONTEXT\n"
        "---------------\n"
        f"{context_block}\n\n"
        "TOPIC\n"
        "-----\n"
        f"{request.topic}\n\n"
        "INSTRUCTIONS\n"
        "------------\n"
        f"{_INSTRUCTIONS}\n\n"
        "OUTPUT STRUCTURE\n"
        "----------------\n"
        f"{_OUTPUT_STRUCTURE}"
    )

    return PromptBuildResult(
        prompt=prompt,
        strategy=PromptStrategy.structured.value,
        techniques=(
            "role prompting",
            "context injection",
            "explicit task definition",
            "constraints",
            "structured output instructions",
        ),
        purpose=(
            "Provide the model with detailed instructions for generating a "
            "consistent, well-structured learning session."
        ),
    )
