/**
 * Frontend rubric definitions and criteria metadata for the StudyPilot Evaluation Framework.
 */

export const RUBRIC_CRITERIA = [
  {
    id: 'relevance',
    title: 'Relevance',
    description: 'Measures whether the response directly addresses the requested topic and learning goal.',
    supportsNa: false,
    rubric: {
      1: 'Mostly unrelated or misses the requested topic.',
      2: 'Partially relevant but contains substantial unrelated content.',
      3: 'Generally relevant but includes some unnecessary content.',
      4: 'Clearly addresses the requested topic and goal.',
      5: 'Highly focused and directly aligned with the requested topic and goal.',
    },
  },
  {
    id: 'personalization',
    title: 'Personalization',
    description: 'Measures whether the response appropriately reflects the supplied learner context (no penalty for null optional fields).',
    supportsNa: false,
    rubric: {
      1: 'Ignores the learner context.',
      2: 'Uses very little of the available context.',
      3: 'Uses some relevant context.',
      4: 'Clearly adapts to most applicable learner preferences.',
      5: 'Strongly and appropriately adapts to all applicable learner context.',
    },
  },
  {
    id: 'instruction_adherence',
    title: 'Instruction Adherence',
    description: 'Measures whether the response follows requested style, output type, goal, and explicit task constraints.',
    supportsNa: false,
    rubric: {
      1: 'Fails to follow the instructions.',
      2: 'Follows only a small portion.',
      3: 'Generally follows instructions with noticeable deviations.',
      4: 'Follows instructions well.',
      5: 'Follows all applicable instructions precisely.',
    },
  },
  {
    id: 'clarity',
    title: 'Clarity',
    description: 'Measures how understandable and well-organized the explanation is for the specified learner level.',
    supportsNa: false,
    rubric: {
      1: 'Very difficult to understand.',
      2: 'Often unclear or confusing.',
      3: 'Understandable but inconsistent.',
      4: 'Clear and well organized.',
      5: 'Exceptionally clear and easy to follow for the target learner.',
    },
  },
  {
    id: 'completeness',
    title: 'Completeness',
    description: 'Measures whether the response covers the essential knowledge requirements for the requested task without superfluous padding.',
    supportsNa: false,
    rubric: {
      1: 'Major required information missing.',
      2: 'Several important omissions.',
      3: 'Covers the main idea but misses some useful information.',
      4: 'Covers the important requirements.',
      5: 'Thoroughly covers the relevant learning requirements without unnecessary content.',
    },
  },
  {
    id: 'difficulty_alignment',
    title: 'Difficulty Alignment',
    description: 'Measures whether the conceptual depth and complexity match the selected learner level and difficulty.',
    supportsNa: false,
    rubric: {
      1: 'Severely mismatched.',
      2: 'Significantly mismatched.',
      3: 'Mostly appropriate with some mismatch.',
      4: 'Well aligned.',
      5: 'Precisely aligned with the learner\'s requested difficulty and level.',
    },
  },
  {
    id: 'time_alignment',
    title: 'Time Alignment',
    description: 'Measures whether the response is reasonably scoped for the selected study time (mark N/A if time was not specified).',
    supportsNa: true,
    rubric: {
      1: 'Clearly impractical for the available time.',
      2: 'Significantly over/under scoped.',
      3: 'Reasonably usable but imperfectly scoped.',
      4: 'Well scoped for the available time.',
      5: 'Very well optimized for the available study time.',
    },
  },
  {
    id: 'structure_schema_quality',
    title: 'Structure / Schema Quality',
    description: 'Measures whether the response conforms to the expected structured format (objectives, breakdown, code examples, analogy, quiz, checklist).',
    supportsNa: false,
    rubric: {
      1: 'Severely malformed.',
      2: 'Multiple structural problems.',
      3: 'Mostly valid but contains notable structural issues.',
      4: 'Valid and well structured.',
      5: 'Fully valid, complete, and consistently structured.',
    },
  },
]

export const SCORE_LABELS = {
  1: 'Poor',
  2: 'Needs Improvement',
  3: 'Acceptable',
  4: 'Good',
  5: 'Excellent',
}
