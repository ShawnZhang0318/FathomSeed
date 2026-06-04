<script setup lang="ts">
import { ArrowRight, CheckCircle2, Clock, Circle, Play } from 'lucide-vue-next'
import FeedbackButtons from './FeedbackButtons.vue'
import type { LearningPlan, PlanTask } from '../types'

defineProps<{
  plan: LearningPlan
  planningMode: string
  selectedTaskId: string | null
  busyTaskId: string | null
}>()

const emit = defineEmits<{
  select: [task: PlanTask]
  start: [task: PlanTask]
  complete: [task: PlanTask]
  feedback: [payload: { task: PlanTask; eventType: string }]
}>()

function experienceLabel(code: string): string {
  const labels: Record<string, string> = {
    drill: '刷题',
    game: '游戏',
    quest: '游戏',
    podcast: '播客',
    video: '视频',
    cinematic: '故事',
    project_lab: '项目',
    mentor: '导师',
    memory: '闪卡'
  }
  return labels[code] ?? code
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

function unitLabel(task: PlanTask, planningMode: string): string {
  if (planningMode === 'p_mode') return '自由入口'
  if (planningMode === 'adaptive') return `Day ${task.day_number} · 可选入口`
  return `Day ${task.day_number}`
}

function taskProgress(task: PlanTask): number {
  return Math.max(0, Math.min(100, task.progress_percent ?? (task.status === 'completed' ? 100 : 0)))
}
</script>

<template>
  <section class="mission-grid">
    <article
      v-for="task in plan.tasks"
      :key="task.id"
      class="mission-card"
      :class="{ 'is-active': selectedTaskId === task.id }"
    >
      <button class="w-full text-left" @click="emit('select', task)">
        <div class="flex flex-wrap items-center gap-2">
          <CheckCircle2 v-if="task.status === 'completed'" :size="18" class="text-emerald-500" aria-hidden="true" />
          <Play v-else-if="task.status === 'in_progress'" :size="18" class="text-saffron" aria-hidden="true" />
          <Circle v-else :size="18" class="soft-text" aria-hidden="true" />
          <span class="text-sm font-semibold soft-text">{{ unitLabel(task, planningMode) }}</span>
          <span class="signal-chip">
            {{ experienceLabel(task.experience_mode || task.method_code) }}
          </span>
          <span class="flex items-center gap-1 text-xs soft-text">
            <Clock :size="14" aria-hidden="true" />
            {{ task.estimated_minutes }}m
          </span>
        </div>
        <h3 class="mt-3 text-lg font-black leading-snug">{{ task.title }}</h3>
        <p class="mt-2 text-sm leading-6 muted-text">{{ task.description }}</p>
        <p class="mt-3 text-xs font-semibold soft-text">{{ task.expected_outcome }}</p>
        <div class="mt-4">
          <div class="flex items-center justify-between text-xs font-black soft-text">
            <span>完成度</span>
            <span>{{ taskProgress(task) }}%</span>
          </div>
          <div class="progress-track mt-2" aria-hidden="true">
            <span :style="{ width: `${taskProgress(task)}%` }"></span>
          </div>
        </div>
      </button>

      <div class="mt-4 grid gap-3 border-t pt-3" style="border-color: var(--line)">
        <div class="flex flex-wrap gap-2">
          <button
            class="primary-button"
            :disabled="busyTaskId === task.id"
            @click="emit('start', task)"
          >
            <ArrowRight :size="16" aria-hidden="true" />
            {{ entryLabel(task) }}
          </button>
          <button
            class="text-button"
            :disabled="busyTaskId === task.id || taskProgress(task) >= 100"
            @click="emit('complete', task)"
          >
            <CheckCircle2 :size="16" aria-hidden="true" />
            标记完成
          </button>
        </div>
        <FeedbackButtons @feedback="(eventType) => emit('feedback', { task, eventType })" />
      </div>
    </article>
  </section>
</template>
