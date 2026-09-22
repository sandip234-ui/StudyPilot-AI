
export function Badge({ children, variant = 'neutral' }) {
  const variants = {
    neutral: 'bg-stone-100 text-stone-700 border-stone-200',
    blue: 'bg-blue-50 text-blue-700 border-blue-200',
    green: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    amber: 'bg-amber-50 text-amber-700 border-amber-200',
    purple: 'bg-purple-50 text-purple-700 border-purple-200',
  }

  const activeVariant = variants[variant] || variants.neutral

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${activeVariant}`}
    >
      {children}
    </span>
  )
}
