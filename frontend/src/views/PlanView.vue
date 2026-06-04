<script setup lang="ts">
import {
  ArrowLeft,
  CalendarCheck2,
  Compass,
  Gamepad2,
  Medal,
  RotateCcw,
  Sparkles,
  Trophy
} from 'lucide-vue-next'
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
const planningMode = computed(() => plan.value?.planning_mode ?? 'adaptive')

const modeMeta = computed(() => {
  if (planningMode.value === 'j_mode') {
    return {
      title: 'J人模式',
      eyebrow: 'Quest Line',
      icon: CalendarCheck2,
      description: '按天推进，路线清楚，每天完成后自动打卡。',
      progressTitle: '每日完成度',
      progressHint: '完成当天全部入口后打卡'
    }
  }
  if (planningMode.value === 'p_mode') {
    return {
      title: 'P人模式',
      eyebrow: 'Open Pool',
      icon: Compass,
      description: '系统准备任务池，你按今天的状态自由选择学习入口。',
      progressTitle: '任务池进度',
      progressHint: '完成任意入口都会训练系统偏好'
    }
  }
  return {
    title: '自适应模式',
    eyebrow: 'Hybrid Lobby',
    icon: Sparkles,
    description: '系统守住阶段主线，你选择今天从刷题、游戏、播客、项目或闪卡进入。',
    progressTitle: '今日达标度',
    progressHint: '达到 70% 即视为今日达标'
  }
})

const dayTargetPercent = computed(() => (planningMode.value === 'adaptive' ? 70 : 100))
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
    const percent = Math.round(total / Math.max(1, tasks.length))
    return {
      dayNumber,
      percent,
      isComplete: percent >= dayTargetPercent.value,
      taskCount: tasks.length,
      tasks
    }
  })
})
const currentDay = computed(() => dayProgress.value.find((day) => !day.isComplete) ?? dayProgress.value[0])
const poolProgress = computed(() => {
  if (!plan.value?.tasks.length) return 0
  const total = plan.value.tasks.reduce((sum, task) => sum + taskProgress(task), 0)
  return Math.round(total / plan.value.tasks.length)
})
const recommendedTasks = computed(() => {
  if (!plan.value) return []
  const openTasks = plan.value.tasks.filter((task) => taskProgress(task) < 100)
  if (planningMode.value === 'p_mode') {
    return openTasks.slice(0, 5)
  }
  const dayNumber = currentDay.value?.dayNumber ?? 1
  const dayTasks = plan.value.tasks.filter((task) => task.day_number === dayNumber && taskProgress(task) < 100)
  return (dayTasks.length ? dayTasks : openTasks).slice(0, 4)
})
const headlineTask = computed(() => recommendedTasks.value[0] ?? plan.value?.tasks[0] ?? null)
const returnLabel = computed(() => (planningMode.value === 'p_mode' ? '返回任务池' : '返回 Challenge Lobby'))
const activeActivityProgress = computed(() =>
  activeActivityTask.value ? taskProgress(activeActivityTask.value) : 0
)
const activeActivityLabel = computed(() =>
  activeActivityTask.value ? activityLabel(activeActivityTask.value) : '学习活动'
)
const honorItems = computed(() => [
  { title: '变量徽章', status: poolProgress.value > 10 ? '已获得' : '待解锁', tone: 'green' },
  { title: '循环徽章', status: poolProgress.value > 24 ? '已获得' : '待解锁', tone: 'green' },
  { title: '函数徽章', status: poolProgress.value > 44 ? '今日中' : '待解锁', tone: 'gold' },
  { title: '项目杯', status: projectCount.value ? `${projectCount.value} 个项目` : '待解锁', tone: 'blue' },
  { title: '错因档案', status: '持续记录', tone: 'orange' },
  { title: '复盘卡', status: '自动沉淀', tone: 'violet' }
])

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
    game: '学习游戏',
    quest: '学习游戏',
    podcast: '播客讲解',
    video: '短视频学习',
    cinematic: '电影故事',
    project_lab: '项目实验室',
    mentor: '导师对话',
    memory: '闪卡记忆'
  }
  return labels[task.experience_mode || task.method_code] ?? '学习活动'
}

