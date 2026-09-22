import { useState } from 'react'
import { PageShell } from './components/layout/PageShell'
import { LandingPage } from './pages/LandingPage'
import { ContextFormPage } from './pages/ContextFormPage'
import { GeneratingPage } from './pages/GeneratingPage'
import { LearningSessionPage } from './pages/LearningSessionPage'
import { ErrorPage } from './pages/ErrorPage'
import { PromptLabPage } from './pages/PromptLabPage'
import { FewShotLabPage } from './pages/FewShotLabPage'
import { EvaluationPage } from './pages/EvaluationPage'
import { useLearnSession } from './hooks/useLearnSession'

const INITIAL_FORM_DATA = {
  knowledge_level: null,
  learning_goal: null,
  available_time: null,
  explanation_style: null,
  difficulty: null,
  output_type: null,
}

export default function App() {
  const [activeTab, setActiveTab] = useState('learning') // 'learning' | 'lab' | 'few_shot'
  const [appState, setAppState] = useState('landing') // landing | context | generating | session | error
  const [topic, setTopic] = useState('')
  const [formData, setFormData] = useState(INITIAL_FORM_DATA)

  const {
    sessionData,
    error,
    generate,
    cancel,
    reset: resetHook,
    setError,
  } = useLearnSession()

  // Reset entire application state to fresh landing
  const handleResetAll = () => {
    cancel()
    resetHook()
    setTopic('')
    setFormData(INITIAL_FORM_DATA)
    setAppState('landing')
    setActiveTab('learning')
  }

  // landing -> context
  const handleStartLearning = () => {
    if (topic.trim().length >= 3) {
      setAppState('context')
    }
  }

  // context -> landing (preserves topic & form data)
  const handleEditTopic = () => {
    setAppState('landing')
  }

  // context -> generating -> session | error
  const handleGenerateSession = async () => {
    setAppState('generating')

    const payload = {
      topic: topic.trim(),
      knowledge_level: formData.knowledge_level,
      learning_goal: formData.learning_goal,
      available_time: formData.available_time || null,
      explanation_style: formData.explanation_style || null,
      difficulty: formData.difficulty || null,
      output_type: formData.output_type || null,
    }

    const result = await generate(payload)

    if (result.success) {
      setAppState('session')
    } else if (result.cancelled) {
      // Aborted by student clicking Cancel: return to context with all selections preserved
      setAppState('context')
    } else {
      setAppState('error')
    }
  }

  // generating -> context (Cancel)
  const handleCancelGeneration = () => {
    cancel()
    setAppState('context')
  }

  // error -> context (Try Again)
  const handleTryAgain = () => {
    setError(null)
    setAppState('context')
  }

  return (
    <PageShell
      onReset={handleResetAll}
      activeTab={activeTab}
      onSelectTab={setActiveTab}
      isLanding={activeTab === 'learning' && appState === 'landing'}
    >
      {activeTab === 'evaluation' ? (
        <EvaluationPage />
      ) : activeTab === 'few_shot' ? (
        <FewShotLabPage />
      ) : activeTab === 'lab' ? (
        <PromptLabPage />
      ) : (
        <>
          {appState === 'landing' && (
            <LandingPage
              topic={topic}
              onTopicChange={setTopic}
              onStartLearning={handleStartLearning}
            />
          )}

          {appState === 'context' && (
            <ContextFormPage
              topic={topic}
              formData={formData}
              onFormChange={setFormData}
              onEditTopic={handleEditTopic}
              onGenerate={handleGenerateSession}
            />
          )}

          {appState === 'generating' && (
            <GeneratingPage
              topic={topic}
              onCancel={handleCancelGeneration}
            />
          )}

          {appState === 'session' && (
            <LearningSessionPage
              sessionData={sessionData}
              onStartNewSession={handleResetAll}
            />
          )}

          {appState === 'error' && (
            <ErrorPage
              errorMessage={error}
              onTryAgain={handleTryAgain}
              onStartOver={handleResetAll}
            />
          )}
        </>
      )}
    </PageShell>
  )
}
