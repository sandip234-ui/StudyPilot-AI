/**
 * API client service for StudyPilot.
 *
 * Calls the FastAPI backend via the Vite /api proxy using relative URLs.
 * Never accesses Ollama directly.
 */

export class ApiError extends Error {
  constructor(message, statusCode = null, originalError = null) {
    super(message)
    this.name = 'ApiError'
    this.statusCode = statusCode
    this.originalError = originalError
  }
}

/**
 * Friendly error messages mapped to specific backend HTTP statuses.
 */
export function getFriendlyErrorMessage(status) {
  switch (status) {
    case 422:
      return 'Please check your topic and learning preferences.'
    case 502:
      return 'StudyPilot received an unexpected response from the AI model. Please try again.'
    case 503:
      return "The local AI model isn't available right now. Make sure Ollama is running and try again."
    case 504:
      return 'The AI model took too long to respond. Please try again.'
    default:
      return 'An unexpected error occurred. Please try again.'
  }
}

/**
 * Generate a personalized learning session from the backend.
 *
 * @param {Object} payload - The LearnRequest payload
 * @param {AbortSignal} [signal] - Optional AbortSignal for request cancellation
 * @returns {Promise<Object>} The LearnResponse data
 */
export async function learnSession(payload, signal) {
  let response

  try {
    response = await fetch('/api/learn', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal,
    })
  } catch (err) {
    // If the request was cancelled intentionally, rethrow so callers can ignore or handle as abort
    if (err.name === 'AbortError' || signal?.aborted) {
      const abortErr = new Error('Request was cancelled')
      abortErr.name = 'AbortError'
      throw abortErr
    }

    // Network error / connection failure
    throw new ApiError(
      "StudyPilot couldn't connect to the backend. Make sure the backend server is running and try again.",
      null,
      err,
    )
  }

  if (!response.ok) {
    const friendlyMessage = getFriendlyErrorMessage(response.status)
    throw new ApiError(friendlyMessage, response.status)
  }

  try {
    return await response.json()
  } catch (err) {
    throw new ApiError(
      'StudyPilot received an unexpected response from the AI model. Please try again.',
      502,
      err,
    )
  }
}

/**
 * Execute a Prompt Engineering Lab experiment across all 4 strategies.
 *
 * @param {Object} payload - The LearnRequest payload
 * @param {AbortSignal} [signal] - Optional AbortSignal
 * @returns {Promise<Object>} The PromptLabResponse data
 */
export async function runPromptLab(payload, signal) {
  let response

  try {
    response = await fetch('/api/prompt-lab', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal,
    })
  } catch (err) {
    if (err.name === 'AbortError' || signal?.aborted) {
      const abortErr = new Error('Experiment was cancelled')
      abortErr.name = 'AbortError'
      throw abortErr
    }

    throw new ApiError(
      "StudyPilot couldn't connect to the backend. Make sure the backend server is running and try again.",
      null,
      err,
    )
  }

  if (!response.ok) {
    const friendlyMessage = getFriendlyErrorMessage(response.status)
    throw new ApiError(friendlyMessage, response.status)
  }

  try {
    return await response.json()
  } catch (err) {
    throw new ApiError(
      'StudyPilot received an unexpected response from the AI model. Please try again.',
      502,
      err,
    )
  }
}

/**
 * Execute a Few-Shot Lab experiment comparing Zero-Shot vs Few-Shot.
 *
 * @param {Object} payload - The LearnRequest payload
 * @param {AbortSignal} [signal] - Optional AbortSignal
 * @returns {Promise<Object>} The FewShotLabResponse data
 */
export async function runFewShotLab(payload, signal) {
  let response

  try {
    response = await fetch('/api/few-shot-lab', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal,
    })
  } catch (err) {
    if (err.name === 'AbortError' || signal?.aborted) {
      const abortErr = new Error('Experiment was cancelled')
      abortErr.name = 'AbortError'
      throw abortErr
    }

    throw new ApiError(
      "StudyPilot couldn't connect to the backend. Make sure the backend server is running and try again.",
      null,
      err,
    )
  }

  if (!response.ok) {
    const friendlyMessage = getFriendlyErrorMessage(response.status)
    throw new ApiError(friendlyMessage, response.status)
  }

  try {
    return await response.json()
  } catch (err) {
    throw new ApiError(
      'StudyPilot received an unexpected response from the AI model. Please try again.',
      502,
      err,
    )
  }
}

/**
 * Submit an evaluation payload to the backend for verification and calculation.
 *
 * @param {Object} payload - The EvaluationRequest payload
 * @param {AbortSignal} [signal] - Optional AbortSignal
 * @returns {Promise<Object>} The EvaluationResult data
 */
export async function submitEvaluation(payload, signal) {
  let response

  try {
    response = await fetch('/api/evaluate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal,
    })
  } catch (err) {
    if (err.name === 'AbortError' || signal?.aborted) {
      const abortErr = new Error('Evaluation submission was cancelled')
      abortErr.name = 'AbortError'
      throw abortErr
    }

    throw new ApiError(
      "StudyPilot couldn't connect to the backend. Make sure the backend server is running and try again.",
      null,
      err,
    )
  }

  if (!response.ok) {
    const friendlyMessage = getFriendlyErrorMessage(response.status)
    throw new ApiError(friendlyMessage, response.status)
  }

  try {
    return await response.json()
  } catch (err) {
    throw new ApiError(
      'StudyPilot received an unexpected response from the evaluation endpoint.',
      502,
      err,
    )
  }
}


