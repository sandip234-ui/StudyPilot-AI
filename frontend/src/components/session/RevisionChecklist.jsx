import { useState } from 'react'

export function RevisionChecklist({ checklist }) {
  const [checkedItems, setCheckedItems] = useState({})

  if (!checklist || !Array.isArray(checklist) || checklist.length === 0) {
    return null
  }

  const toggleItem = (idx) => {
    setCheckedItems((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }))
  }

  const completedCount = Object.values(checkedItems).filter(Boolean).length

  return (
    <section className="bg-white border border-stone-200 rounded-xl p-6 sm:p-7 mb-8 shadow-xs">
      <div className="flex items-center justify-between pb-3 mb-4 border-b border-stone-100">
        <h2 className="text-xl font-bold text-stone-900 flex items-center gap-2">
          <span className="text-blue-600 font-normal text-lg">📋</span>
          Revision Checklist
        </h2>
        <span className="text-xs font-medium text-stone-700 bg-stone-100 px-2.5 py-1 rounded-full">
          {completedCount} / {checklist.length} completed
        </span>
      </div>

      <div className="space-y-2.5">
        {checklist.map((item, idx) => {
          const isChecked = !!checkedItems[idx]

          return (
            <label
              key={idx}
              className={`flex items-start gap-3 p-3 rounded-lg border transition-colors cursor-pointer select-none ${
                isChecked
                  ? 'bg-stone-50/80 border-stone-200 text-stone-600 line-through'
                  : 'bg-white border-stone-200 text-stone-800 hover:bg-stone-50'
              }`}
            >
              <input
                type="checkbox"
                checked={isChecked}
                onChange={() => toggleItem(idx)}
                className="w-4 h-4 mt-0.5 rounded text-blue-600 border-stone-300 focus:ring-blue-500 cursor-pointer"
              />
              <span className="text-sm sm:text-base leading-snug">{item}</span>
            </label>
          )
        })}
      </div>
    </section>
  )
}
