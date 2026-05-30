import type {
  ExerciseResponse,
  FeedbackEvent,
  IntentResponse,
  LearningPlan,
  MethodOption,
  PlanTask,
  StrategyCard
} from '../types'

const API_BASES = import.meta.env.VITE_API_BASE
  ? [import.meta.env.VITE_API_BASE]
  : Array.from(
      new Set([
        `${window.location.protocol}//${window.location.hostname}:8010`,
        `${window.location.protocol}//127.0.0.1:8010`
      ])
    )

class HttpResponseError extends Error {}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let lastError: unknown

  for (const base of API_BASES) {
    const controller = new AbortController()
    const timeout = window.setTimeout(() => controller.abort(), 3500)
    try {
      const response = await fetch(`${base}${path}`, {
        headers: {
          'Content-Type': 'application/json',
          ...(init?.headers ?? {})
        },
        ...init,
        signal: controller.signal
      })
      if (!response.ok) {
        const message = await response.text()
        throw new HttpResponseError(message || `Request failed: ${response.status}`)
      }
      return response.json() as Promise<T>
    } catch (error) {
      if (error instanceof HttpResponseError) throw error
      lastError = error
    } finally {
      window.clearTimeout(timeout)
    }
  }

  throw lastError instanceof Error ? lastError : new Error('Request failed')
}

export const api = {
  clarify(text: string) {
    return request<IntentResponse>('/intent/clarify', {
      method: 'POST',
      body: JSON.stringify({ text })
    })
  },
  suggestStrategies(goal_summary: string, subject_area: string) {
    return request<{ strategies: StrategyCard[] }>('/strategies/suggest', {
      method: 'POST',
      body: JSON.stringify({ goal_summary, subject_area })
    })
  },
  listMethods() {
    return request<{ methods: MethodOption[] }>('/methods')
  },
  generatePlan(payload: {
    user_id?: string
    goal_summary: string
    title?: string
    subject_area: string
    goal_mode: string
    selected_methods: string[]
    selected_experiences?: string[]
    duration_days: number
    daily_minutes: number
  }) {
    return request<LearningPlan>('/plans/generate', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  },
  getPlan(planId: string) {
    return request<LearningPlan>(`/plans/${planId}`)
  },
  updateTaskStatus(taskId: string, status: string) {
    return request<PlanTask>(`/tasks/${taskId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status })
    })
  },
  updateTaskProgress(taskId: string, progressPercent: number) {
    return request<PlanTask>(`/tasks/${taskId}/progress`, {
      method: 'PATCH',
      body: JSON.stringify({ progress_percent: progressPercent })
    })
  },
  createFeedback(event: FeedbackEvent) {
    return request<FeedbackEvent>('/feedback-events', {
      method: 'POST',
      body: JSON.stringify(event)
    })
  },
  syncFeedbackEvents(events: FeedbackEvent[]) {
    return request<{ accepted: FeedbackEvent[]; duplicates: string[] }>('/sync/feedback-events', {
      method: 'POST',
      body: JSON.stringify({ events })
    })
  },
  pivotPlan(planId: string, eventId: string) {
    return request<LearningPlan>(`/plans/${planId}/pivot`, {
      method: 'POST',
      body: JSON.stringify({ event_id: eventId })
    })
  },
  getExercises(taskId: string) {
    return request<ExerciseResponse>(`/exercises/task/${taskId}`)
  }
}
