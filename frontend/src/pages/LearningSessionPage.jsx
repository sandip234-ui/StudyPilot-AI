import { SessionHeader } from '../components/session/SessionHeader'
import { LearningObjectives } from '../components/session/LearningObjectives'
import { ConceptExplanation } from '../components/session/ConceptExplanation'
import { TopicBreakdown } from '../components/session/TopicBreakdown'
import { Examples } from '../components/session/Examples'
import { Analogy } from '../components/session/Analogy'
import { PracticeQuestions } from '../components/session/PracticeQuestions'
import { Quiz } from '../components/session/Quiz'
import { RevisionChecklist } from '../components/session/RevisionChecklist'
import { Button } from '../components/ui/Button'

export function LearningSessionPage({ sessionData, onStartNewSession }) {
  if (!sessionData || !sessionData.learning_session) {
    return (
      <div className="text-center py-12">
        <p className="text-stone-600 mb-4">No session data available.</p>
        <Button onClick={onStartNewSession}>Start a New Session</Button>
      </div>
    )
  }

  const {
    topic,
    model_used,
    context_used,
    learning_session,
  } = sessionData

  const {
    title,
    learning_objectives,
    concept_explanation,
    topic_breakdown,
    examples,
    analogy,
    practice_questions,
    quiz,
    revision_checklist,
  } = learning_session

  return (
    <div className="max-w-3xl mx-auto py-2 sm:py-6">
      {/* Session Header with Badges and Model Tag */}
      <SessionHeader
        title={title || topic}
        contextUsed={context_used}
        modelUsed={model_used}
      />

      {/* Learning Objectives */}
      <LearningObjectives objectives={learning_objectives} />

      {/* Concept Explanation */}
      <ConceptExplanation explanation={concept_explanation} />

      {/* Topic Breakdown */}
      <TopicBreakdown breakdown={topic_breakdown} />

      {/* Examples */}
      <Examples examples={examples} />

      {/* Educational Analogy */}
      <Analogy analogy={analogy} />

      {/* Practice Questions */}
      <PracticeQuestions questions={practice_questions} />

      {/* Interactive Quiz */}
      <Quiz quiz={quiz} />

      {/* Interactive Revision Checklist */}
      <RevisionChecklist checklist={revision_checklist} />

      {/* Start New Session CTA */}
      <div className="mt-12 pt-8 border-t border-stone-200 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="text-center sm:text-left">
          <h3 className="font-semibold text-stone-900 text-base">
            Ready to explore another topic?
          </h3>
          <p className="text-xs text-stone-700">
            Start a fresh learning journey anytime.
          </p>
        </div>
        <Button
          size="lg"
          variant="primary"
          onClick={onStartNewSession}
          className="w-full sm:w-auto"
        >
          Start a New Session &rarr;
        </Button>
      </div>
    </div>
  )
}
