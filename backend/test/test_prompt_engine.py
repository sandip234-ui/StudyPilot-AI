"""
Prompt Engineering Engine — unit tests.

Coverage
--------
  TestStrategiesEnum          — enum values exist and are correct
  TestPromptBuildResult       — result type has required attributes
  TestBaselineStrategy        — minimal prompt, no context
  TestRoleStrategy            — role text, topic, no student context
  TestPersonalizedStrategy    — student context injected when provided
  TestStructuredStrategy      — role + context + instructions + output spec
  TestNullHandling            — no "None", no fake defaults for optional fields
  TestStrategyIsolation       — strategies don't leak each other's content
  TestMetadata                — every strategy returns techniques and purpose
  TestContextHelper           — build_context_section() in isolation
  TestAllStrategiesContainTopic — topic is never lost

All tests run without Ollama. No HTTP calls are made.
"""

import pytest

from app.schemas.request import (
    AvailableTime,
    Difficulty,
    ExplanationStyle,
    KnowledgeLevel,
    LearnRequest,
    LearningGoal,
    OutputType,
)
from app.prompts.strategies import PromptBuildResult, PromptStrategy
from app.prompts.engine import build_learning_prompt
from app.prompts.helpers import build_context_section


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def full_request() -> LearnRequest:
    """Request with every field populated — the reference case."""
    return LearnRequest(
        topic="Explain recursion in Java",
        knowledge_level=KnowledgeLevel.beginner,
        learning_goal=LearningGoal.exam_preparation,
        available_time=AvailableTime.thirty_minutes,
        explanation_style=ExplanationStyle.example_based,
        difficulty=Difficulty.medium,
        output_type=OutputType.complete_learning_session,
    )


@pytest.fixture
def minimal_request() -> LearnRequest:
    """Request with only required fields — all optionals are None."""
    return LearnRequest(
        topic="Explain recursion in Java",
        knowledge_level=KnowledgeLevel.beginner,
        learning_goal=LearningGoal.exam_preparation,
    )


@pytest.fixture
def advanced_request() -> LearnRequest:
    """Intermediate knowledge level — exercises the 'an' article path."""
    return LearnRequest(
        topic="Explain binary search trees",
        knowledge_level=KnowledgeLevel.intermediate,
        learning_goal=LearningGoal.interview_preparation,
        available_time=AvailableTime.one_hour,
    )


TOPIC = "Explain recursion in Java"
ALL_STRATEGIES = list(PromptStrategy)


# ── TestStrategiesEnum ────────────────────────────────────────────────────────

class TestStrategiesEnum:
    def test_four_strategies_defined(self):
        assert len(PromptStrategy) == 4

    def test_baseline_value(self):
        assert PromptStrategy.baseline.value == "baseline"

    def test_role_value(self):
        assert PromptStrategy.role.value == "role"

    def test_personalized_value(self):
        assert PromptStrategy.personalized.value == "personalized"

    def test_structured_value(self):
        assert PromptStrategy.structured.value == "structured"

    def test_strategy_is_string_enum(self):
        """PromptStrategy values must be usable directly as strings."""
        for strategy in PromptStrategy:
            assert isinstance(strategy.value, str)


# ── TestPromptBuildResult ─────────────────────────────────────────────────────

