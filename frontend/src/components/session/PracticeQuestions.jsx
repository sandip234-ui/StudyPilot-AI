
export function PracticeQuestions({ questions }) {
  if (!questions || !Array.isArray(questions) || questions.length === 0) {
    return null
  }

  return (
    <section className="bg-white border border-stone-200 rounded-xl p-6 sm:p-7 mb-8 shadow-xs">
      <h2 className="text-xl font-bold text-stone-900 mb-4 pb-2 border-b border-stone-100 flex items-center gap-2">
        <span className="text-blue-600 font-normal text-lg">✏️</span>
        Practice Questions
      </h2>
      <ol className="space-y-3.5 list-none">
        {questions.map((q, idx) => (
          <li key={idx} className="flex items-start gap-3 text-sm sm:text-base text-stone-800">
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-stone-100 text-stone-700 text-xs font-semibold shrink-0 mt-0.5 border border-stone-200">
              {idx + 1}
            </span>
            <span className="leading-relaxed">{q}</span>
          </li>
        ))}
      </ol>
    </section>
  )
}
