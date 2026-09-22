import { useState, useRef, useCallback } from 'react'
import { learnSession } from '../services/api'

/**
 * Hook to manage learning session generation and cancellation.
 */
export function useLearnSession() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [sessionData, setSessionData] = useState(null)
  const abortControllerRef = useRef(null)

  const generate = useCallback(async (payload) => {
    // Abort any existing pending request before starting a new one
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    const controller = new AbortController()
    abortControllerRef.current = controller

    setLoading(true)
    setError(null)

    try {
      const data = await learnSession(payload, controller.signal)
      setSessionData(data)
      setLoading(false)
      return { success: true, data }
    } catch (err) {
      // If cancelled intentionally, do NOT set an error
      if (err.name === 'AbortError' || controller.signal.aborted) {
        setLoading(false)
        return { success: false, cancelled: true }
      }

      setError(err.message)
      setLoading(false)
      return { success: false, error: err.message }
    } finally {
      if (abortControllerRef.current === controller) {
        abortControllerRef.current = null
      }
    }
  }, [])

  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    setLoading(false)
  }, [])

  const reset = useCallback(() => {
    cancel()
    setError(null)
    setSessionData(null)
  }, [cancel])

  return {
    loading,
    error,
    sessionData,
    generate,
    cancel,
    reset,
    setError,
    setSessionData,
  }
}
