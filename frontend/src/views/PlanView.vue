<script setup lang="ts">
import { ArrowLeft, RotateCcw } from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import ExercisePanel from '../components/ExercisePanel.vue'
import TaskTimeline from '../components/TaskTimeline.vue'
import { api } from '../services/api'
import { makeClientEventId, queueFeedbackEvent } from '../services/offlineQueue'
import { offlineQueueStore } from '../stores/offlineQueueStore'
import { planStore } from '../stores/planStore'
import type { ExerciseResponse, FeedbackEvent, PlanTask } from '../types'

const exercises = ref<ExerciseResponse | null>(null)
const loadingExercises = ref(false)
const busyTaskId = ref<string | null>(null)
const message = ref('')
const activeActivityTask = ref<PlanTask | null>(null)

const pivotFeedbackTypes = new Set([
  'TOO_HARD',
  'NOT_UNDERSTOOD',
  'WANT_MORE_PRACTICE',
  'WANT_MORE_EXPLANATION'
])

const plan = computed(() => planStore.plan)
const totalMinutes = computed(() =>
  plan.value?.tasks.reduce((sum, task) => sum + task.estimated_minutes, 0) ?? 0
)
const practiceCount = computed(() =>
  plan.value?.tasks.filter((task) => task.experience_mode === 'drill').length ?? 0
)
const projectCount = computed(() =>
  plan.value?.tasks.filter((task) => task.experience_mode === 'project_lab').length ?? 0
)
const gameCount = computed(() =>
  plan.value?.tasks.filter((task) => ['game', 'quest'].includes(task.experience_mode)).length ?? 0
)
const dayProgress = computed(() => {
  if (!plan.value) return []
  const groups = new Map<number, PlanTask[]>()
  for (const task of plan.value.tasks) {
    const tasks = groups.get(task.day_number) ?? []
    tasks.push(task)
    groups.set(task.day_number, tasks)
  }
  return Array.from(groups.entries()).map(([dayNumber, tasks]) => {
    const total = tasks.reduce((sum, task) => sum + taskProgress(task), 0)
    const percent = Math.round(total / tasks.length)
    return {
      dayNumber,
      percent,
      isComplete: percent >= 100,
      taskCount: tasks.length
    }
  })
})
const currentDay = computed(() => dayProgress.value.find((day) => !day.isComplete) ?? dayProgress.value[0])
const activeActivityProgress = computed(() =>
  activeActivityTask.value ? taskProgress(activeActivityTask.value) : 0
)
const activeActivityLabel = computed(() =>
  activeActivityTask.value ? activityLabel(activeActivityTask.value) : '学习活动'
)

watch(
  () => planStore.selectedTask?.id,
  async (taskId) => {
    await loadExercises(taskId)
  },
  { immediate: true }
)

function selectTask(task: PlanTask) {
  planStore.selectedTask = task
}

function startTask(task: PlanTask) {
  selectTask(task)
  activeActivityTask.value = task
  void loadExercises(task.id)
  window.scrollTo({ top: 0, behavior: 'smooth' })
  if (taskProgress(task) === 0) {
    void updateTaskProgress({ task, progressPercent: 1 })
  }
}

async function loadExercises(taskId: string | undefined | null) {
  exercises.value = null
  if (!taskId || !navigator.onLine) return
  loadingExercises.value = true
  try {
    exercises.value = await api.getExercises(taskId)
  } finally {
    loadingExercises.value = false
  }
}

