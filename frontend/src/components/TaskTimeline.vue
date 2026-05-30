<script setup lang="ts">
import { ArrowRight, Check, CheckCircle2, Clock, Circle, Play } from 'lucide-vue-next'
import FeedbackButtons from './FeedbackButtons.vue'
import type { LearningPlan, PlanTask } from '../types'

defineProps<{
  plan: LearningPlan
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
    cinematic: '电影',
    project_lab: '项目',
    mentor: '导师',
    memory: '记忆'
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

function taskProgress(task: PlanTask): number {
  return Math.max(0, Math.min(100, task.progress_percent ?? (task.status === 'completed' ? 100 : 0)))
}
</script>

<template>
  <section class="relative grid gap-4 pl-5 before:absolute before:bottom-2 before:left-1.5 before:top-2 before:w-0.5 before:rounded-full before:bg-gradient-to-b before:from-indigo-500 before:via-violet-500 before:to-sky-400">
    <article
      v-for="task in plan.tasks"
      :key="task.id"
      class="quiet-card relative p-5 transition-all before:absolute before:left-[-22px] before:top-6 before:h-4 before:w-4 before:rounded-full before:border-[3px] before:border-white before:bg-indigo-500 before:shadow hover:-translate-y-0.5"
      :class="{ 'is-active': selectedTaskId === task.id }"
    >
      <button class="w-full text-left" @click="emit('select', task)">
        <div class="flex flex-wrap items-center gap-2">
          <Check v-if="task.status === 'completed'" :size="18" class="text-emerald-500" aria-hidden="true" />
          <Play v-else-if="task.status === 'in_progress'" :size="18" class="text-saffron" aria-hidden="true" />
          <Circle v-else :size="18" class="text-slate-400" aria-hidden="true" />
          <span class="text-sm font-semibold soft-text">Day {{ task.day_number }}</span>
          <span class="signal-chip">
            {{ experienceLabel(task.experience_mode || task.method_code) }}
          </span>
          <span class="flex items-center gap-1 text-xs soft-text">
            <Clock :size="14" aria-hidden="true" />
            {{ task.estimated_minutes }}m
          </span>
        </div>
        <h3 class="mt-3 text-lg font-bold">{{ task.title }}</h3>
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
      <div class="mt-4 flex flex-col gap-3 border-t pt-3" style="border-color: var(--line)">
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
