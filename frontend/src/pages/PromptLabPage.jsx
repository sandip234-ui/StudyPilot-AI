import { useState, useRef } from 'react'
import { Button } from '../components/ui/Button'
import { Spinner } from '../components/ui/Spinner'
import { StrategyCard } from '../components/lab/StrategyCard'
import { runPromptLab } from '../services/api'

const KNOWLEDGE_LEVELS = [
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' },
]

const LEARNING_GOALS = [
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

export function PromptLabPage() {
  const [topic, setTopic] = useState('Explain recursion in Java')
  const [knowledgeLevel, setKnowledgeLevel] = useState('beginner')
  const [learningGoal, setLearningGoal] = useState('concept_understanding')
  const [availableTime, setAvailableTime] = useState('30_minutes')
  const [explanationStyle, setExplanationStyle] = useState('step_by_step')
  const [difficulty, setDifficulty] = useState('easy')
  const [outputType, setOutputType] = useState('explanation')

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [labResponse, setLabResponse] = useState(null)

  const abortControllerRef = useRef(null)

  const isValid = topic.trim().length >= 3 && knowledgeLevel && learningGoal

  const handleRunExperiment = async (e) => {
    if (e) e.preventDefault()
    if (!isValid || loading) return

    const controller = new AbortController()
    abortControllerRef.current = controller

    setLoading(true)
    setError(null)
    setLabResponse(null)

    const payload = {
      topic: topic.trim(),
      knowledge_level: knowledgeLevel,
      learning_goal: learningGoal,
      available_time: availableTime || null,
      explanation_style: explanationStyle || null,
      difficulty: difficulty || null,
      output_type: outputType || null,
    }

    try {
      const data = await runPromptLab(payload, controller.signal)
      setLabResponse(data)
    } catch (err) {
      if (err.name === 'AbortError' || controller.signal.aborted) {
        // Cancelled intentionally
        setLoading(false)
        return
      }
      setError(err.message || 'Failed to run Prompt Engineering Lab experiment.')
    } finally {
      setLoading(false)
      if (abortControllerRef.current === controller) {
        abortControllerRef.current = null
      }
    }
  }

  const handleCancel = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    setLoading(false)
  }

  return (
    <div className="space-y-10">
      {/* Header Banner */}
      <div className="border-b border-stone-200 pb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-50 border border-purple-200 text-purple-700 text-xs font-semibold mb-3">
          <span>🔬</span> Experimental Evaluation Suite
        </div>
        <h1 className="text-3xl font-extrabold text-stone-900 tracking-tight">
          Prompt Engineering Lab
        </h1>
        <p className="text-stone-600 text-sm mt-1 max-w-2xl leading-relaxed">
          Compare the four core prompt engineering strategies side-by-side using the exact same student request context. Observe how instruction structure, role assignment, and context injection shape local LLM reasoning.
        </p>
      </div>

      {/* Experiment Configuration Form */}
      <div className="bg-white border border-stone-200 rounded-2xl p-6 shadow-xs">
        <h2 className="text-base font-bold text-stone-900 mb-4 pb-2 border-b border-stone-100 flex items-center justify-between">
          <span>Experiment Request Context</span>
          <span className="text-xs font-normal text-stone-500">Held constant across all 4 strategies</span>
        </h2>

        <form onSubmit={handleRunExperiment} className="space-y-5">
          {/* Topic */}
          <div>
            <label htmlFor="lab-topic" className="block text-xs font-semibold text-stone-800 mb-1">
              Topic <span className="text-red-500">*</span>
            </label>
            <input
              id="lab-topic"
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. Explain recursion in Java"
              className="w-full rounded-lg border border-stone-300 p-2.5 text-sm text-stone-900 focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          {/* Required Fields */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-stone-800 mb-1">
                Knowledge Level <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-3 gap-2">
                {KNOWLEDGE_LEVELS.map((lvl) => (
                  <button
                    key={lvl.value}
                    type="button"
                    onClick={() => setKnowledgeLevel(lvl.value)}
                    className={`py-2 px-1 text-xs rounded-lg border font-medium text-center transition-colors cursor-pointer ${
                      knowledgeLevel === lvl.value
                        ? 'border-purple-600 bg-purple-50 text-purple-900 font-semibold'
                        : 'border-stone-200 text-stone-700 hover:bg-stone-50'
                    }`}
                  >
                    {lvl.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label htmlFor="lab-goal" className="block text-xs font-semibold text-stone-800 mb-1">
                Learning Goal <span className="text-red-500">*</span>
              </label>
              <select
                id="lab-goal"
                value={learningGoal}
                onChange={(e) => setLearningGoal(e.target.value)}
                className="w-full rounded-lg border border-stone-300 p-2 text-xs sm:text-sm text-stone-800 focus:outline-none focus:ring-2 focus:ring-purple-500 cursor-pointer"
              >
                {LEARNING_GOALS.map((g) => (
                  <option key={g.value} value={g.value}>
                    {g.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Optional Fields */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 border-t border-stone-100">
            <div>
              <label htmlFor="lab-time" className="block text-[11px] font-semibold text-stone-600 mb-1">
                Available Time
              </label>
              <select
                id="lab-time"
                value={availableTime}
                onChange={(e) => setAvailableTime(e.target.value)}
                className="w-full rounded-md border border-stone-300 p-1.5 text-xs text-stone-800"
              >
                {AVAILABLE_TIMES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="lab-style" className="block text-[11px] font-semibold text-stone-600 mb-1">
                Explanation Style
              </label>
              <select
                id="lab-style"
                value={explanationStyle}
                onChange={(e) => setExplanationStyle(e.target.value)}
                className="w-full rounded-md border border-stone-300 p-1.5 text-xs text-stone-800"
              >
                {EXPLANATION_STYLES.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="lab-diff" className="block text-[11px] font-semibold text-stone-600 mb-1">
                Difficulty
              </label>
              <select
                id="lab-diff"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="w-full rounded-md border border-stone-300 p-1.5 text-xs text-stone-800"
              >
                {DIFFICULTIES.map((d) => (
                  <option key={d.value} value={d.value}>
                    {d.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="lab-out" className="block text-[11px] font-semibold text-stone-600 mb-1">
                Output Type
              </label>
              <select
                id="lab-out"
                value={outputType}
                onChange={(e) => setOutputType(e.target.value)}
                className="w-full rounded-md border border-stone-300 p-1.5 text-xs text-stone-800"
              >
                {OUTPUT_TYPES.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Action CTA */}
          <div className="flex items-center justify-between pt-3">
            <span className="text-xs text-stone-500">
              Executes Baseline, Role, Personalized, and Structured sequentially.
            </span>
            <Button
              type="submit"
              size="md"
              disabled={!isValid || loading}
              className="bg-purple-600 hover:bg-purple-700 active:bg-purple-800 focus:ring-purple-500"
            >
              {loading ? 'Running Experiment...' : 'Run Experiment →'}
            </Button>
          </div>
        </form>
      </div>

      {/* Loading Progress State */}
      {loading && (
        <div className="bg-white border border-stone-200 rounded-2xl p-8 text-center shadow-xs flex flex-col items-center">
          <Spinner size="lg" className="text-purple-600 mb-4" />
          <h3 className="text-lg font-bold text-stone-900 mb-1">
            Running Prompt Engineering Experiment...
          </h3>
          <p className="text-xs text-stone-600 max-w-md mb-6 leading-relaxed">
            Executing all 4 strategies sequentially on local model to preserve memory. This takes approximately 1-2 minutes on local hardware.
          </p>
          <Button variant="outline" size="sm" onClick={handleCancel}>
            Cancel Experiment
          </Button>
        </div>
      )}

      {/* Global Error State */}
      {error && !loading && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-sm flex items-center justify-between">
          <span>{error}</span>
          <Button size="sm" variant="outline" onClick={() => setError(null)}>
            Dismiss
          </Button>
        </div>
      )}

      {/* Experiment Results */}
      {labResponse && !loading && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-stone-100/70 border border-stone-200 rounded-xl p-4">
            <div>
              <h2 className="text-lg font-bold text-stone-900">
                Comparative Results
              </h2>
              <p className="text-xs text-stone-600 mt-0.5">
                Model: <span className="font-mono font-medium text-stone-800">{labResponse.model_used}</span> &bull; Evaluated on identical context
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleRunExperiment}
              >
                Re-run Experiment
              </Button>
            </div>
          </div>

          {/* 4 Strategy Cards Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {labResponse.results.map((result) => (
              <StrategyCard key={result.strategy} result={result} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
