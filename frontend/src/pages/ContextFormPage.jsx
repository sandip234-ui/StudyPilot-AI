import { Button } from '../components/ui/Button'

const KNOWLEDGE_LEVELS = [
  { value: 'beginner', label: 'Beginner', desc: 'New to this subject' },
  { value: 'intermediate', label: 'Intermediate', desc: 'Have fundamentals down' },
  { value: 'advanced', label: 'Advanced', desc: 'Seeking deep mastery' },
]

const LEARNING_GOALS = [
  { value: '', label: 'Select your learning goal...' },
  { value: 'concept_understanding', label: 'Concept Understanding' },
  { value: 'exam_preparation', label: 'Exam Preparation' },
  { value: 'interview_preparation', label: 'Interview Preparation' },
  { value: 'assignment', label: 'Assignment' },
  { value: 'practice', label: 'Practice' },
]

const AVAILABLE_TIMES = [
  { value: '', label: 'Not specified' },
  { value: '15_minutes', label: '15 minutes' },
  { value: '30_minutes', label: '30 minutes' },
  { value: '1_hour', label: '1 hour' },
  { value: '2_plus_hours', label: '2+ hours' },
]

const EXPLANATION_STYLES = [
  { value: '', label: 'Not specified' },
  { value: 'simple', label: 'Simple' },
  { value: 'step_by_step', label: 'Step-by-step' },
  { value: 'example_based', label: 'Example-based' },
  { value: 'analogy_based', label: 'Analogy-based' },
  { value: 'detailed', label: 'Detailed' },
]

const DIFFICULTIES = [
  { value: '', label: 'Not specified' },
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
]

const OUTPUT_TYPES = [
  { value: '', label: 'Not specified' },
  { value: 'explanation', label: 'Explanation' },
  { value: 'study_notes', label: 'Study Notes' },
  { value: 'practice_questions', label: 'Practice Questions' },
  { value: 'quiz', label: 'Quiz' },
  { value: 'complete_learning_session', label: 'Complete Learning Session' },
]

