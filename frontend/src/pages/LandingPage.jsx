import { Button } from '../components/ui/Button'

export function LandingPage({ topic, onTopicChange, onStartLearning }) {
  const trimmed = topic.trim()
  const charCount = topic.length
  const isValid = trimmed.length >= 3 && charCount <= 500

  const handleKeyDown = (e) => {
    // Ctrl+Enter or Cmd+Enter submits
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault()
      if (isValid) {
        onStartLearning()
      }
    }
    // Plain Enter should just insert newline (default behavior of textarea)
  }

  return (
    <div className="w-full max-w-2xl mx-auto flex flex-col items-center text-center my-auto py-2 sm:py-4">
      {/* Branding */}
      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold mb-3 sm:mb-4 shadow-2xs">
        <span>🎓</span> AI-Powered Personalized Learning
      </div>

      <h1 className="text-2xl sm:text-4xl lg:text-[40px] font-extrabold text-stone-900 tracking-tight leading-tight mb-2 sm:mb-3">
        Learn anything, <br className="hidden sm:inline" />
        <span className="text-blue-600">the way you learn best.</span>
      </h1>

      <p className="text-stone-600 text-sm sm:text-base mb-4 sm:mb-6 max-w-lg leading-relaxed">
        StudyPilot designs an interactive lesson tailored precisely to your background, goals, and study time.
      </p>

      {/* Main Form Box */}
      <div className="w-full bg-white border border-stone-200 rounded-2xl p-4 sm:p-6 shadow-xs text-left">
        <label
          htmlFor="topic-input"
          className="block font-semibold text-stone-900 text-sm sm:text-base mb-1"
        >
          What do you want to learn today?
        </label>

        <p className="text-xs text-stone-500 mb-2.5">
          Enter a concept, question, or skill you want to master.
        </p>

        <div className="relative">
          <textarea
            id="topic-input"
            rows={3}
            value={topic}
            onChange={(e) => onTopicChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="e.g. Explain recursion in Java"
            maxLength={500}
            className="w-full rounded-xl border border-stone-300 p-3 sm:p-3.5 text-stone-900 placeholder:text-stone-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm sm:text-base leading-relaxed transition-all resize-none"
          />

          <div className="flex items-center justify-between mt-1.5 px-1">
            <span
              className={`text-[11px] sm:text-xs ${
                charCount > 0 && trimmed.length < 3
                  ? 'text-amber-700 font-medium'
                  : charCount > 480
                  ? 'text-red-700'
                  : 'text-stone-500'
              }`}
            >
              {charCount > 0 && trimmed.length < 3
                ? 'Minimum 3 characters required'
                : 'Press Ctrl+Enter or Cmd+Enter to start'}
            </span>
            <span
              className={`text-[11px] sm:text-xs font-mono ${
                charCount > 500 ? 'text-red-600 font-bold' : 'text-stone-500'
              }`}
            >
              {charCount}/500
            </span>
          </div>
        </div>

        <div className="mt-4 sm:mt-5 flex justify-end">
          <Button
            size="md"
            disabled={!isValid}
            onClick={onStartLearning}
            className="w-full sm:w-auto"
          >
            Start Learning &rarr;
          </Button>
        </div>
      </div>
    </div>
  )
}
