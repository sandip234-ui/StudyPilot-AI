import { Spinner } from '../components/ui/Spinner'
import { Button } from '../components/ui/Button'

export function GeneratingPage({ topic, onCancel }) {
  return (
    <div className="max-w-xl mx-auto text-center py-12 sm:py-20">
      <div className="bg-white border border-stone-200 rounded-2xl p-8 sm:p-12 shadow-sm flex flex-col items-center">
        {/* Subtle animated spinner */}
        <div className="mb-6">
          <Spinner size="lg" />
        </div>

        <span className="text-xs font-semibold uppercase tracking-wider text-blue-700 bg-blue-50 px-3 py-1 rounded-full border border-blue-100 mb-3">
          StudyPilot
        </span>

        <h1 className="text-2xl sm:text-3xl font-bold text-stone-900 mb-3 tracking-tight">
          Preparing your personalized learning session...
        </h1>

        <div className="bg-stone-50 border border-stone-200 rounded-xl p-4 my-6 w-full text-left">
          <span className="text-xs font-semibold text-stone-600 block mb-1">
            Topic:
          </span>
          <p className="text-base font-medium text-stone-900 leading-snug">
            &ldquo;{topic}&rdquo;
          </p>
        </div>

        <p className="text-sm text-stone-700 mb-8 max-w-md leading-relaxed">
          This may take a little while while the local AI model generates your lesson.
        </p>

        <Button
          variant="outline"
          size="md"
          onClick={onCancel}
          className="text-stone-700 hover:text-stone-900"
        >
          Cancel
        </Button>
      </div>
    </div>
  )
}