function entryLabel(task: PlanTask): string {
  const labels: Record<string, string> = {
    drill: '进入刷题',
    game: '进入游戏',
    quest: '进入游戏',
    podcast: '进入播客',
    video: '进入短视频',
    cinematic: '进入故事',
    project_lab: '进入项目',
    mentor: '进入对话',
    memory: '进入闪卡'
  }
  return labels[task.experience_mode || task.method_code] ?? '进入学习'
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
  if (planningMode.value === 'p_mode') {
    message.value = '已记录一次学习进度，任务池会继续根据你的选择调整'
    return
  }
  const dayTasks = plan.value.tasks.filter((task) => task.day_number === dayNumber)
  if (dayTasks.length > 0) {
    const percent = Math.round(dayTasks.reduce((sum, task) => sum + taskProgress(task), 0) / dayTasks.length)
    if (percent >= dayTargetPercent.value) {
      message.value =
        planningMode.value === 'adaptive'
          ? `Day ${dayNumber} 已达标，今日主线已自动打卡`
          : `Day ${dayNumber} 已完成，今日计划已自动打卡`
    }
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
    <section class="activity-topbar mb-6">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div class="flex min-w-0 items-center gap-3">
          <button class="text-button shrink-0" @click="closeActivity">
            <ArrowLeft :size="16" aria-hidden="true" />
            {{ returnLabel }}
          </button>
          <div class="min-w-0">
            <p class="text-sm font-extrabold soft-text">{{ activeActivityLabel }}</p>
            <h1 class="mt-1 truncate text-2xl font-black tracking-normal md:text-4xl">
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
    <section id="learning-lobby" class="challenge-lobby">
      <div class="lobby-copy">
        <p class="mb-3 flex items-center gap-2 text-sm font-extrabold soft-text">
          <component :is="modeMeta.icon" :size="16" aria-hidden="true" />
          {{ modeMeta.eyebrow }} · {{ modeMeta.title }}
        </p>
        <h1 class="text-3xl font-black tracking-normal md:text-5xl">Challenge Lobby</h1>
        <p class="mt-4 max-w-2xl text-sm leading-7 muted-text">{{ modeMeta.description }}</p>
        <div class="mt-5 flex flex-wrap gap-2">
          <span class="signal-chip">V{{ plan.version }}</span>
          <span class="signal-chip">{{ plan.daily_minutes }} 分钟/天</span>
          <span class="signal-chip">{{ plan.generation_mode === 'local' ? '本地生成' : '智能增强' }}</span>
        </div>
      </div>
      <div class="lobby-card">
        <p class="text-xs font-black uppercase soft-text">Start Mission</p>
        <h2 class="mt-3 text-2xl font-black">{{ headlineTask?.title ?? plan.title }}</h2>
        <p class="mt-3 line-clamp-3 text-sm leading-7 muted-text">
          {{ headlineTask?.description ?? plan.goal_summary }}
        </p>
        <div class="mt-5">
          <div class="flex items-center justify-between text-xs font-black soft-text">
            <span>{{ modeMeta.progressTitle }}</span>
            <span>{{ planningMode === 'p_mode' ? poolProgress : currentDay?.percent ?? 0 }}%</span>
          </div>
          <div class="progress-track mt-2">
            <span :style="{ width: `${planningMode === 'p_mode' ? poolProgress : currentDay?.percent ?? 0}%` }"></span>
          </div>
        </div>
        <button
          v-if="headlineTask"
          class="primary-button mt-6 w-full"
          :disabled="busyTaskId === headlineTask.id"
          @click="startTask(headlineTask)"
        >
          <Gamepad2 :size="16" aria-hidden="true" />
          {{ entryLabel(headlineTask) }}
        </button>
      </div>
    </section>

    <section class="mt-6 grid gap-3 sm:grid-cols-3">
      <div class="signal-chip justify-start">任务 {{ plan.tasks.length }} 个</div>
      <div class="signal-chip justify-start">刷题 {{ practiceCount }} 组 · 游戏 {{ gameCount }} 个</div>
      <div class="signal-chip justify-start">项目 {{ projectCount }} 个 · {{ totalMinutes }} 分钟</div>
    </section>

    <section v-if="recommendedTasks.length" class="mt-6">
      <div class="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p class="text-xs font-black uppercase soft-text">Today Entrances</p>
          <h2 class="mt-2 text-2xl font-black tracking-normal">今天从哪里开始？</h2>
          <p class="mt-2 text-sm leading-7 muted-text">{{ modeMeta.progressHint }}</p>
        </div>
        <button class="text-button" @click="resetPlan">
          <RotateCcw :size="16" aria-hidden="true" />
          重新选择目标
        </button>
      </div>
      <div class="grid gap-3 md:grid-cols-2">
        <article v-for="task in recommendedTasks" :key="task.id" class="pool-entry-card">
          <div class="min-w-0">
            <p class="text-xs font-black soft-text">
              {{ activityLabel(task) }} · {{ task.estimated_minutes }} 分钟 · {{ taskProgress(task) }}%
            </p>
            <h3 class="mt-2 text-base font-black leading-snug">{{ task.title }}</h3>
            <p class="mt-2 line-clamp-2 text-sm leading-6 muted-text">{{ task.description }}</p>
          </div>
          <button class="primary-button" :disabled="busyTaskId === task.id" @click="startTask(task)">
            {{ entryLabel(task) }}
          </button>
        </article>
      </div>
    </section>

    <section id="route-map" class="route-map-panel mt-8">
      <div class="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p class="text-xs font-black uppercase soft-text">Route Map</p>
          <h2 class="mt-2 text-2xl font-black tracking-normal">规划路线</h2>
          <p class="mt-2 text-sm leading-7 muted-text">保留地图征服感，但用清晰学习大厅承载，不变成后台列表。</p>
        </div>
        <span class="signal-chip">
          {{ planningMode === 'p_mode' ? `任务池 ${poolProgress}%` : `Day ${currentDay?.dayNumber ?? 1} · ${currentDay?.percent ?? 0}%` }}
        </span>
      </div>
      <div class="route-node-grid">
        <button
          v-for="day in dayProgress"
          :key="day.dayNumber"
          class="route-node-card"
          :class="{ 'is-complete': day.isComplete, 'is-current': day.dayNumber === currentDay?.dayNumber }"
          @click="day.tasks[0] && startTask(day.tasks[0])"
        >
          <span class="route-node-orb">D{{ day.dayNumber }}</span>
          <strong>{{ day.percent }}%</strong>
          <small>{{ day.taskCount }} 个入口</small>
        </button>
      </div>
    </section>

    <section v-if="message" class="status-callout mt-6">
      {{ message }}
    </section>

    <section class="mt-8">
      <div class="mb-4">
        <p class="text-xs font-black uppercase soft-text">Mission Pool</p>
        <h2 class="mt-2 text-2xl font-black tracking-normal">全部学习入口</h2>
      </div>
      <TaskTimeline
        :plan="plan"
        :planning-mode="planningMode"
        :selected-task-id="planStore.selectedTask?.id ?? null"
        :busy-task-id="busyTaskId"
        @select="selectTask"
        @start="startTask"
        @complete="completeTask"
        @feedback="sendFeedback"
      />
    </section>

    <section id="honor-room" class="honor-room-panel mt-10">
      <div class="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p class="text-xs font-black uppercase soft-text">Honor Room</p>
          <h2 class="mt-2 flex items-center gap-2 text-2xl font-black tracking-normal">
            <Trophy :size="24" aria-hidden="true" />
            荣誉室
          </h2>
          <p class="mt-2 text-sm leading-7 muted-text">荣誉室不占首屏，只从导航进入，用来收藏徽章、错因档案、项目杯和复盘卡。</p>
        </div>
      </div>
      <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <article v-for="item in honorItems" :key="item.title" class="honor-card" :class="`tone-${item.tone}`">
          <span class="honor-icon">
            <Medal :size="22" aria-hidden="true" />
          </span>
          <div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.status }}</p>
          </div>
        </article>
      </div>
    </section>
  </main>
</template>
