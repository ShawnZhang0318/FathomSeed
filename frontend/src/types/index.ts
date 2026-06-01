export interface IntentResponse {
  needs_clarification: boolean
  goal_summary: string
  subject_area: string
  questions: string[]
}

export interface StrategyCard {
  mode: string
  title: string
  description: string
  best_for: string
}

export interface MethodOption {
  code: string
  title: string
  description: string
}

export type PlanningMode = 'j_mode' | 'p_mode' | 'adaptive'

export interface PlanTask {
  id: string
  plan_id: string
  source_task_id: string | null
  day_number: number
  position: number
  title: string
  description: string
  method_code: string
  experience_mode: string
  skill_type: string
  expected_outcome: string
  exercise_type: string
  content_format: string
  estimated_minutes: number
  difficulty: number
  progress_percent: number
  status: string
  completed_at: string | null
  created_at: string
  updated_at: string
}

export interface LearningPlan {
  id: string
  user_id: string
  plan_group_id: string
  parent_plan_id: string | null
  version: number
  title: string
  goal_summary: string
  goal_mode: string
  planning_mode: PlanningMode
  method_policy: string
  method_mix: Record<string, number>
  experience_policy: string
  experience_mix: Record<string, number>
  duration_days: number
  daily_minutes: number
  status: string
  revision_reason_event_id: string | null
  source_summary: string | null
  generation_mode: string
  created_at: string
  updated_at: string
  tasks: PlanTask[]
}

export interface FeedbackEvent {
  id: string
  user_id: string
  plan_id: string
  task_id: string | null
  event_type: string
  user_comment: string | null
  client_created_at: string
  server_received_at?: string
  processed_at?: string | null
}

export interface ExerciseItem {
  type: string
  prompt: string
  expected_output: string
  hints: string[]
}

export interface ExerciseResponse {
  task_id: string
  provider: string
  exercises: ExerciseItem[]
}
