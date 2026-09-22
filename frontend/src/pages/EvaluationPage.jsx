import { useState } from 'react'
import { RUBRIC_CRITERIA, SCORE_LABELS } from '../constants/rubric'
import { REFERENCE_SESSIONS } from '../constants/referenceSessions'
import { submitEvaluation } from '../services/api'

const STORAGE_KEY = 'studypilot_evaluations_v1'

export function EvaluationPage() {
  const [selectedSessionId, setSelectedSessionId] = useState(REFERENCE_SESSIONS[0].id)
  const [activeSession, setActiveSession] = useState(REFERENCE_SESSIONS[0])
  const [viewJson, setViewJson] = useState(false)

  // Scores state: { [criterionId]: { score: number|null, isNa: boolean, justification: string } }
  const [scores, setScores] = useState(() => {
    const initial = {}
    RUBRIC_CRITERIA.forEach((crit) => {
      initial[crit.id] = {
        score: 4,
        isNa: false,
        justification: '',
      }
    })
    return initial
  })

  const [savedEvaluations, setSavedEvaluations] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      return stored ? JSON.parse(stored) : []
    } catch {
      return []
    }
  })
  const [apiVerification, setApiVerification] = useState(null)
  const [apiError, setApiError] = useState(null)
  const [isVerifying, setIsVerifying] = useState(false)
  const [saveSuccessMsg, setSaveSuccessMsg] = useState(null)

  // When session changes, update activeSession
  const handleSelectSession = (id) => {
    setSelectedSessionId(id)
    const found = REFERENCE_SESSIONS.find((s) => s.id === id)
    if (found) {
      setActiveSession(found)
      // If session had no available_time, auto-suggest N/A for time_alignment
      if (!found.context?.available_time) {
        setScores((prev) => ({
          ...prev,
          time_alignment: {
            ...prev.time_alignment,
            isNa: true,
            score: null,
            justification: 'No available study time was specified by the learner.',
          },
        }))
      } else {
        setScores((prev) => ({
          ...prev,
          time_alignment: {
            ...prev.time_alignment,
            isNa: false,
            score: 4,
          },
        }))
      }
    }
    setApiVerification(null)
    setApiError(null)
  }

  // Calculate live score
  const applicableCriteria = RUBRIC_CRITERIA.filter((crit) => !scores[crit.id]?.isNa)
  const totalScore = applicableCriteria.reduce((sum, crit) => sum + (scores[crit.id]?.score || 0), 0)
  const maxPossibleScore = applicableCriteria.length * 5
  const percentage = maxPossibleScore > 0 ? ((totalScore / maxPossibleScore) * 100).toFixed(1) : '0.0'

  const handleScoreChange = (critId, newScore) => {
    setScores((prev) => ({
      ...prev,
      [critId]: {
        ...prev[critId],
        score: newScore,
        isNa: false,
      },
    }))
    setApiVerification(null)
  }

  const handleNaToggle = (critId) => {
    setScores((prev) => {
      const current = prev[critId]
      const nextIsNa = !current.isNa
      return {
        ...prev,
        [critId]: {
          ...current,
          isNa: nextIsNa,
          score: nextIsNa ? null : 3,
        },
      }
    })
    setApiVerification(null)
  }

  const handleJustificationChange = (critId, text) => {
    setScores((prev) => ({
      ...prev,
      [critId]: {
        ...prev[critId],
        justification: text,
      },
    }))
  }

  // Verify calculation via backend API POST /api/evaluate
  const handleVerifyBackend = async () => {
    setIsVerifying(true)
    setApiError(null)

    const payload = {
      topic: activeSession.topic,
      strategy: activeSession.strategy,
      model_used: activeSession.model,
      context_used: activeSession.context,
      generated_response: activeSession.response,
      scores: RUBRIC_CRITERIA.map((crit) => ({
        criterion: crit.id,
        score: scores[crit.id].isNa ? null : scores[crit.id].score,
        max_score: scores[crit.id].isNa ? 0 : 5,
        is_na: scores[crit.id].isNa,
        justification: scores[crit.id].justification || '',
      })),
    }

    try {
      const res = await submitEvaluation(payload)
      setApiVerification(res)
    } catch (err) {
      setApiError(err.message || 'Failed to verify evaluation with backend.')
    } finally {
      setIsVerifying(false)
    }
  }

  // Save evaluation to localStorage
  const handleSaveEvaluation = () => {
    const newEval = {
      id: `eval-${Date.now()}`,
      timestamp: new Date().toISOString(),
      topic: activeSession.topic,
      strategy: activeSession.strategy || 'standard',
      model: activeSession.model || 'llama3.2:3b',
      scores: { ...scores },
      totalScore,
      maxPossibleScore,
      percentage: Number(percentage),
      applicableCount: applicableCriteria.length,
    }

    const updated = [newEval, ...savedEvaluations]
    setSavedEvaluations(updated)
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated))
    } catch {
      // ignore
    }

    setSaveSuccessMsg('Evaluation successfully saved to local history!')
    setTimeout(() => setSaveSuccessMsg(null), 3000)
  }

  const handleDeleteEvaluation = (id) => {
    const updated = savedEvaluations.filter((item) => item.id !== id)
    setSavedEvaluations(updated)
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated))
    } catch {
      // ignore
    }
  }

  const handleClearAllHistory = () => {
    setSavedEvaluations([])
    try {
      localStorage.removeItem(STORAGE_KEY)
    } catch {
      // ignore
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      {/* Header Banner */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-900 border border-amber-200">
            Academic Assessment
          </span>
          <span className="text-xs text-stone-500 font-medium">Transparent · Reproducible · Human-in-the-loop</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-stone-900 tracking-tight">
          Rubric-Based Evaluation Framework
        </h1>
        <p className="text-sm sm:text-base text-stone-600 mt-1 max-w-3xl">
          Evaluate generated learning sessions against 8 explicit criteria on a 1–5 scale. Generation is strictly separated from evaluation, and scores reflect factual rubric alignment without arbitrary quality labels.
        </p>
      </div>

      {/* Session Selector Bar */}
      <div className="bg-white border border-stone-200 rounded-xl p-4 mb-6 shadow-xs flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <label htmlFor="session-select" className="text-xs font-semibold text-stone-700 uppercase tracking-wider">
            Select Response:
          </label>
          <select
            id="session-select"
            value={selectedSessionId}
            onChange={(e) => handleSelectSession(e.target.value)}
            className="text-sm bg-stone-50 border border-stone-300 rounded-lg px-3 py-1.5 font-medium text-stone-800 focus:outline-none focus:ring-2 focus:ring-amber-500"
          >
            {REFERENCE_SESSIONS.map((sess) => (
              <option key={sess.id} value={sess.id}>
                {sess.title}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="text-stone-500 font-medium">Model:</span>
          <span className="font-mono bg-stone-100 px-2 py-0.5 rounded text-stone-700 font-semibold border border-stone-200">
            {activeSession.model}
          </span>
          <span className="text-stone-500 font-medium ml-2">Strategy:</span>
          <span className="font-mono bg-amber-50 px-2 py-0.5 rounded text-amber-800 font-semibold border border-amber-200">
            {activeSession.strategy}
          </span>
        </div>
      </div>

      {/* Main Split Layout: Left = Response Inspector, Right = Evaluation Form */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* LEFT COLUMN: Response Inspector (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white border border-stone-200 rounded-xl p-5 shadow-xs">
            <div className="flex items-center justify-between border-b border-stone-200 pb-3 mb-4">
              <h2 className="text-sm font-bold text-stone-900 flex items-center gap-1.5">
                <span>📄</span> Original Generated Response
              </h2>
              <button
                type="button"
                onClick={() => setViewJson(!viewJson)}
                className="text-xs font-semibold text-stone-600 hover:text-stone-900 bg-stone-100 px-2 py-1 rounded cursor-pointer transition-colors"
              >
                {viewJson ? 'Formatted View' : 'Raw JSON View'}
              </button>
            </div>

            {/* Learner Context Metadata Box */}
            <div className="bg-stone-50 border border-stone-200 rounded-lg p-3 text-xs space-y-1.5 mb-4">
              <div className="font-semibold text-stone-700">Supplied Learner Context:</div>
              <div className="grid grid-cols-2 gap-x-2 gap-y-1 text-stone-600">
                <div><span className="text-stone-500">Topic:</span> <strong className="text-stone-800">{activeSession.topic}</strong></div>
                <div><span className="text-stone-500">Level:</span> <strong className="text-stone-800">{activeSession.context?.knowledge_level}</strong></div>
                <div><span className="text-stone-500">Goal:</span> <strong className="text-stone-800">{activeSession.context?.learning_goal}</strong></div>
                <div><span className="text-stone-500">Time:</span> <strong className="text-stone-800">{activeSession.context?.available_time || 'None (null)'}</strong></div>
                <div><span className="text-stone-500">Style:</span> <strong className="text-stone-800">{activeSession.context?.explanation_style || 'Default'}</strong></div>
                <div><span className="text-stone-500">Difficulty:</span> <strong className="text-stone-800">{activeSession.context?.difficulty || 'Default'}</strong></div>
              </div>
            </div>

            {/* Response Content View */}
            {viewJson ? (
              <pre className="text-xs font-mono bg-stone-950 text-stone-100 p-4 rounded-lg overflow-x-auto max-h-[600px] border border-stone-800">
                {JSON.stringify(activeSession.response, null, 2)}
              </pre>
            ) : (
              <div className="space-y-4 max-h-[600px] overflow-y-auto pr-1 text-xs sm:text-sm text-stone-800">
                <div>
                  <h3 className="text-base font-bold text-stone-900">{activeSession.response?.title}</h3>
                </div>

                {/* Objectives */}
                {activeSession.response?.learning_objectives?.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-stone-700 text-xs uppercase tracking-wider mb-1">Learning Objectives:</h4>
                    <ul className="list-disc list-inside space-y-0.5 text-stone-600">
                      {activeSession.response.learning_objectives.map((obj, i) => (
                        <li key={i}>{obj}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Concept Explanation */}
                {activeSession.response?.concept_explanation && (
                  <div>
                    <h4 className="font-semibold text-stone-700 text-xs uppercase tracking-wider mb-1">Concept Explanation:</h4>
                    <p className="text-stone-700 leading-relaxed bg-stone-50 p-2.5 rounded-lg border border-stone-100">
                      {activeSession.response.concept_explanation}
                    </p>
                  </div>
                )}

                {/* Analogy */}
                {activeSession.response?.analogy && (
                  <div>
                    <h4 className="font-semibold text-stone-700 text-xs uppercase tracking-wider mb-1">Analogy:</h4>
                    <p className="italic text-stone-600 bg-amber-50/60 p-2 rounded border border-amber-200/50">
                      "{activeSession.response.analogy}"
                    </p>
                  </div>
                )}

                {/* Code Examples */}
                {activeSession.response?.examples?.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-stone-700 text-xs uppercase tracking-wider mb-1">Examples:</h4>
                    {activeSession.response.examples.map((ex, i) => (
                      <div key={i} className="mb-2 bg-stone-900 text-stone-100 p-2.5 rounded-lg font-mono text-xs">
                        <div className="text-stone-400 font-sans font-semibold mb-1">{ex.title}</div>
                        <pre className="overflow-x-auto">{ex.code}</pre>
                        {ex.explanation && (
                          <div className="mt-1 text-stone-400 font-sans text-[11px] border-t border-stone-800 pt-1">
                            {ex.explanation}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Practice Questions */}
                {activeSession.response?.practice_questions?.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-stone-700 text-xs uppercase tracking-wider mb-1">Practice Questions:</h4>
                    <ol className="list-decimal list-inside space-y-1 text-stone-600">
                      {activeSession.response.practice_questions.map((q, i) => (
                        <li key={i}>{q}</li>
                      ))}
                    </ol>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* RIGHT COLUMN: Evaluation Scoring Form (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Live Score Summary Sticky Banner */}
          <div className="bg-white border-2 border-stone-900 rounded-xl p-5 shadow-sm sticky top-16 z-10">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <span className="text-xs font-bold text-stone-500 uppercase tracking-wider block">
                  Evaluation Score
                </span>
                <div className="flex items-baseline gap-2 mt-0.5">
                  <span className="text-3xl font-extrabold text-stone-900">{totalScore}</span>
                  <span className="text-sm font-semibold text-stone-500">/ {maxPossibleScore} max</span>
                  <span className="ml-2 px-2.5 py-0.5 rounded-md text-sm font-bold bg-amber-100 text-amber-900 border border-amber-200">
                    {percentage}%
                  </span>
                </div>
                <div className="text-[11px] text-stone-500 mt-1">
                  Active Criteria: <strong>{applicableCriteria.length}</strong> / 8
                  {8 - applicableCriteria.length > 0 && ` (${8 - applicableCriteria.length} N/A excluded from denominator)`}
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleVerifyBackend}
                  disabled={isVerifying}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-stone-100 hover:bg-stone-200 text-stone-700 border border-stone-300 cursor-pointer transition-colors"
                >
                  {isVerifying ? 'Verifying...' : '⚡ Verify with Backend'}
                </button>
                <button
                  type="button"
                  onClick={handleSaveEvaluation}
                  className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-stone-900 hover:bg-stone-800 text-white shadow-xs cursor-pointer transition-colors"
                >
                  💾 Save Evaluation
                </button>
              </div>
            </div>

            {saveSuccessMsg && (
              <div className="mt-2 text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-lg">
                {saveSuccessMsg}
              </div>
            )}

            {apiVerification && (
              <div className="mt-2 text-xs text-stone-700 bg-stone-50 border border-stone-200 px-3 py-2 rounded-lg font-mono">
                ✓ Backend Verified: {apiVerification.total_score} / {apiVerification.max_score} ({apiVerification.percentage}%) at {apiVerification.timestamp.slice(11, 19)} UTC
              </div>
            )}

            {apiError && (
              <div className="mt-2 text-xs text-rose-700 bg-rose-50 border border-rose-200 px-3 py-1.5 rounded-lg">
                {apiError}
              </div>
            )}
          </div>

          {/* Criteria Cards */}
          <div className="space-y-4">
            {RUBRIC_CRITERIA.map((crit, idx) => {
              const current = scores[crit.id] || { score: 3, isNa: false, justification: '' }
              const isNa = current.isNa

              return (
                <div
                  key={crit.id}
                  className={`bg-white border rounded-xl p-4 transition-all shadow-xs ${
                    isNa ? 'border-stone-200 bg-stone-50/50 opacity-80' : 'border-stone-300'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-stone-200 text-stone-700 text-xs font-bold flex items-center justify-center shrink-0">
                          {idx + 1}
                        </span>
                        <h3 className="font-bold text-sm text-stone-900">{crit.title}</h3>
                      </div>
                      <p className="text-xs text-stone-600 mt-1">{crit.description}</p>
                    </div>

                    {/* N/A Toggle for supported criteria (Time Alignment) */}
                    {crit.supportsNa && (
                      <label className="flex items-center gap-1.5 text-xs text-stone-600 font-semibold cursor-pointer shrink-0 ml-2">
                        <input
                          type="checkbox"
                          checked={isNa}
                          onChange={() => handleNaToggle(crit.id)}
                          className="rounded text-amber-600 focus:ring-amber-500"
                        />
                        <span>Mark N/A</span>
                      </label>
                    )}
                  </div>

                  {/* Score 1-5 Radio Buttons */}
                  {!isNa ? (
                    <div className="mt-3">
                      <div className="grid grid-cols-5 gap-1.5 mb-2">
                        {[1, 2, 3, 4, 5].map((val) => {
                          const isSelected = current.score === val
                          return (
                            <button
                              key={val}
                              type="button"
                              onClick={() => handleScoreChange(crit.id, val)}
                              className={`py-1.5 px-2 rounded-lg text-center cursor-pointer transition-all border text-xs font-semibold ${
                                isSelected
                                  ? 'bg-amber-600 text-white border-amber-600 shadow-xs ring-2 ring-amber-200'
                                  : 'bg-stone-50 text-stone-700 border-stone-200 hover:bg-stone-100'
                              }`}
                            >
                              <span className="block text-sm font-bold">{val}</span>
                              <span className="block text-[10px] truncate">{SCORE_LABELS[val]}</span>
                            </button>
                          )
                        })}
                      </div>

                      {/* Active Rubric Level Text */}
                      {current.score && crit.rubric[current.score] && (
                        <div className="text-xs bg-amber-50/70 border border-amber-200/60 p-2 rounded-lg text-amber-900 font-medium">
                          <strong>Level {current.score} ({SCORE_LABELS[current.score]}):</strong> {crit.rubric[current.score]}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="mt-2 text-xs text-stone-500 italic bg-stone-100 p-2 rounded-lg border border-stone-200">
                      Excluded from score calculation (0 points assigned, excluded from denominator).
                    </div>
                  )}

                  {/* Justification Text Area */}
                  <div className="mt-3">
                    <label htmlFor={`just-${crit.id}`} className="block text-[11px] font-semibold text-stone-600 uppercase tracking-wider mb-1">
                      Justification / Evaluator Notes:
                    </label>
                    <input
                      id={`just-${crit.id}`}
                      type="text"
                      value={current.justification || ''}
                      onChange={(e) => handleJustificationChange(crit.id, e.target.value)}
                      placeholder="Factual reason for assigned score..."
                      className="w-full text-xs bg-stone-50 border border-stone-300 rounded-lg px-2.5 py-1.5 text-stone-800 focus:outline-none focus:ring-1 focus:ring-amber-500"
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* COMPARISON & SAVED EVALUATIONS SECTION */}
      <div className="mt-12 pt-8 border-t border-stone-300">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-stone-900">Evaluation History & Criteria Matrix</h2>
            <p className="text-xs text-stone-600">
              Compare factual scores across evaluated strategies. In accordance with academic guidelines, no strategy is automatically declared best or worst.
            </p>
          </div>
          {savedEvaluations.length > 0 && (
            <button
              type="button"
              onClick={handleClearAllHistory}
              className="text-xs text-stone-500 hover:text-rose-600 font-semibold underline cursor-pointer"
            >
              Clear History
            </button>
          )}
        </div>

        {savedEvaluations.length === 0 ? (
          <div className="text-center py-10 bg-stone-50 border border-dashed border-stone-300 rounded-xl text-stone-500 text-xs">
            No saved evaluations yet. Complete the rubric above and click <strong>"Save Evaluation"</strong> to build your comparison matrix.
          </div>
        ) : (
          <div className="overflow-x-auto bg-white border border-stone-200 rounded-xl shadow-xs">
            <table className="w-full text-xs text-left border-collapse">
              <thead>
                <tr className="bg-stone-100 border-b border-stone-200 text-stone-700 font-bold">
                  <th className="p-3">Evaluation / Strategy</th>
                  <th className="p-3">Topic</th>
                  <th className="p-3">Rel</th>
                  <th className="p-3">Pers</th>
                  <th className="p-3">Inst</th>
                  <th className="p-3">Clar</th>
                  <th className="p-3">Comp</th>
                  <th className="p-3">Diff</th>
                  <th className="p-3">Time</th>
                  <th className="p-3">Struct</th>
                  <th className="p-3 text-right">Total</th>
                  <th className="p-3 text-right">Score %</th>
                  <th className="p-3 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-200 text-stone-800">
                {savedEvaluations.map((ev) => (
                  <tr key={ev.id} className="hover:bg-stone-50 transition-colors">
                    <td className="p-3 font-semibold">
                      <span className="font-mono text-amber-800 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">
                        {ev.strategy}
                      </span>
                      <span className="block text-[10px] text-stone-500 mt-0.5 font-mono">
                        {ev.timestamp.slice(0, 10)}
                      </span>
                    </td>
                    <td className="p-3 max-w-[140px] truncate" title={ev.topic}>
                      {ev.topic}
                    </td>
                    <td className="p-3 font-mono">{ev.scores.relevance?.isNa ? 'N/A' : ev.scores.relevance?.score}</td>
                    <td className="p-3 font-mono">{ev.scores.personalization?.isNa ? 'N/A' : ev.scores.personalization?.score}</td>
                    <td className="p-3 font-mono">{ev.scores.instruction_adherence?.isNa ? 'N/A' : ev.scores.instruction_adherence?.score}</td>
                    <td className="p-3 font-mono">{ev.scores.clarity?.isNa ? 'N/A' : ev.scores.clarity?.score}</td>
                    <td className="p-3 font-mono">{ev.scores.completeness?.isNa ? 'N/A' : ev.scores.completeness?.score}</td>
                    <td className="p-3 font-mono">{ev.scores.difficulty_alignment?.isNa ? 'N/A' : ev.scores.difficulty_alignment?.score}</td>
                    <td className="p-3 font-mono">{ev.scores.time_alignment?.isNa ? 'N/A' : ev.scores.time_alignment?.score}</td>
                    <td className="p-3 font-mono">{ev.scores.structure_schema_quality?.isNa ? 'N/A' : ev.scores.structure_schema_quality?.score}</td>
                    <td className="p-3 text-right font-bold font-mono">
                      {ev.totalScore} / {ev.maxPossibleScore}
                    </td>
                    <td className="p-3 text-right font-bold font-mono text-amber-900">
                      {ev.percentage}%
                    </td>
                    <td className="p-3 text-center">
                      <button
                        type="button"
                        onClick={() => handleDeleteEvaluation(ev.id)}
                        className="text-stone-400 hover:text-rose-600 font-bold px-1.5 py-0.5 text-[11px] cursor-pointer"
                        title="Delete evaluation"
                      >
                        ✕
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
