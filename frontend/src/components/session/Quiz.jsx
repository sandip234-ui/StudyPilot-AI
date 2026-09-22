import { useState } from 'react'
import { Button } from '../ui/Button'

export function Quiz({ quiz }) {
  // State: { [qIdx]: { selected: number | null, checked: boolean } }
  const [quizState, setQuizState] = useState({})

  if (!quiz || !Array.isArray(quiz) || quiz.length === 0) {
    return null
  }

  const handleSelectOption = (qIdx, optIdx) => {
    const current = quizState[qIdx]
    if (current?.checked) return // locked once checked

    setQuizState((prev) => ({
      ...prev,
      [qIdx]: {
        selected: optIdx,
        checked: false,
      },
    }))
  }

  const handleCheckAnswer = (qIdx) => {
    const current = quizState[qIdx]
    if (!current || current.selected === null || current.checked) return

    setQuizState((prev) => ({
      ...prev,
      [qIdx]: {
        ...prev[qIdx],
        checked: true,
      },
    }))
  }

  const handleResetQuestion = (qIdx) => {
    setQuizState((prev) => ({
      ...prev,
      [qIdx]: {
        selected: null,
        checked: false,
      },
    }))
  }

  return (
    <section className="bg-white border border-stone-200 rounded-xl p-6 sm:p-8 mb-8 shadow-xs">
      <h2 className="text-xl font-bold text-stone-900 mb-6 pb-2 border-b border-stone-100 flex items-center gap-2">
        <span className="text-blue-600 font-normal text-lg">💡</span>
        Knowledge Check
      </h2>

      <div className="space-y-8">
        {quiz.map((q, qIdx) => {
          const state = quizState[qIdx] || { selected: null, checked: false }
          const isSelected = state.selected !== null
          const isChecked = state.checked
          const isCorrect = isChecked && state.selected === q.correct_index

          return (
            <div
              key={qIdx}
              className="p-5 rounded-xl border border-stone-200 bg-stone-50/50"
            >
              <p className="font-medium text-stone-900 mb-4 text-base">
                <span className="font-semibold text-stone-600 mr-2">Q{qIdx + 1}.</span>
                {q.question}
              </p>

              <div className="space-y-2.5 mb-4">
                {q.options.map((opt, optIdx) => {
                  let buttonStyle =
                    'border-stone-200 bg-white text-stone-800 hover:border-stone-300 hover:bg-stone-50'

                  if (isChecked) {
                    if (optIdx === q.correct_index) {
                      // Correct option
                      buttonStyle =
                        'border-emerald-500 bg-emerald-50 text-emerald-900 font-medium'
                    } else if (optIdx === state.selected) {
                      // Incorrectly selected option
                      buttonStyle =
                        'border-red-400 bg-red-50 text-red-900 line-through'
                    } else {
                      buttonStyle = 'border-stone-200 bg-white/60 text-stone-600 opacity-60'
                    }
                  } else if (state.selected === optIdx) {
                    buttonStyle =
                      'border-blue-500 bg-blue-50 text-blue-900 font-medium ring-1 ring-blue-500'
                  }

                  const displayOpt =
                    typeof opt === 'string'
                      ? opt.replace(/^[A-Da-d][.:)\-\s]+/, '')
                      : opt

                  return (
                    <button
                      key={optIdx}
                      type="button"
                      onClick={() => handleSelectOption(qIdx, optIdx)}
                      disabled={isChecked}
                      className={`w-full text-left p-3.5 rounded-lg border text-sm transition-all flex items-start gap-3 cursor-pointer disabled:cursor-default ${buttonStyle}`}
                    >
                      <span className="w-5 h-5 rounded-full border border-stone-300 flex items-center justify-center text-xs shrink-0 font-mono mt-0.5">
                        {String.fromCharCode(65 + optIdx)}
                      </span>
                      <span className="flex-1 leading-snug">{displayOpt}</span>
                    </button>
                  )
                })}
              </div>

              <div className="flex items-center gap-3">
                {!isChecked ? (
                  <Button
                    size="sm"
                    disabled={!isSelected}
                    onClick={() => handleCheckAnswer(qIdx)}
                  >
                    Check Answer
                  </Button>
                ) : (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleResetQuestion(qIdx)}
                  >
                    Retry Question
                  </Button>
                )}
              </div>

              {isChecked && (
                <div
                  className={`mt-4 p-4 rounded-lg text-sm leading-relaxed border ${
                    isCorrect
                      ? 'bg-emerald-50/70 border-emerald-200 text-emerald-900'
                      : 'bg-stone-100 border-stone-300 text-stone-800'
                  }`}
                >
                  <p className="font-semibold mb-1 flex items-center gap-1.5">
                    {isCorrect ? (
                      <>
                        <span className="text-emerald-600 font-bold">✓</span> Correct!
                      </>
                    ) : (
                      <>
                        <span className="text-red-500 font-bold">✗</span> Not quite right.
                      </>
                    )}
                  </p>
                  {q.explanation && (
                    <p className="text-xs sm:text-sm mt-1">{q.explanation}</p>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </section>
  )
}
