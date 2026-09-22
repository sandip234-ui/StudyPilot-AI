
export function TopicBreakdown({ breakdown }) {
  if (!breakdown || !Array.isArray(breakdown) || breakdown.length === 0) {
    return null
  }

  return (
    <section className="mb-8">
      <h2 className="text-xl font-bold text-stone-900 mb-4 flex items-center gap-2">
        <span className="text-blue-600 font-normal text-lg">📑</span>
        Topic Breakdown
      </h2>
      <div className="grid grid-cols-1 gap-4">
        {breakdown.map((item, idx) => (
          <div
            key={idx}
            className="bg-white border border-stone-200 rounded-xl p-5 shadow-xs hover:border-stone-300 transition-colors"
          >
            <h3 className="text-base font-semibold text-stone-900 mb-2">
              {item.heading}
            </h3>
            <p className="text-sm text-stone-700 leading-relaxed whitespace-pre-line">
              {item.content}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}
