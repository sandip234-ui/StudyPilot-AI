import { Badge } from '../ui/Badge'

const LABEL_MAP = {
  knowledge_level: {
    beginner: 'Beginner',
    intermediate: 'Intermediate',
    advanced: 'Advanced',
  },
  learning_goal: {
    concept_understanding: 'Concept Understanding',
    exam_preparation: 'Exam Preparation',
    interview_preparation: 'Interview Preparation',
    assignment: 'Assignment',
    practice: 'Practice',
  },
  available_time: {
    '15_minutes': '15 minutes',
    '30_minutes': '30 minutes',
    '1_hour': '1 hour',
    '2_plus_hours': '2+ hours',
  },
  explanation_style: {
    simple: 'Simple',
    step_by_step: 'Step-by-step',
    example_based: 'Example-based',
    analogy_based: 'Analogy-based',
    detailed: 'Detailed',
  },
  difficulty: {
    easy: 'Easy',
    medium: 'Medium',
    hard: 'Hard',
  },
  output_type: {
    explanation: 'Explanation',
    study_notes: 'Study Notes',
    practice_questions: 'Practice Questions',
    quiz: 'Quiz',
    complete_learning_session: 'Complete Session',
  },
}

export function SessionHeader({ title, contextUsed, modelUsed }) {
  const badges = []

  if (contextUsed) {
    if (contextUsed.knowledge_level && LABEL_MAP.knowledge_level[contextUsed.knowledge_level]) {
      badges.push({
        label: LABEL_MAP.knowledge_level[contextUsed.knowledge_level],
        variant: 'blue',
      })
    }
    if (contextUsed.learning_goal && LABEL_MAP.learning_goal[contextUsed.learning_goal]) {
      badges.push({
        label: LABEL_MAP.learning_goal[contextUsed.learning_goal],
        variant: 'purple',
      })
    }
    if (contextUsed.available_time && LABEL_MAP.available_time[contextUsed.available_time]) {
      badges.push({
        label: LABEL_MAP.available_time[contextUsed.available_time],
        variant: 'amber',
      })
    }
    if (contextUsed.explanation_style && LABEL_MAP.explanation_style[contextUsed.explanation_style]) {
      badges.push({
        label: LABEL_MAP.explanation_style[contextUsed.explanation_style],
        variant: 'green',
      })
    }
    if (contextUsed.difficulty && LABEL_MAP.difficulty[contextUsed.difficulty]) {
      badges.push({
        label: `Difficulty: ${LABEL_MAP.difficulty[contextUsed.difficulty]}`,
        variant: 'neutral',
      })
    }
    if (contextUsed.output_type && LABEL_MAP.output_type[contextUsed.output_type]) {
      badges.push({
        label: LABEL_MAP.output_type[contextUsed.output_type],
        variant: 'neutral',
      })
    }
  }

  return (
    <header className="border-b border-stone-200 pb-6 mb-8">
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-stone-900 tracking-tight">
            {title}
          </h1>
          {badges.length > 0 && (
            <div className="flex flex-wrap items-center gap-2 mt-3">
              {badges.map((b, idx) => (
                <Badge key={idx} variant={b.variant}>
                  {b.label}
                </Badge>
              ))}
            </div>
          )}
        </div>
        {modelUsed && (
          <div className="text-xs text-stone-600 bg-stone-100 px-2.5 py-1 rounded-md self-start border border-stone-200 font-mono">
            Powered by {modelUsed}
          </div>
        )}
      </div>
    </header>
  )
}
