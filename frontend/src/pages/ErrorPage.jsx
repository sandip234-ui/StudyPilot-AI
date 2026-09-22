import { Button } from '../components/ui/Button'

export function ErrorPage({ errorMessage, onTryAgain, onStartOver }) {
  return (
    <div className="max-w-lg mx-auto py-12 sm:py-16 text-center">
      <div className="bg-white border border-stone-200 rounded-2xl p-8 sm:p-10 shadow-sm">
        <div className="w-14 h-14 rounded-full bg-red-50 text-red-600 border border-red-200 flex items-center justify-center mx-auto mb-5 text-2xl">
          ⚠️
        </div>

        <h1 className="text-xl sm:text-2xl font-bold text-stone-900 mb-3 tracking-tight">
          Session Generation Error
        </h1>

        <p className="text-sm sm:text-base text-stone-700 leading-relaxed mb-8">
          {errorMessage || 'Something went wrong while creating your learning session.'}
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Button
            variant="primary"
            onClick={onTryAgain}
            className="w-full sm:w-auto"
          >
            Try Again
          </Button>
          <Button
            variant="outline"
            onClick={onStartOver}
            className="w-full sm:w-auto"
          >
            Start Over
          </Button>
        </div>
      </div>
    </div>
  )
}
