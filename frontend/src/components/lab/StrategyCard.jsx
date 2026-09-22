import { useState } from 'react'
import { Badge } from '../ui/Badge'
import { ConceptExplanation } from '../session/ConceptExplanation'
import { TopicBreakdown } from '../session/TopicBreakdown'
import { Examples } from '../session/Examples'
import { Analogy } from '../session/Analogy'
import { PracticeQuestions } from '../session/PracticeQuestions'
import { Quiz } from '../session/Quiz'
import { RevisionChecklist } from '../session/RevisionChecklist'

const STRATEGY_THEMES = {
  baseline: {
    badgeVariant: 'neutral',
    label: 'Baseline Strategy',
    icon: '⚪',
  },
  role: {
    badgeVariant: 'blue',
    label: 'Role Strategy',
    icon: '👤',
  },
  personalized: {
    badgeVariant: 'amber',
    label: 'Personalized Strategy',
    icon: '🎯',
  },
  structured: {
    badgeVariant: 'purple',
    label: 'Structured Strategy',
    icon: '📑',
  },
}

export function StrategyCard({ result }) {
  const [showPrompt, setShowPrompt] = useState(false)

  const {
    strategy,
    prompt,
    techniques,
    purpose,
    response,
    generation_time_ms,
    tokens_used,
    success,
    error,
  } = result

  const theme = STRATEGY_THEMES[strategy] || {
    badgeVariant: 'neutral',
    label: strategy,
    icon: '🔬',
  }

  const durationSec =
    generation_time_ms !== null && generation_time_ms !== undefined
      ? (generation_time_ms / 1000).toFixed(1)
      : null

  return (
    <div className="bg-white border border-stone-200 rounded-2xl p-5 sm:p-6 shadow-xs flex flex-col justify-between">
      <div>
        {/* Strategy Title & Badges */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-base">{theme.icon}</span>
              <h3 className="text-lg font-bold text-stone-900 capitalize">
                {theme.label}
              </h3>
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
              <Badge key={idx} variant={theme.badgeVariant}>
                {t}
              </Badge>
            ))}
          </div>
        )}

        {/* Factual Performance Metrics */}
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

        {/* Collapsible Generated Prompt Box */}
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

            {/* Concept Explanation */}
            <ConceptExplanation explanation={response.concept_explanation} />

            {/* Topic Breakdown */}
            <TopicBreakdown breakdown={response.topic_breakdown} />

            {/* Examples */}
            <Examples examples={response.examples} />

            {/* Analogy */}
            <Analogy analogy={response.analogy} />

            {/* Practice Questions */}
            <PracticeQuestions questions={response.practice_questions} />

            {/* Quiz */}
            <Quiz quiz={response.quiz} />

            {/* Revision Checklist */}
            <RevisionChecklist checklist={response.revision_checklist} />
          </div>
        ) : (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs sm:text-sm">
            <p className="font-semibold mb-1">Strategy Execution Failed</p>
            <p className="text-stone-700 leading-relaxed">
              {error || 'The model did not return a valid learning session for this strategy.'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
