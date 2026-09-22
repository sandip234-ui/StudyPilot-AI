import { useState, useRef } from 'react'
import { Button } from '../components/ui/Button'
import { Spinner } from '../components/ui/Spinner'
import { Badge } from '../components/ui/Badge'
import { ConceptExplanation } from '../components/session/ConceptExplanation'
import { TopicBreakdown } from '../components/session/TopicBreakdown'
import { Examples } from '../components/session/Examples'
import { Analogy } from '../components/session/Analogy'
import { PracticeQuestions } from '../components/session/PracticeQuestions'
import { Quiz } from '../components/session/Quiz'
import { RevisionChecklist } from '../components/session/RevisionChecklist'
import { runFewShotLab } from '../services/api'

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

function FewShotCard({ result }) {
  const [showPrompt, setShowPrompt] = useState(false)
  const [showDemos, setShowDemos] = useState(false)

  const {
    strategy,
    prompt,
    demonstration_examples,
    techniques,
    purpose,
    response,
    generation_time_ms,
    tokens_used,
    success,
    error,
  } = result

  const isFewShot = strategy === 'few_shot'
  const label = isFewShot ? 'Few-Shot Strategy' : 'Zero-Shot Strategy'
  const icon = isFewShot ? '💡' : '🎯'
  const themeVariant = isFewShot ? 'green' : 'blue'

  const durationSec =
    generation_time_ms !== null && generation_time_ms !== undefined
      ? (generation_time_ms / 1000).toFixed(1)
      : null

  return (
    <div className="bg-white border border-stone-200 rounded-2xl p-5 sm:p-6 shadow-xs flex flex-col justify-between">
      <div>
        {/* Card Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-base">{icon}</span>
              <h3 className="text-lg font-bold text-stone-900">{label}</h3>
            </div>
            <p className="text-xs text-stone-600 mt-1 leading-relaxed">
              {purpose}
            </p>
          </div>
          <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold shrink-0 border ${
              success
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                : 'bg-red-50 text-red-700 border-red-200'
            }`}
          >
            {success ? '✓ Succeeded' : '✗ Failed'}
          </span>
        </div>

        {/* Techniques List */}
        {techniques && techniques.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {techniques.map((t, idx) => (
              <Badge key={idx} variant={themeVariant}>
                {t}
              </Badge>
            ))}
          </div>
        )}

        {/* Performance Metrics */}
        <div className="grid grid-cols-2 gap-2 bg-stone-50 border border-stone-200 rounded-lg p-2.5 mb-4 text-xs">
          <div>
            <span className="text-stone-500 block">Generation Time</span>
            <span className="font-semibold text-stone-800">
              {durationSec ? `${durationSec}s` : 'N/A'}
            </span>
          </div>
          <div>
            <span className="text-stone-500 block">Generated Tokens</span>
            <span className="font-semibold text-stone-800">
              {tokens_used !== null && tokens_used !== undefined
                ? `${tokens_used} tokens`
                : 'N/A'}
            </span>
          </div>
        </div>

        {/* Few-Shot Demonstration Examples Viewer */}
        {isFewShot && demonstration_examples && (
          <div className="mb-3 border border-emerald-200 bg-emerald-50/50 rounded-xl overflow-hidden">
            <button
              type="button"
              onClick={() => setShowDemos((prev) => !prev)}
              className="w-full text-left px-3.5 py-2.5 bg-emerald-100/60 hover:bg-emerald-100/90 flex items-center justify-between text-xs font-semibold text-emerald-950 transition-colors cursor-pointer"
            >
              <span className="flex items-center gap-1.5">
                <span>{showDemos ? '▼' : '▶'}</span> View Demonstration Examples
              </span>
              <span className="text-emerald-700 text-[11px] font-normal">
                Curated example pattern
              </span>
            </button>
            {showDemos && (
              <div className="p-3 bg-emerald-950 text-emerald-100 font-mono text-xs overflow-x-auto whitespace-pre-wrap leading-relaxed">
                {demonstration_examples}
              </div>
            )}
          </div>
        )}

        {/* Collapsible Prompt Viewer */}
        <div className="mb-5 border border-stone-200 rounded-xl overflow-hidden">
          <button
            type="button"
            onClick={() => setShowPrompt((prev) => !prev)}
            className="w-full text-left px-3.5 py-2.5 bg-stone-100/70 hover:bg-stone-100 flex items-center justify-between text-xs font-semibold text-stone-700 transition-colors cursor-pointer"
          >
            <span className="flex items-center gap-1.5">
              <span>{showPrompt ? '▼' : '▶'}</span> View Generated Prompt
            </span>
            <span className="text-stone-500 text-[11px] font-normal">
              {prompt.length} chars
            </span>
          </button>
          {showPrompt && (
            <div className="p-3 bg-stone-900 text-stone-100 font-mono text-xs overflow-x-auto max-h-80 whitespace-pre-wrap leading-relaxed">
              {prompt}
            </div>
          )}
        </div>

        {/* Response Body or Error Panel */}
        {success && response ? (
          <div className="space-y-4 pt-2 border-t border-stone-100">
            {response.title && (
              <h4 className="font-bold text-base text-stone-900">
                {response.title}
              </h4>
            )}

            <ConceptExplanation explanation={response.concept_explanation} />
            <TopicBreakdown breakdown={response.topic_breakdown} />
            <Examples examples={response.examples} />
            <Analogy analogy={response.analogy} />
            <PracticeQuestions questions={response.practice_questions} />
            <Quiz quiz={response.quiz} />
            <RevisionChecklist checklist={response.revision_checklist} />
          </div>
        ) : (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs sm:text-sm">
            <p className="font-semibold mb-1">Execution Failed</p>
            <p className="text-stone-700 leading-relaxed">
              {error || 'The model did not return a valid learning session.'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export function FewShotLabPage() {
  const [topic, setTopic] = useState('Explain recursion in Java')
  const [knowledgeLevel, setKnowledgeLevel] = useState('beginner')
  const [learningGoal, setLearningGoal] = useState('concept_understanding')
  const [availableTime, setAvailableTime] = useState('30_minutes')
  const [explanationStyle, setExplanationStyle] = useState('step_by_step')
  const [difficulty, setDifficulty] = useState('easy')
  const [outputType, setOutputType] = useState('explanation')

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [fewShotResponse, setFewShotResponse] = useState(null)

  const abortControllerRef = useRef(null)

  const isValid = topic.trim().length >= 3 && knowledgeLevel && learningGoal

  const handleRunExperiment = async (e) => {
    if (e) e.preventDefault()
    if (!isValid || loading) return

    const controller = new AbortController()
    abortControllerRef.current = controller

    setLoading(true)
    setError(null)
    setFewShotResponse(null)

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
      const data = await runFewShotLab(payload, controller.signal)
      setFewShotResponse(data)
    } catch (err) {
      if (err.name === 'AbortError' || controller.signal.aborted) {
        setLoading(false)
        return
      }
      setError(err.message || 'Failed to run Few-Shot experiment.')
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
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold mb-3">
          <span>💡</span> In-Context Demonstration Lab
        </div>
        <h1 className="text-3xl font-extrabold text-stone-900 tracking-tight">
          Few-Shot Prompting Experiment
        </h1>
        <p className="text-stone-600 text-sm mt-1 max-w-2xl leading-relaxed">
          Compare Zero-Shot and Few-Shot prompting under identical conditions. Observe how providing curated demonstration examples guides model formatting and structural consistency without modifying system weights.
        </p>
      </div>

      {/* Configuration Form */}
      <div className="bg-white border border-stone-200 rounded-2xl p-6 shadow-xs">
        <h2 className="text-base font-bold text-stone-900 mb-4 pb-2 border-b border-stone-100 flex items-center justify-between">
          <span>Experiment Request Context</span>
          <span className="text-xs font-normal text-stone-500">
            Held identical for Zero-Shot &amp; Few-Shot
          </span>
        </h2>

        <form onSubmit={handleRunExperiment} className="space-y-5">
          {/* Topic */}
          <div>
            <label htmlFor="few-topic" className="block text-xs font-semibold text-stone-800 mb-1">
              Topic <span className="text-red-500">*</span>
            </label>
            <input
              id="few-topic"
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. Explain recursion in Java"
              className="w-full rounded-lg border border-stone-300 p-2.5 text-sm text-stone-900 focus:outline-none focus:ring-2 focus:ring-emerald-500"
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
                        ? 'border-emerald-600 bg-emerald-50 text-emerald-950 font-semibold'
                        : 'border-stone-200 text-stone-700 hover:bg-stone-50'
                    }`}
                  >
                    {lvl.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label htmlFor="few-goal" className="block text-xs font-semibold text-stone-800 mb-1">
                Learning Goal <span className="text-red-500">*</span>
              </label>
              <select
                id="few-goal"
                value={learningGoal}
                onChange={(e) => setLearningGoal(e.target.value)}
                className="w-full rounded-lg border border-stone-300 p-2 text-xs sm:text-sm text-stone-800 focus:outline-none focus:ring-2 focus:ring-emerald-500 cursor-pointer"
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
              <label htmlFor="few-time" className="block text-[11px] font-semibold text-stone-600 mb-1">
                Available Time
              </label>
              <select
                id="few-time"
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
              <label htmlFor="few-style" className="block text-[11px] font-semibold text-stone-600 mb-1">
                Explanation Style
              </label>
              <select
                id="few-style"
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
              <label htmlFor="few-diff" className="block text-[11px] font-semibold text-stone-600 mb-1">
                Difficulty
              </label>
              <select
                id="few-diff"
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
              <label htmlFor="few-out" className="block text-[11px] font-semibold text-stone-600 mb-1">
                Output Type
              </label>
              <select
                id="few-out"
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
              Executes Zero-Shot and Few-Shot sequentially.
            </span>
            <Button
              type="submit"
              size="md"
              disabled={!isValid || loading}
              className="bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 focus:ring-emerald-500 text-white"
            >
              {loading ? 'Running Experiment...' : 'Run Experiment →'}
            </Button>
          </div>
        </form>
      </div>

      {/* Loading Progress State */}
      {loading && (
        <div className="bg-white border border-stone-200 rounded-2xl p-8 text-center shadow-xs flex flex-col items-center">
          <Spinner size="lg" className="text-emerald-600 mb-4" />
          <h3 className="text-lg font-bold text-stone-900 mb-1">
            Running Few-Shot Experiment...
          </h3>
          <p className="text-xs text-stone-600 max-w-md mb-6 leading-relaxed">
            Executing Zero-Shot and Few-Shot sequentially on local model. This takes approximately 30-45 seconds.
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
      {fewShotResponse && !loading && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-stone-100/70 border border-stone-200 rounded-xl p-4">
            <div>
              <h2 className="text-lg font-bold text-stone-900">
                Zero-Shot vs Few-Shot Comparison
              </h2>
              <p className="text-xs text-stone-600 mt-0.5">
                Model: <span className="font-mono font-medium text-stone-800">{fewShotResponse.model_used}</span> &bull; Evaluated with identical task instructions
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

          {/* 2-Column Comparison Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {fewShotResponse.results.map((result) => (
              <FewShotCard key={result.strategy} result={result} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
