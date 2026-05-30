import { reactive } from 'vue'
import type { LearningPlan, PlanTask } from '../types'

export const planStore = reactive({
  plan: null as LearningPlan | null,
  selectedTask: null as PlanTask | null,
  setPlan(plan: LearningPlan) {
    this.plan = normalizePlan(plan)
    localStorage.setItem('fullmind:last-plan', JSON.stringify(this.plan))
    this.selectedTask = this.plan.tasks[0] ?? null
  },
  patchTask(task: PlanTask) {
    if (!this.plan) return
    const normalizedTask = normalizeTask(task)
    this.plan.tasks = this.plan.tasks.map((item) => (item.id === task.id ? normalizedTask : item))
    if (this.selectedTask?.id === task.id) {
      this.selectedTask = normalizedTask
    }
    localStorage.setItem('fullmind:last-plan', JSON.stringify(this.plan))
  },
  loadCachedPlan() {
    const cached = localStorage.getItem('fullmind:last-plan')
    if (!cached) return
    this.plan = normalizePlan(JSON.parse(cached) as LearningPlan)
    this.selectedTask = this.plan.tasks[0] ?? null
  }
})

function normalizePlan(plan: LearningPlan): LearningPlan {
  return {
    ...plan,
    tasks: plan.tasks.map(normalizeTask)
  }
}

function normalizeTask(task: PlanTask): PlanTask {
  return {
    ...task,
    progress_percent: task.progress_percent ?? (task.status === 'completed' ? 100 : 0)
  }
}
