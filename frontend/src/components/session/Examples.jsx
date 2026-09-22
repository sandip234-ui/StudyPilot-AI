
export function Examples({ examples }) {
  if (!examples || !Array.isArray(examples) || examples.length === 0) {
    return null
  }

  return (
    <section className="mb-8">
      <h2 className="text-xl font-bold text-stone-900 mb-4 flex items-center gap-2">
        <span className="text-blue-600 font-normal text-lg">💻</span>
        Examples
      </h2>
      <div className="space-y-5">
        {examples.map((eg, idx) => (
          <div
            key={idx}
            className="bg-white border border-stone-200 rounded-xl overflow-hidden shadow-xs"
          >
            <div className="px-5 py-3.5 bg-stone-50 border-b border-stone-200">
              <h3 className="font-semibold text-stone-900 text-sm sm:text-base">
                {eg.title}
              </h3>
            </div>
            {eg.code && (
              <div className="p-4 bg-stone-900 overflow-x-auto">
                <pre className="font-mono text-xs sm:text-sm text-stone-100 leading-relaxed">
                  <code>{eg.code}</code>
                </pre>
              </div>
            )}
            <div className="p-5">
              <p className="text-sm text-stone-700 leading-relaxed whitespace-pre-line">
                {eg.explanation}
              </p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