export function ContextFormPage({
  topic,
  formData,
  onFormChange,
  onEditTopic,
  onGenerate,
}) {
  const isRequiredFilled =
    Boolean(formData.knowledge_level) && Boolean(formData.learning_goal)

  const handleKnowledgeLevelSelect = (level) => {
    onFormChange({
      ...formData,
      knowledge_level: level,
    })
  }

  const handleSelectChange = (field, value) => {
    onFormChange({
      ...formData,
      [field]: value === '' ? null : value,
    })
  }

  return (
    <div className="max-w-2xl mx-auto py-2 sm:py-6">
      {/* Topic Card with Edit Option */}
      <div className="bg-blue-50/70 border border-blue-200/80 rounded-xl p-4 sm:p-5 mb-8 flex items-start justify-between gap-4">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-blue-800 block mb-1">
            Learning Topic
          </span>
          <p className="text-base sm:text-lg font-semibold text-blue-950 leading-snug">
            {topic}
          </p>
        </div>
        <button
          type="button"
          onClick={onEditTopic}
          className="text-xs font-medium text-blue-700 hover:text-blue-900 bg-white hover:bg-blue-50 border border-blue-300 rounded-md px-2.5 py-1.5 transition-colors shrink-0 cursor-pointer"
        >
          Edit Topic
        </button>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault()
          if (isRequiredFilled) onGenerate()
        }}
        className="space-y-8"
      >
        {/* Required Section */}
        <div className="bg-white border border-stone-200 rounded-xl p-5 sm:p-7 shadow-xs space-y-6">
          <h2 className="text-lg font-bold text-stone-900 pb-3 border-b border-stone-100 flex items-center justify-between">
            <span>Learning Context</span>
            <span className="text-xs font-normal text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
              Required
            </span>
          </h2>

          {/* Knowledge Level Pills */}
          <div>
            <label className="block text-sm font-semibold text-stone-900 mb-1">
              Your Knowledge Level <span className="text-red-500">*</span>
            </label>
            <p className="text-xs text-stone-700 mb-3">
              How familiar are you with this topic?
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
              {KNOWLEDGE_LEVELS.map((lvl) => {
                const isSelected = formData.knowledge_level === lvl.value
                return (
                  <button
                    key={lvl.value}
                    type="button"
                    onClick={() => handleKnowledgeLevelSelect(lvl.value)}
                    className={`p-3 rounded-lg border text-left transition-all cursor-pointer ${
                      isSelected
                        ? 'border-blue-600 bg-blue-50/80 text-blue-950 ring-1 ring-blue-600'
                        : 'border-stone-200 bg-white text-stone-800 hover:border-stone-300 hover:bg-stone-50'
                    }`}
                  >
                    <div className="font-semibold text-sm">{lvl.label}</div>
                    <div className="text-xs text-stone-600 mt-0.5">{lvl.desc}</div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Learning Goal Dropdown */}
          <div>
            <label
              htmlFor="learning-goal-select"
              className="block text-sm font-semibold text-stone-900 mb-1"
            >
              Learning Goal <span className="text-red-500">*</span>
            </label>
            <p className="text-xs text-stone-700 mb-2">
              What outcome are you working toward?
            </p>
            <select
              id="learning-goal-select"
              value={formData.learning_goal || ''}
              onChange={(e) => handleSelectChange('learning_goal', e.target.value)}
              className="w-full rounded-lg border border-stone-300 bg-white p-2.5 text-stone-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 cursor-pointer"
            >
              {LEARNING_GOALS.map((g) => (
                <option key={g.value} value={g.value} disabled={g.value === ''}>
                  {g.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Optional Section */}
        <div className="bg-white border border-stone-200 rounded-xl p-5 sm:p-7 shadow-xs space-y-5">
          <div className="pb-3 border-b border-stone-100 flex items-center justify-between">
            <h2 className="text-base font-bold text-stone-900">
              Personalize further (optional)
            </h2>
            <span className="text-xs text-stone-600">All optional</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-5">
            {/* Available Study Time */}
            <div>
              <label
                htmlFor="available-time-select"
                className="block text-xs font-semibold text-stone-800 mb-1"
              >
                Available Study Time
              </label>
              <select
                id="available-time-select"
                value={formData.available_time || ''}
                onChange={(e) => handleSelectChange('available_time', e.target.value)}
                className="w-full rounded-lg border border-stone-300 bg-white p-2 text-stone-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
              >
                {AVAILABLE_TIMES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Explanation Style */}
            <div>
              <label
                htmlFor="explanation-style-select"
                className="block text-xs font-semibold text-stone-800 mb-1"
              >
                Explanation Style
              </label>
              <select
                id="explanation-style-select"
                value={formData.explanation_style || ''}
                onChange={(e) => handleSelectChange('explanation_style', e.target.value)}
                className="w-full rounded-lg border border-stone-300 bg-white p-2 text-stone-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
              >
                {EXPLANATION_STYLES.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Difficulty */}
            <div>
              <label
                htmlFor="difficulty-select"
                className="block text-xs font-semibold text-stone-800 mb-1"
              >
                Difficulty
              </label>
              <select
                id="difficulty-select"
                value={formData.difficulty || ''}
                onChange={(e) => handleSelectChange('difficulty', e.target.value)}
                className="w-full rounded-lg border border-stone-300 bg-white p-2 text-stone-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
              >
                {DIFFICULTIES.map((d) => (
                  <option key={d.value} value={d.value}>
                    {d.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Output Type */}
            <div>
              <label
                htmlFor="output-type-select"
                className="block text-xs font-semibold text-stone-800 mb-1"
              >
                Output Type
              </label>
              <select
                id="output-type-select"
                value={formData.output_type || ''}
                onChange={(e) => handleSelectChange('output_type', e.target.value)}
                className="w-full rounded-lg border border-stone-300 bg-white p-2 text-stone-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
              >
                {OUTPUT_TYPES.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Generate Button */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
          <button
            type="button"
            onClick={onEditTopic}
            className="text-sm text-stone-700 hover:text-stone-900 cursor-pointer"
          >
            &larr; Back to Topic
          </button>
          <Button
            type="submit"
            size="lg"
            disabled={!isRequiredFilled}
            className="w-full sm:w-auto"
          >
            Generate Learning Session &rarr;
          </Button>
        </div>
      </form>
    </div>
  )
}
