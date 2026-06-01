<script setup lang="ts">
import { CalendarCheck2, Compass, Sparkles } from 'lucide-vue-next'
import type { Component } from 'vue'
import type { PlanningMode } from '../types'

defineProps<{
  selected: PlanningMode
}>()

const emit = defineEmits<{
  select: [mode: PlanningMode]
}>()

const modes: Array<{
  code: PlanningMode
  title: string
  badge: string
  description: string
  detail: string
  icon: Component
}> = [
  {
    code: 'j_mode',
    title: 'J人模式',
    badge: '每天安排清楚',
    description: '适合想按路线推进、每天知道该做什么的人。',
    detail: '系统生成按天计划，完成当天任务后自动打卡。',
    icon: CalendarCheck2
  },
  {
    code: 'p_mode',
    title: 'P人模式',
    badge: '今天自由进入',
    description: '适合不想被日程绑死、想按状态和兴趣学习的人。',
    detail: '系统生成任务池，每天推荐多个入口，你自由选择体验。',
    icon: Compass
  },
  {
    code: 'adaptive',
    title: '自适应模式',
    badge: '有主线也有选择',
    description: '适合有目标，但每天状态不同的人。',
    detail: '系统把控阶段进度，你选择今天用刷题、游戏、播客还是项目进入。',
    icon: Sparkles
  }
]
</script>

<template>
  <section class="mx-auto max-w-6xl px-4 py-10">
    <div class="mb-7 flex flex-wrap items-end justify-between gap-4">
      <div>
        <span class="signal-chip">学习节奏</span>
        <h2 class="mt-3 text-2xl font-black tracking-[-0.035em] md:text-3xl">
          你更想怎么推进？
        </h2>
        <p class="mt-2 max-w-2xl text-sm leading-7 muted-text">
          这不是性格测试，只是选择学习节奏。之后可以随时切换和重生成。
        </p>
      </div>
    </div>

    <div class="grid auto-rows-fr gap-5 md:grid-cols-3">
      <button
        v-for="mode in modes"
        :key="mode.code"
        class="mode-card"
        :class="{ 'is-active': selected === mode.code }"
        @click="emit('select', mode.code)"
      >
        <div class="flex items-start justify-between gap-4">
          <span class="choice-icon">
            <component :is="mode.icon" :size="28" aria-hidden="true" />
          </span>
          <span class="mode-card-badge">{{ mode.badge }}</span>
        </div>
        <h3 class="mt-6 text-2xl font-black tracking-[-0.035em]">{{ mode.title }}</h3>
        <p class="mt-3 text-sm leading-7 muted-text">{{ mode.description }}</p>
        <p class="mt-4 text-xs font-bold leading-6 soft-text">{{ mode.detail }}</p>
      </button>
    </div>
  </section>
</template>
