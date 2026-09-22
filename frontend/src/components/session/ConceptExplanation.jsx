
/**
 * Safely renders markdown-like paragraphs and bullet points without dangerouslySetInnerHTML.
 */
function renderSafeFormattedText(text) {
  if (!text) return null

  // Split into blocks by double newlines
  const blocks = text.split(/\n{2,}/)

  return blocks.map((block, bIdx) => {
    const trimmed = block.trim()
    if (!trimmed) return null

    // Check if it's a heading: ### or ##
    if (trimmed.startsWith('### ')) {
      return (
        <h3 key={bIdx} className="text-lg font-semibold text-stone-900 mt-4 mb-2">
          {trimmed.replace(/^###\s+/, '')}
        </h3>
      )
    }
    if (trimmed.startsWith('## ')) {
      return (
        <h2 key={bIdx} className="text-xl font-bold text-stone-900 mt-5 mb-2">
          {trimmed.replace(/^##\s+/, '')}
        </h2>
      )
    }

    // Check if block contains list items (lines starting with * or - or number.)
    const lines = trimmed.split('\n')
    const isBulletList = lines.every((line) => /^(\*|-|\d+\.)\s/.test(line.trim()))

    if (isBulletList) {
      return (
        <ul key={bIdx} className="list-disc pl-5 space-y-1 my-3 text-stone-700 leading-relaxed">
          {lines.map((line, lIdx) => (
            <li key={lIdx}>
              {line.replace(/^(\*|-|\d+\.)\s+/, '')}
            </li>
          ))}
        </ul>
      )
    }

    // Normal paragraph with preserved line breaks if any
    return (
      <p key={bIdx} className="text-stone-700 leading-relaxed my-3 whitespace-pre-line text-base">
        {trimmed}
      </p>
    )
  })
}

export function ConceptExplanation({ explanation }) {
  if (!explanation) return null

  return (
    <section className="bg-white border border-stone-200 rounded-xl p-6 sm:p-8 mb-8 shadow-xs">
      <h2 className="text-xl font-bold text-stone-900 mb-4 pb-2 border-b border-stone-100 flex items-center gap-2">
        <span className="text-blue-600 font-normal text-lg">📖</span>
        Concept Explanation
      </h2>
      <div className="prose-like max-w-none">
        {renderSafeFormattedText(explanation)}
      </div>
    </section>
  )
}
