"""
Prompt Engineering — shared helpers.

Provides:
  LABEL_* dicts    — convert enum values to human-readable display strings
  build_context_section() — shared context builder for personalized and
                             structured strategies

Design rule:
  Optional fields are ONLY included if they are not None.
  No "None", "not specified", or invented defaults are ever inserted.
"""

from app.schemas.request import LearnRequest


# ── Human-readable label maps ─────────────────────────────────────────────────
# Converts enum .value strings into prompt-friendly display text.
# These are the only place where display labels are defined.

LABEL_LEVEL: dict[str, str] = {
    "beginner":     "Beginner",
    "intermediate": "Intermediate",
    "advanced":     "Advanced",
}

LABEL_GOAL: dict[str, str] = {
    "concept_understanding": "Concept Understanding",
    "exam_preparation":      "Exam Preparation",
    "interview_preparation": "Interview Preparation",
    "assignment":            "Assignment",
    "practice":              "Practice",
}

LABEL_TIME: dict[str, str] = {
    "15_minutes":    "15 minutes",
    "30_minutes":    "30 minutes",
    "1_hour":        "1 hour",
    "2_plus_hours":  "2 or more hours",
}

LABEL_STYLE: dict[str, str] = {
    "simple":        "Simple",
    "step_by_step":  "Step-by-step",
    "example_based": "Example-based",
    "analogy_based": "Analogy-based",
    "detailed":      "Detailed",
}

LABEL_DIFFICULTY: dict[str, str] = {
    "easy":   "Easy",
    "medium": "Medium",
    "hard":   "Hard",
}

LABEL_OUTPUT: dict[str, str] = {
    "explanation":               "Explanation",
    "study_notes":               "Study Notes",
    "practice_questions":        "Practice Questions",
    "quiz":                      "Quiz",
    "complete_learning_session": "Complete Learning Session",
}

# Indefinite article for each knowledge level (used in personalized intro line).
_LEVEL_ARTICLE: dict[str, str] = {
    "beginner":     "a",
    "intermediate": "an",
    "advanced":     "an",
}


# ── Context section builder ───────────────────────────────────────────────────

def build_context_section(request: LearnRequest) -> str:
    """
    Build the student context block shared by the personalized and structured
    prompt strategies.

    Rules:
      - knowledge_level and learning_goal are always included (required fields).
      - available_time, explanation_style, difficulty, and output_type are
        included ONLY when the field is not None.
      - No "None", "not specified", or any invented value is ever emitted.

    Returns a multi-line string, e.g.:

        Knowledge level: Beginner
        Learning goal: Exam Preparation
        Available study time: 30 minutes
        Explanation style: Example-based
        Difficulty: Medium
        Desired output: Complete Learning Session
    """
    lines: list[str] = []

    # Required — always present
    lines.append(f"Knowledge level: {LABEL_LEVEL[request.knowledge_level.value]}")
    lines.append(f"Learning goal: {LABEL_GOAL[request.learning_goal.value]}")

    # Optional — only when provided
    if request.available_time is not None:
        lines.append(f"Available study time: {LABEL_TIME[request.available_time.value]}")

    if request.explanation_style is not None:
        lines.append(f"Explanation style: {LABEL_STYLE[request.explanation_style.value]}")

    if request.difficulty is not None:
        lines.append(f"Difficulty: {LABEL_DIFFICULTY[request.difficulty.value]}")

    if request.output_type is not None:
        lines.append(f"Desired output: {LABEL_OUTPUT[request.output_type.value]}")

    return "\n".join(lines)


def level_article(request: LearnRequest) -> str:
    """Return the correct indefinite article ('a' or 'an') for the knowledge level."""
    return _LEVEL_ARTICLE[request.knowledge_level.value]
