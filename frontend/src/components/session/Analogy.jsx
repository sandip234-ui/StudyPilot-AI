
export function Analogy({ analogy }) {
  if (!analogy || typeof analogy !== 'string' || !analogy.trim()) {
    return null
  }

  return (
    <aside className="bg-amber-50/80 border border-amber-200/80 rounded-xl p-6 sm:p-7 mb-8 shadow-xs">
      <div className="flex items-start gap-3">
        <span className="text-2xl select-none" role="img" aria-label="Lightbulb">
          💡
        </span>
        <div>
          <h2 className="text-base font-bold text-amber-950 mb-2">
            Think of it like...
          </h2>
          <p className="text-sm sm:text-base text-amber-900 leading-relaxed whitespace-pre-line">
            {analogy}
          </p>
        </div>
      </div>
    </aside>
  )
}
