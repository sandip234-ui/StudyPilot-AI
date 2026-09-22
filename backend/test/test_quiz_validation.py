"""
Tests for QuizQuestion validation and semantic consistency checks.

Verifies:
- Exactly four options requirement
- Valid correct_index bounds (0..3)
- Internal consistency between correct_answer and correct_index
- Contradiction rejection when correct_answer != options[correct_index]
- Backward compatibility when correct_answer is omitted
"""

import pytest
from pydantic import ValidationError
from app.schemas.response import QuizQuestion


class TestQuizQuestionValidation:
    def test_valid_quiz_question_without_correct_answer(self):
        """Backward compatibility: quiz question without correct_answer is valid."""
        q = QuizQuestion(
            question="What is a Python list?",
            options=["A mutable sequence", "An immutable sequence", "A fixed-size array", "A hash map"],
            correct_index=0,
            explanation="Python lists are mutable sequence types.",
        )
        assert q.correct_index == 0
        assert len(q.options) == 4
        assert q.correct_answer is None

    def test_valid_quiz_question_with_matching_correct_answer(self):
        """Valid question where options[correct_index] exactly matches correct_answer."""
        q = QuizQuestion(
            question="Which method adds an element to the end of a list?",
            options=["insert()", "append()", "extend()", "add()"],
            correct_index=1,
            explanation="append() adds an item to the end.",
            correct_answer="append()",
        )
        assert q.correct_index == 1
        assert q.options[q.correct_index] == "append()"
        assert q.correct_answer == "append()"

    def test_valid_quiz_question_with_normalized_matching_answer(self):
        """Handles minor whitespace, casing, or option prefix differences gracefully."""
        q = QuizQuestion(
            question="What is the index of the first element in Python?",
            options=["A. 0", "B. 1", "C. -1", "D. None"],
            correct_index=0,
            explanation="Python uses 0-based indexing.",
            correct_answer="0",
        )
        assert q.correct_index == 0

    def test_rejection_when_fewer_than_four_options(self):
        """Quiz question with 3 options must be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            QuizQuestion(
                question="What is 2 + 2?",
                options=["3", "4", "5"],
                correct_index=1,
                explanation="2 + 2 is 4.",
            )
        assert "exactly 4 options" in str(exc_info.value)

    def test_rejection_when_more_than_four_options(self):
        """Quiz question with 5 options must be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            QuizQuestion(
                question="What is 2 + 2?",
                options=["1", "2", "3", "4", "5"],
                correct_index=3,
                explanation="2 + 2 is 4.",
            )
        assert "exactly 4 options" in str(exc_info.value)

    def test_rejection_when_option_is_empty_string(self):
        """Quiz options must not be blank."""
        with pytest.raises(ValidationError) as exc_info:
            QuizQuestion(
                question="What is 2 + 2?",
                options=["3", "4", " ", "6"],
                correct_index=1,
                explanation="2 + 2 is 4.",
            )
        assert "must be non-empty" in str(exc_info.value)

    def test_rejection_when_correct_index_negative(self):
        """Negative correct_index must be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            QuizQuestion(
                question="What is 2 + 2?",
                options=["3", "4", "5", "6"],
                correct_index=-1,
                explanation="2 + 2 is 4.",
            )
        assert "out of bounds" in str(exc_info.value)

    def test_rejection_when_correct_index_out_of_bounds(self):
        """correct_index >= 4 must be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            QuizQuestion(
                question="What is 2 + 2?",
                options=["3", "4", "5", "6"],
                correct_index=4,
                explanation="2 + 2 is 4.",
            )
        assert "out of bounds" in str(exc_info.value)

    def test_rejection_when_correct_answer_contradicts_selected_option(self):
        """If correct_answer points to a different option than correct_index, reject."""
        with pytest.raises(ValidationError) as exc_info:
            QuizQuestion(
                question="What is the benefit of arrays over lists?",
                options=[
                    "Arrays are more flexible",
                    "Arrays are faster",
                    "Arrays use less memory",
                    "Arrays are more secure",
                ],
                correct_index=3,  # Points to "Arrays are more secure"
                correct_answer="Arrays use less memory",  # Contradicts index 3 (matches index 2)
                explanation="Arrays use contiguous memory and less overhead.",
            )
        assert "Quiz question contradiction" in str(exc_info.value)


class TestParserQuizFiltering:
    def test_filter_drops_contradictory_quiz_item(self):
        from app.services.response_parser import _filter_inconsistent_quiz_items
        data = {
            "title": "Arrays in Python",
            "quiz": [
                {
                    "question": "Consistent Question",
                    "options": ["A", "B", "C", "D"],
                    "correct_index": 0,
                    "correct_answer": "A",
                    "explanation": "A is correct.",
                },
                {
                    "question": "Contradictory Question",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correct_index": 2,  # Points to Option 3
                    "correct_answer": "Option 1",  # Contradicts index 2
                    "explanation": "Option 1 is correct.",
                },
            ],
        }
        filtered = _filter_inconsistent_quiz_items(data)
        assert len(filtered["quiz"]) == 1
        assert filtered["quiz"][0]["question"] == "Consistent Question"

    def test_filter_drops_malformed_options_count(self):
        from app.services.response_parser import _filter_inconsistent_quiz_items
        data = {
            "quiz": [
                {
                    "question": "Only 3 options",
                    "options": ["A", "B", "C"],
                    "correct_index": 0,
                    "explanation": "A is correct",
                }
            ]
        }
        filtered = _filter_inconsistent_quiz_items(data)
        assert filtered["quiz"] is None