function closeActivity() {
  activeActivityTask.value = null
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function resetPlan() {
  planStore.plan = null
  planStore.selectedTask = null
  activeActivityTask.value = null
  localStorage.removeItem('fullmind:last-plan')
}

async function completeTask(task: PlanTask) {
  busyTaskId.value = task.id
  message.value = ''
  try {
    if (!navigator.onLine) {
      message.value = '离线时暂不更新任务状态'
      return
    }
    const updated = await api.updateTaskProgress(task.id, 100)
    planStore.patchTask(updated)
    syncActiveActivityTask(updated.id)
    announceDayCompletion(updated.day_number)
  } finally {
    busyTaskId.value = null
  }
}

async function updateTaskProgress(payload: { task: PlanTask; progressPercent: number }) {
  const progressPercent = clampProgress(payload.progressPercent)
  busyTaskId.value = payload.task.id
  message.value = ''
  try {
    if (!navigator.onLine) {
      planStore.patchTask({
        ...payload.task,
        progress_percent: progressPercent,
        status: progressPercent >= 100 ? 'completed' : progressPercent > 0 ? 'in_progress' : 'pending'
      })
      syncActiveActivityTask(payload.task.id)
      announceDayCompletion(payload.task.day_number)
      return
    }
    const updated = await api.updateTaskProgress(payload.task.id, progressPercent)
    planStore.patchTask(updated)
    syncActiveActivityTask(updated.id)
    announceDayCompletion(updated.day_number)
  } finally {
    busyTaskId.value = null
  }
}

function taskProgress(task: PlanTask): number {
  return clampProgress(task.progress_percent ?? (task.status === 'completed' ? 100 : 0))
}

function activityLabel(task: PlanTask): string {
  const labels: Record<string, string> = {
    drill: '刷题训练',
    game: '游戏学习',
    quest: '游戏学习',
    podcast: '播客讲解',
    video: '短视频学习',
    cinematic: '电影故事',
    project_lab: '项目实验室',
    mentor: '导师对话',
    memory: '闪卡记忆'
  }
  return labels[task.experience_mode || task.method_code] ?? '学习活动'
}

function syncActiveActivityTask(taskId: string) {
  if (!activeActivityTask.value || activeActivityTask.value.id !== taskId || !planStore.plan) return
  activeActivityTask.value = planStore.plan.tasks.find((task) => task.id === taskId) ?? activeActivityTask.value
}

function clampProgress(value: number): number {
  return Math.max(0, Math.min(100, Math.round(value)))
}

function announceDayCompletion(dayNumber: number) {
  if (!plan.value) return
  const dayTasks = plan.value.tasks.filter((task) => task.day_number === dayNumber)
  if (dayTasks.length > 0 && dayTasks.every((task) => taskProgress(task) >= 100)) {
    message.value = `Day ${dayNumber} 已完成，今日计划已自动打卡`
  }
}

async function sendFeedback(payload: { task: PlanTask; eventType: string }) {
  if (!plan.value) return
  busyTaskId.value = payload.task.id
  message.value = ''
  const event: FeedbackEvent = {
    id: makeClientEventId(),
    user_id: plan.value.user_id,
    plan_id: plan.value.id,
    task_id: payload.task.id,
    event_type: payload.eventType,
    user_comment: null,
    client_created_at: new Date().toISOString()
  }

  try {
    if (!navigator.onLine) {
      await queueFeedbackEvent(event)
      await offlineQueueStore.refresh()
      message.value = '反馈已保存'
      return
    }

    const saved = await api.createFeedback(event)
    if (pivotFeedbackTypes.has(payload.eventType)) {
      const newPlan = await api.pivotPlan(plan.value.id, saved.id)
      planStore.setPlan(newPlan)
      message.value = `已生成 V${newPlan.version}`
    } else {
      message.value = '反馈已记录'
    }
  } catch (err) {
    await queueFeedbackEvent(event)
    await offlineQueueStore.refresh()
    message.value = err instanceof Error ? '已转入离线队列' : '反馈已保存'
  } finally {
    busyTaskId.value = null
  }
}
</script>

<template>
  <main v-if="plan && activeActivityTask" class="activity-page mx-auto max-w-7xl px-4 py-8">
    <section class="surface-card mb-6 p-5 md:p-6">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div class="flex min-w-0 items-center gap-3">
          <button class="text-button shrink-0" @click="closeActivity">
            <ArrowLeft :size="16" aria-hidden="true" />
            返回计划
          </button>
          <div class="min-w-0">
            <p class="text-sm font-extrabold soft-text">{{ activeActivityLabel }}</p>
            <h1 class="mt-1 truncate text-2xl font-black tracking-[-0.035em] md:text-4xl">
              {{ activeActivityTask.title }}
            </h1>
          </div>
        </div>
        <div class="min-w-[180px]">
          <div class="flex items-center justify-between text-xs font-black soft-text">
            <span>当前进度</span>
            <span>{{ activeActivityProgress }}%</span>
          </div>
          <div class="progress-track mt-2">
            <span :style="{ width: `${activeActivityProgress}%` }"></span>
          </div>
        </div>
      </div>
    </section>

    <ExercisePanel
      :task="activeActivityTask"
      :exercises="exercises"
      :loading="loadingExercises"
      :progress="activeActivityProgress"
      layout="page"
      @progress="updateTaskProgress"
    />
  </main>

  <main v-else-if="plan" class="mx-auto max-w-6xl px-4 py-8">
    <section>
      <div class="surface-card mb-6 p-6">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p class="mb-2 text-sm font-extrabold soft-text">今日学习航线</p>
            <h1 class="text-3xl font-black tracking-[-0.04em] md:text-4xl">{{ plan.title }}</h1>
            <p class="mt-2 text-sm muted-text">
              第 {{ plan.version }} 版路线 · {{ plan.daily_minutes }} 分钟/天 · {{ plan.generation_mode === 'local' ? '本地生成' : '智能增强' }}
            </p>
          </div>
          <button class="text-button" @click="resetPlan">
            <RotateCcw :size="16" aria-hidden="true" />
            重新选择目标
          </button>
        </div>
      </div>
      <div class="mb-6 grid gap-4 md:grid-cols-3">
        <article class="quiet-card p-5">
          <p class="text-xs font-black uppercase tracking-[0.16em] soft-text">Stage 1</p>
          <h2 class="mt-3 text-lg font-black">体验转译</h2>
          <p class="mt-2 text-sm leading-6 muted-text">知识点会被转成播客、微电影、导师追问、短视频或互动游戏。</p>
        </article>
        <article class="quiet-card p-5">
          <p class="text-xs font-black uppercase tracking-[0.16em] soft-text">Stage 2</p>
          <h2 class="mt-3 text-lg font-black">互动练习</h2>
          <p class="mt-2 text-sm leading-6 muted-text">刷题、游戏任务、情景选择和错因记录形成训练闭环。</p>
        </article>
        <article class="quiet-card p-5">
          <p class="text-xs font-black uppercase tracking-[0.16em] soft-text">Stage 3</p>
          <h2 class="mt-3 text-lg font-black">输出沉淀</h2>
          <p class="mt-2 text-sm leading-6 muted-text">用项目、闪卡、脚本和复盘沉淀成可重复使用的学习资产。</p>
        </article>
      </div>
      <div class="mb-6 grid gap-3 sm:grid-cols-3">
        <div class="signal-chip justify-start">任务 {{ plan.tasks.length }} 个</div>
        <div class="signal-chip justify-start">刷题 {{ practiceCount }} 组 · 游戏 {{ gameCount }} 个</div>
        <div class="signal-chip justify-start">项目 {{ projectCount }} 个 · {{ totalMinutes }} 分钟</div>
      </div>
      <div class="quiet-card mb-6 p-5">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p class="text-xs font-black uppercase tracking-[0.16em] soft-text">每日完成度</p>
            <h2 class="mt-2 text-xl font-black">
              Day {{ currentDay?.dayNumber ?? 1 }} · {{ currentDay?.percent ?? 0 }}%
            </h2>
          </div>
          <span class="signal-chip">
            {{ currentDay?.isComplete ? '今日已自动打卡' : `还剩 ${100 - (currentDay?.percent ?? 0)}%` }}
          </span>
        </div>
        <div class="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
          <div
            v-for="day in dayProgress"
            :key="day.dayNumber"
            class="day-progress-pill"
            :class="{ 'is-complete': day.isComplete }"
          >
            <span>Day {{ day.dayNumber }}</span>
            <strong>{{ day.percent }}%</strong>
          </div>
        </div>
      </div>
      <div v-if="message" class="mb-4 rounded-2xl px-4 py-3 text-sm font-semibold" style="border: 1px solid var(--line); background: var(--accent-soft); color: var(--text)">
        {{ message }}
      </div>
      <TaskTimeline
        :plan="plan"
        :selected-task-id="planStore.selectedTask?.id ?? null"
        :busy-task-id="busyTaskId"
        @select="selectTask"
        @start="startTask"
        @complete="completeTask"
        @feedback="sendFeedback"
      />
    </section>
  </main>
</template>
