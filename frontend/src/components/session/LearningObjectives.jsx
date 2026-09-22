
export function LearningObjectives({ objectives }) {
  if (!objectives || !Array.isArray(objectives) || objectives.length === 0) {
    return null
  }

  return (
    <section className="bg-blue-50/70 border border-blue-100 rounded-xl p-5 mb-8">
      <h2 className="text-base font-semibold text-blue-900 mb-3 flex items-center gap-2">
        <svg
          className="w-5 h-5 text-blue-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        Learning Objectives
      </h2>
      <ul className="space-y-2">
        {objectives.map((obj, idx) => (
          <li key={idx} className="flex items-start gap-2.5 text-sm text-blue-950">
            <span className="text-blue-600 font-bold select-none mt-0.5">✓</span>
            <span>{obj}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}
