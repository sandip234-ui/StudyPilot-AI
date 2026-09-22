export function Header({ onLogoClick, activeTab = 'learning', onSelectTab }) {
  return (
    <header className="border-b border-stone-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-3 sm:px-6 py-2.5 sm:py-3.5 flex flex-wrap items-center justify-between gap-2 sm:gap-4">
        {/* Logo / Branding */}
        <button
          type="button"
          onClick={onLogoClick}
          className="flex items-center gap-2 sm:gap-2.5 text-left group focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg p-1 shrink-0"
        >
          <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-sm sm:text-base shadow-sm group-hover:bg-blue-700 transition-colors shrink-0">
            SP
          </div>
          <div>
            <span className="font-semibold text-stone-900 tracking-tight block text-sm sm:text-lg leading-tight">
              StudyPilot
            </span>
            <span className="text-[11px] text-stone-600 block font-medium hidden sm:block">
              AI-Powered Personalized Learning
            </span>
          </div>
        </button>

        {/* Navigation Tabs */}
        {onSelectTab && (
          <nav className="flex items-center bg-stone-100 p-0.5 sm:p-1 rounded-xl border border-stone-200 overflow-x-auto max-w-full">
            <button
              type="button"
              onClick={() => onSelectTab('learning')}
              className={`px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg text-[11px] sm:text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
                activeTab === 'learning'
                  ? 'bg-white text-stone-900 shadow-xs'
                  : 'text-stone-600 hover:text-stone-900'
              }`}
            >
              🎓 Learning
            </button>
            <button
              type="button"
              onClick={() => onSelectTab('lab')}
              className={`px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg text-[11px] sm:text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
                activeTab === 'lab'
                  ? 'bg-white text-purple-900 shadow-xs'
                  : 'text-stone-600 hover:text-stone-900'
              }`}
            >
              🔬 Prompt Lab
            </button>
            <button
              type="button"
              onClick={() => onSelectTab('few_shot')}
              className={`px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg text-[11px] sm:text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
                activeTab === 'few_shot'
                  ? 'bg-white text-emerald-900 shadow-xs'
                  : 'text-stone-600 hover:text-stone-900'
              }`}
            >
              💡 Few-Shot Lab
            </button>
            <button
              type="button"
              onClick={() => onSelectTab('evaluation')}
              className={`px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg text-[11px] sm:text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
                activeTab === 'evaluation'
                  ? 'bg-white text-amber-900 shadow-xs'
                  : 'text-stone-600 hover:text-stone-900'
              }`}
            >
              📊 Evaluation
            </button>
          </nav>
        )}
      </div>
    </header>
  )
}