class TestPromptBuildResult:
    def test_result_has_prompt(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        assert hasattr(result, "prompt")

    def test_result_has_strategy(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        assert hasattr(result, "strategy")

    def test_result_has_techniques(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        assert hasattr(result, "techniques")

    def test_result_has_purpose(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        assert hasattr(result, "purpose")

    def test_techniques_list_method(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        assert isinstance(result.techniques_list(), list)

    def test_result_is_immutable(self, full_request):
        """PromptBuildResult is frozen — fields cannot be reassigned."""
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        with pytest.raises((AttributeError, TypeError)):
            result.prompt = "mutated"  # type: ignore[misc]


# ── TestAllStrategiesContainTopic ─────────────────────────────────────────────

class TestAllStrategiesContainTopic:
    @pytest.mark.parametrize("strategy", ALL_STRATEGIES)
    def test_topic_present_in_every_strategy(self, strategy, full_request):
        result = build_learning_prompt(full_request, strategy)
        assert TOPIC in result.prompt, (
            f"Strategy [{strategy.value}] prompt does not contain the topic."
        )

    @pytest.mark.parametrize("strategy", ALL_STRATEGIES)
    def test_prompt_is_non_empty(self, strategy, full_request):
        result = build_learning_prompt(full_request, strategy)
        assert len(result.prompt.strip()) > 0


# ── TestBaselineStrategy ──────────────────────────────────────────────────────

class TestBaselineStrategy:
    def test_returns_prompt_build_result(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        assert isinstance(result, PromptBuildResult)

    def test_strategy_field_is_baseline(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        assert result.strategy == "baseline"

    def test_prompt_contains_topic(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        assert TOPIC in result.prompt

    def test_prompt_does_not_contain_knowledge_level(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        assert "Knowledge level" not in result.prompt
        assert "knowledge level" not in result.prompt.lower()

    def test_prompt_does_not_contain_learning_goal(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        assert "Learning goal" not in result.prompt

    def test_prompt_does_not_contain_role_instruction(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        assert "tutor" not in result.prompt.lower()
        assert "You are" not in result.prompt

    def test_baseline_is_shortest_prompt(self, full_request):
        """Baseline must be shorter than all other strategies for the same request."""
        baseline_len = len(build_learning_prompt(full_request, PromptStrategy.baseline).prompt)
        for strategy in [PromptStrategy.role, PromptStrategy.personalized, PromptStrategy.structured]:
            other_len = len(build_learning_prompt(full_request, strategy).prompt)
            assert baseline_len < other_len, (
                f"Baseline ({baseline_len}) is not shorter than {strategy.value} ({other_len})"
            )

    def test_technique_is_direct_instruction(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        assert "direct instruction" in result.techniques_list()

    def test_purpose_is_non_empty(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        assert len(result.purpose.strip()) > 0


# ── TestRoleStrategy ──────────────────────────────────────────────────────────

class TestRoleStrategy:
    def test_returns_prompt_build_result(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.role)
        assert isinstance(result, PromptBuildResult)

    def test_strategy_field_is_role(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.role)
        assert result.strategy == "role"

    def test_prompt_contains_topic(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.role)
        assert TOPIC in result.prompt

    def test_prompt_contains_role_instruction(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.role)
        assert "tutor" in result.prompt.lower()

    def test_prompt_contains_you_are(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.role)
        assert "You are" in result.prompt

    def test_prompt_does_not_contain_knowledge_level_label(self, full_request):
        """Role strategy must not inject student context."""
        result = build_learning_prompt(full_request, PromptStrategy.role)
        assert "Knowledge level" not in result.prompt

    def test_prompt_does_not_contain_learning_goal_label(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.role)
        assert "Learning goal" not in result.prompt

    def test_technique_includes_role_prompting(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.role)
        assert "role prompting" in result.techniques_list()

    def test_purpose_is_non_empty(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.role)
        assert len(result.purpose.strip()) > 0


# ── TestPersonalizedStrategy ──────────────────────────────────────────────────

class TestPersonalizedStrategy:
    def test_returns_prompt_build_result(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.personalized)
        assert isinstance(result, PromptBuildResult)

    def test_strategy_field_is_personalized(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.personalized)
        assert result.strategy == "personalized"

    def test_prompt_contains_topic(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.personalized)
        assert TOPIC in result.prompt

    def test_prompt_contains_role_instruction(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.personalized)
        assert "You are" in result.prompt

    def test_prompt_contains_knowledge_level(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.personalized)
        assert "Knowledge level" in result.prompt

    def test_prompt_contains_learning_goal(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.personalized)
        assert "Learning goal" in result.prompt

    def test_prompt_contains_available_time_when_provided(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.personalized)
        assert "30 minutes" in result.prompt

    def test_prompt_contains_explanation_style_when_provided(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.personalized)
        assert "Example-based" in result.prompt

    def test_prompt_contains_difficulty_when_provided(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.personalized)
        assert "Medium" in result.prompt

    def test_prompt_contains_output_type_when_provided(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.personalized)
        assert "Complete Learning Session" in result.prompt

    def test_techniques_include_context_injection(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.personalized)
        techniques = result.techniques_list()
        assert "context injection" in techniques

    def test_techniques_include_role_prompting(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.personalized)
        assert "role prompting" in result.techniques_list()

    def test_purpose_is_non_empty(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.personalized)
        assert len(result.purpose.strip()) > 0


# ── TestStructuredStrategy ────────────────────────────────────────────────────

class TestStructuredStrategy:
    def test_returns_prompt_build_result(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.structured)
        assert isinstance(result, PromptBuildResult)

    def test_strategy_field_is_structured(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.structured)
        assert result.strategy == "structured"

    def test_prompt_contains_topic(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.structured)
        assert TOPIC in result.prompt

    def test_prompt_contains_role_instruction(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.structured)
        assert "You are" in result.prompt

    def test_prompt_contains_student_context_header(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.structured)
        assert "STUDENT CONTEXT" in result.prompt

    def test_prompt_contains_knowledge_level(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.structured)
        assert "Knowledge level" in result.prompt

    def test_prompt_contains_learning_goal(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.structured)
        assert "Learning goal" in result.prompt

    def test_prompt_contains_available_time_when_provided(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.structured)
        assert "30 minutes" in result.prompt

    def test_prompt_contains_instructions_section(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.structured)
        assert "INSTRUCTIONS" in result.prompt

    def test_prompt_contains_output_structure_section(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.structured)
        assert "OUTPUT STRUCTURE" in result.prompt

    def test_prompt_contains_numbered_output_sections(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.structured)
        assert "Learning Objectives" in result.prompt
        assert "Concept Explanation" in result.prompt
        assert "Revision Checklist" in result.prompt

    def test_structured_is_longest_prompt(self, full_request):
        """Structured should be the most verbose strategy."""
        structured_len = len(build_learning_prompt(full_request, PromptStrategy.structured).prompt)
        for strategy in [PromptStrategy.baseline, PromptStrategy.role, PromptStrategy.personalized]:
            other_len = len(build_learning_prompt(full_request, strategy).prompt)
            assert structured_len > other_len, (
                f"Structured ({structured_len}) is not longer than {strategy.value} ({other_len})"
            )

    def test_techniques_include_structured_output_instructions(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.structured)
        assert "structured output instructions" in result.techniques_list()

    def test_techniques_include_explicit_task_definition(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.structured)
        assert "explicit task definition" in result.techniques_list()

    def test_purpose_is_non_empty(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.structured)
        assert len(result.purpose.strip()) > 0


# ── TestNullHandling ──────────────────────────────────────────────────────────

class TestNullHandling:
    """
    When all optional fields are None, no strategy should emit:
      - the string "None"
      - field labels with blank values
      - invented defaults
    """

    @pytest.mark.parametrize("strategy", ALL_STRATEGIES)
    def test_no_none_string_in_prompt(self, strategy, minimal_request):
        result = build_learning_prompt(minimal_request, strategy)
        assert "None" not in result.prompt, (
            f"Strategy [{strategy.value}] contains the string 'None' "
            f"when optional fields are null."
        )

    @pytest.mark.parametrize("strategy", ALL_STRATEGIES)
    def test_no_null_string_in_prompt(self, strategy, minimal_request):
        result = build_learning_prompt(minimal_request, strategy)
        assert "null" not in result.prompt.lower()

    def test_personalized_omits_available_time_when_none(self, minimal_request):
        result = build_learning_prompt(minimal_request, PromptStrategy.personalized)
        assert "Available study time" not in result.prompt
        assert "30 minutes" not in result.prompt

    def test_personalized_omits_explanation_style_when_none(self, minimal_request):
        result = build_learning_prompt(minimal_request, PromptStrategy.personalized)
        assert "Explanation style" not in result.prompt

    def test_personalized_omits_difficulty_when_none(self, minimal_request):
        result = build_learning_prompt(minimal_request, PromptStrategy.personalized)
        assert "Difficulty" not in result.prompt

    def test_personalized_omits_output_type_when_none(self, minimal_request):
        result = build_learning_prompt(minimal_request, PromptStrategy.personalized)
        assert "Desired output" not in result.prompt

    def test_structured_omits_available_time_when_none(self, minimal_request):
        result = build_learning_prompt(minimal_request, PromptStrategy.structured)
        assert "Available study time" not in result.prompt

    def test_structured_omits_optional_fields_when_none(self, minimal_request):
        result = build_learning_prompt(minimal_request, PromptStrategy.structured)
        assert "Explanation style" not in result.prompt
        assert "Difficulty" not in result.prompt
        assert "Desired output" not in result.prompt

    def test_personalized_still_has_required_context_when_optionals_null(self, minimal_request):
        result = build_learning_prompt(minimal_request, PromptStrategy.personalized)
        assert "Knowledge level" in result.prompt
        assert "Learning goal" in result.prompt

    def test_structured_still_has_required_context_when_optionals_null(self, minimal_request):
        result = build_learning_prompt(minimal_request, PromptStrategy.structured)
        assert "Knowledge level" in result.prompt
        assert "Learning goal" in result.prompt

    def test_no_not_specified_placeholder(self, minimal_request):
        """Engines must not invent 'not specified' or similar defaults."""
        for strategy in ALL_STRATEGIES:
            result = build_learning_prompt(minimal_request, strategy)
            assert "not specified" not in result.prompt.lower()
            assert "not provided" not in result.prompt.lower()
            assert "n/a" not in result.prompt.lower()


# ── TestStrategyIsolation ─────────────────────────────────────────────────────

class TestStrategyIsolation:
    """
    Verify that strategies do not leak content from more advanced strategies.
    baseline < role < personalized < structured (in terms of content added).
    """

    def test_baseline_has_no_role_text(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        assert "You are" not in result.prompt
        assert "tutor" not in result.prompt.lower()

    def test_baseline_has_no_student_context(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        assert "Knowledge level" not in result.prompt
        assert "Learning goal" not in result.prompt
        assert "Exam Preparation" not in result.prompt
        assert "Beginner" not in result.prompt

    def test_baseline_has_no_output_structure(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        assert "OUTPUT STRUCTURE" not in result.prompt
        assert "INSTRUCTIONS" not in result.prompt

    def test_role_has_no_student_context_labels(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.role)
        assert "Knowledge level" not in result.prompt
        assert "Learning goal" not in result.prompt

    def test_role_has_no_output_structure(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.role)
        assert "OUTPUT STRUCTURE" not in result.prompt
        assert "INSTRUCTIONS" not in result.prompt

    def test_personalized_has_no_structured_sections(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.personalized)
        assert "OUTPUT STRUCTURE" not in result.prompt
        assert "INSTRUCTIONS" not in result.prompt
        assert "STUDENT CONTEXT" not in result.prompt  # that header is structured only

    def test_structured_contains_everything_personalized_does(self, full_request):
        """Structured is a superset of personalized content."""
        pers = build_learning_prompt(full_request, PromptStrategy.personalized)
        struct = build_learning_prompt(full_request, PromptStrategy.structured)
        # Both must have role, topic, knowledge level, learning goal
        for text in ["You are", TOPIC, "Knowledge level", "Learning goal"]:
            assert text in pers.prompt
            assert text in struct.prompt

    def test_different_strategies_produce_different_prompts(self, full_request):
        prompts = {
            strategy: build_learning_prompt(full_request, strategy).prompt
            for strategy in ALL_STRATEGIES
        }
        prompt_list = list(prompts.values())
        # All four prompts must be unique
        assert len(set(prompt_list)) == 4, "Two or more strategies produced identical prompts"


# ── TestMetadata ──────────────────────────────────────────────────────────────

class TestMetadata:
    @pytest.mark.parametrize("strategy", ALL_STRATEGIES)
    def test_strategy_field_matches_enum_value(self, strategy, full_request):
        result = build_learning_prompt(full_request, strategy)
        assert result.strategy == strategy.value

    @pytest.mark.parametrize("strategy", ALL_STRATEGIES)
    def test_techniques_is_non_empty(self, strategy, full_request):
        result = build_learning_prompt(full_request, strategy)
        assert len(result.techniques) > 0

    @pytest.mark.parametrize("strategy", ALL_STRATEGIES)
    def test_techniques_list_contains_strings(self, strategy, full_request):
        result = build_learning_prompt(full_request, strategy)
        for t in result.techniques_list():
            assert isinstance(t, str) and len(t) > 0

    @pytest.mark.parametrize("strategy", ALL_STRATEGIES)
    def test_purpose_is_non_empty_string(self, strategy, full_request):
        result = build_learning_prompt(full_request, strategy)
        assert isinstance(result.purpose, str)
        assert len(result.purpose.strip()) > 0

    def test_baseline_technique_is_direct_instruction(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.baseline)
        assert "direct instruction" in result.techniques_list()

    def test_role_technique_is_role_prompting(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.role)
        assert "role prompting" in result.techniques_list()

    def test_personalized_has_multiple_techniques(self, full_request):
        result = build_learning_prompt(full_request, PromptStrategy.personalized)
        assert len(result.techniques_list()) >= 2

    def test_structured_has_most_techniques(self, full_request):
        """Structured should document more techniques than any other strategy."""
        structured_count = len(
            build_learning_prompt(full_request, PromptStrategy.structured).techniques_list()
        )
        for strategy in [PromptStrategy.baseline, PromptStrategy.role, PromptStrategy.personalized]:
            other_count = len(build_learning_prompt(full_request, strategy).techniques_list())
            assert structured_count >= other_count


# ── TestContextHelper ─────────────────────────────────────────────────────────

class TestContextHelper:
    def test_always_includes_knowledge_level(self, full_request):
        section = build_context_section(full_request)
        assert "Knowledge level" in section
        assert "Beginner" in section

    def test_always_includes_learning_goal(self, full_request):
        section = build_context_section(full_request)
        assert "Learning goal" in section
        assert "Exam Preparation" in section

    def test_includes_available_time_when_provided(self, full_request):
        section = build_context_section(full_request)
        assert "30 minutes" in section

    def test_includes_explanation_style_when_provided(self, full_request):
        section = build_context_section(full_request)
        assert "Example-based" in section

    def test_includes_difficulty_when_provided(self, full_request):
        section = build_context_section(full_request)
        assert "Medium" in section

    def test_includes_output_type_when_provided(self, full_request):
        section = build_context_section(full_request)
        assert "Complete Learning Session" in section

    def test_omits_all_optional_when_none(self, minimal_request):
        section = build_context_section(minimal_request)
        assert "Available study time" not in section
        assert "Explanation style" not in section
        assert "Difficulty" not in section
        assert "Desired output" not in section

    def test_no_none_string_in_context_section(self, minimal_request):
        section = build_context_section(minimal_request)
        assert "None" not in section

    def test_minimal_context_has_exactly_two_lines(self, minimal_request):
        section = build_context_section(minimal_request)
        lines = [l for l in section.strip().splitlines() if l.strip()]
        assert len(lines) == 2

    def test_full_context_has_six_lines(self, full_request):
        section = build_context_section(full_request)
        lines = [l for l in section.strip().splitlines() if l.strip()]
        assert len(lines) == 6  # knowledge + goal + time + style + difficulty + output

    def test_time_label_30_minutes(self):
        request = LearnRequest(
            topic="Test topic",
            knowledge_level=KnowledgeLevel.beginner,
            learning_goal=LearningGoal.practice,
            available_time=AvailableTime.thirty_minutes,
        )
        section = build_context_section(request)
        assert "30 minutes" in section

    def test_time_label_15_minutes(self):
        request = LearnRequest(
            topic="Test topic",
            knowledge_level=KnowledgeLevel.beginner,
            learning_goal=LearningGoal.practice,
            available_time=AvailableTime.fifteen_minutes,
        )
        section = build_context_section(request)
        assert "15 minutes" in section

    def test_time_label_1_hour(self):
        request = LearnRequest(
            topic="Test topic",
            knowledge_level=KnowledgeLevel.beginner,
            learning_goal=LearningGoal.practice,
            available_time=AvailableTime.one_hour,
        )
        section = build_context_section(request)
        assert "1 hour" in section

    def test_goal_label_concept_understanding(self):
        request = LearnRequest(
            topic="Test topic",
            knowledge_level=KnowledgeLevel.beginner,
            learning_goal=LearningGoal.concept_understanding,
        )
        section = build_context_section(request)
        assert "Concept Understanding" in section

    def test_goal_label_interview_preparation(self):
        request = LearnRequest(
            topic="Test topic",
            knowledge_level=KnowledgeLevel.advanced,
            learning_goal=LearningGoal.interview_preparation,
        )
        section = build_context_section(request)
        assert "Interview Preparation" in section
