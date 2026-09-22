"""
Few-Shot Prompt Engineering module.

Implements the experimental comparison between Zero-Shot and Few-Shot prompting
holding the topic, student context, and task definition constant.

Principles
----------
1. The demonstration examples are fixed, curated, and deterministic.
2. The demonstration uses an unrelated topic ("Variables in Java") to prevent leakage.
3. Zero-shot receives the task definition WITHOUT examples.
4. Few-shot receives the SAME task definition PLUS demonstration examples.
"""

from app.prompts.helpers import build_context_section
from app.prompts.strategies import PromptBuildResult
from app.schemas.request import LearnRequest

# ── Fixed, curated demonstration example ──────────────────────────────────────
# Concise, structured demonstration using a distinct educational topic.
# Demonstrates desired instructional tone, clarity, and structural pattern.

FEW_SHOT_DEMONSTRATION_EXAMPLE = """\
DEMONSTRATION EXAMPLE
---------------------
Topic: Variables in Java
Target Level: Beginner

Demonstration Output Pattern:
- Title: Understanding Variables in Java
- Learning Objectives:
  * Define what a variable is in Java
  * Understand primitive vs reference types
  * Declare and initialize variables properly
- Concept Explanation:
  In Java, a variable is a named memory location used to hold values during program execution. Think of it as a container with a designated data type, a name, and a value.
- Examples:
  * Variable declaration and assignment:
    int studentAge = 20;
    String studentName = "Alex";
- Analogy:
  Think of a variable as a labeled storage box in a warehouse that can only store one specific category of item.
- Practice Questions:
  1. What is the difference between declaring a variable and initializing it?
- Revision Checklist:
  * I can declare an int variable in Java.
---------------------"""

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


def build_zero_shot_prompt(request: LearnRequest) -> PromptBuildResult:
    """
    Construct a Zero-Shot learning prompt.

    Contains role, student context, topic, instructions, and output structure
    WITHOUT any demonstration examples.
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
        strategy="zero_shot",
        techniques=(
            "role prompting",
            "context injection",
            "explicit task definition",
            "constraints",
            "structured output instructions",
        ),
        purpose="Demonstrate response generation without demonstration examples (zero-shot baseline).",
    )


def build_few_shot_prompt(request: LearnRequest) -> PromptBuildResult:
    """
    Construct a Few-Shot learning prompt.

    Contains the exact same role, student context, topic, and instructions as
    zero-shot, PLUS the fixed curated demonstration example.
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
        f"{FEW_SHOT_DEMONSTRATION_EXAMPLE}\n\n"
        "OUTPUT STRUCTURE\n"
        "----------------\n"
        f"{_OUTPUT_STRUCTURE}"
    )

    return PromptBuildResult(
        prompt=prompt,
        strategy="few_shot",
        techniques=(
            "role prompting",
            "context injection",
            "explicit task definition",
            "constraints",
            "few-shot demonstrations",
            "structured output instructions",
        ),
        purpose="Demonstrate response generation with curated demonstration examples (few-shot prompting).",
    )
