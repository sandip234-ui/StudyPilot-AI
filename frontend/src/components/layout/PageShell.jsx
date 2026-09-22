import { Header } from './Header'

export function PageShell({ children, onReset, activeTab = 'learning', onSelectTab, isLanding = false }) {
  const isWide = activeTab === 'lab' || activeTab === 'few_shot' || activeTab === 'evaluation'

  return (
    <div className="min-h-screen bg-stone-50 text-stone-900 flex flex-col font-sans antialiased">
      <Header
        onLogoClick={onReset}
        activeTab={activeTab}
        onSelectTab={onSelectTab}
      />
      <main
        className={`flex-1 w-full mx-auto px-4 sm:px-6 transition-all ${
          isLanding
            ? 'flex flex-col justify-center py-4 sm:py-6 max-w-2xl min-h-[calc(100vh-65px-49px)]'
            : isWide
            ? 'max-w-6xl py-6 sm:py-10'
            : 'max-w-4xl py-6 sm:py-10'
        }`}
      >
        {children}
      </main>
      <footer className="border-t border-stone-200 py-3 sm:py-4 text-center text-xs text-stone-500">
        StudyPilot &mdash; Academic Prompt Engineering &amp; Personalized Learning
      </footer>
    </div>
  )
}

