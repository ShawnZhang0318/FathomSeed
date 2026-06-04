<script setup lang="ts">
import { ArrowUpRight, CalendarCheck2, Clock3, Compass, Sparkles, Timer } from 'lucide-vue-next'
import { computed, reactive } from 'vue'
import type { Component } from 'vue'
import type { PlanningMode } from '../types'

type ThemeMode = 'light' | 'dark'

const emit = defineEmits<{
  clarify: [payload: { text: string; durationDays: number; dailyMinutes: number }]
  selectPlanningMode: [mode: PlanningMode]
}>()

const props = defineProps<{
  loading: boolean
  planningMode: PlanningMode
  theme: ThemeMode
}>()

const isDark = computed(() => props.theme === 'dark')
const heroCopy = computed(() =>
  isDark.value
    ? {
        chip: '今日开局配置',
        title: '选择今日开局',
        description:
          '把一个学习目标配置成 Challenge Lobby、路线地图和多模式 Activity Room。你可以先选节奏，再让系统生成今天最适合进入的学习方式。',
        previewEyebrow: 'Preview',
        previewTitle: '挑战大厅会这样生成',
        rhythmHint: '先选节奏，再生成挑战大厅',
        submitLabel: '生成挑战大厅',
        placeholder: '例如：我想学离散数学，用来准备计算机考研'
      }
    : {
        chip: '学习入口',
        title: '今天想抵达哪里？',
        description:
          '先把目标、节奏和每日时间说清楚。系统会生成清晰的学习大厅、规划路线和 Activity Room，让你知道今天从哪里开始。',
        previewEyebrow: 'Plan Preview',
        previewTitle: '学习大厅会这样生成',
        rhythmHint: '先选节奏，再生成学习计划',
        submitLabel: '生成学习计划',
        placeholder: '例如：我想学习 Python，两周后能独立做一个小项目'
      }
)
const previewRows = computed(() =>
  isDark.value
    ? [
        ['今日主线', '函数与参数'],
        ['推荐入口', '刷题 -> 项目'],
        ['奖励预告', '函数徽章碎片']
      ]
    : [
        ['今日重点', '函数与参数'],
        ['学习入口', '刷题 · 播客 · 项目'],
        ['成果沉淀', '轻徽章 · 复盘卡']
      ]
)

const form = reactive({
  text: '我想学习 Python，目标是能独立做一个小项目',
  durationDays: 14,
  dailyMinutes: 45
})

const rhythmModes: Array<{
  code: PlanningMode
  title: string
  badge: string
  description: string
  icon: Component
}> = [
  {
    code: 'j_mode',
    title: 'J人模式',
    badge: '清晰日程',
    description: '按天推进，每天完成后自动打卡。',
    icon: CalendarCheck2
  },
  {
    code: 'p_mode',
    title: 'P人模式',
    badge: '自由任务池',
    description: '生成多种入口，按今天状态选择。',
    icon: Compass
  },
  {
    code: 'adaptive',
    title: '自适应模式',
    badge: '主线 + 今日选择',
    description: '系统守住路线，你选择进入方式。',
    icon: Sparkles
  }
]

function submit() {
  if (!form.text.trim()) return
  emit('clarify', {
    text: form.text.trim(),
    durationDays: form.durationDays,
    dailyMinutes: form.dailyMinutes
  })
}
</script>

<template>
  <section :class="['hero-shell', isDark ? 'hero-shell-hud' : 'hero-shell-clean']">
    <div class="hybrid-hero-grid mx-auto grid gap-8 px-4 py-8 lg:items-start">
      <div class="min-w-0">
        <span class="signal-chip w-fit">
          <Compass :size="14" aria-hidden="true" />
          {{ heroCopy.chip }}
        </span>
        <h1 class="hero-title mt-5">{{ heroCopy.title }}</h1>
        <p class="hero-description mt-5">{{ heroCopy.description }}</p>

        <div class="goal-input-panel mt-9">
          <div class="px-5 pt-5 md:px-7 md:pt-7">
            <label class="sr-only" for="goal">学习目标</label>
            <textarea
              id="goal"
              v-model="form.text"
              class="min-h-44 w-full resize-none border-0 bg-transparent p-0 text-2xl font-black leading-10 outline-none placeholder:soft-text md:text-[30px]"
              maxlength="4000"
              :placeholder="heroCopy.placeholder"
            />
          </div>

          <div class="border-t px-5 py-5 md:px-7" style="border-color: var(--line)">
            <div class="mb-3 flex flex-wrap items-center justify-between gap-2">
              <span class="text-sm font-black soft-text">学习节奏</span>
              <span class="text-xs font-bold muted-text">{{ heroCopy.rhythmHint }}</span>
            </div>
            <div class="grid gap-3 xl:grid-cols-3">
              <button
                v-for="mode in rhythmModes"
                :key="mode.code"
                type="button"
                class="rhythm-choice"
                :class="{ 'is-active': planningMode === mode.code }"
                @click="emit('selectPlanningMode', mode.code)"
              >
                <span class="rhythm-choice-icon">
                  <component :is="mode.icon" :size="18" aria-hidden="true" />
                </span>
                <span class="min-w-0">
                  <strong>{{ mode.title }}</strong>
                  <small>{{ mode.badge }} · {{ mode.description }}</small>
                </span>
              </button>
            </div>
          </div>

          <div
            class="grid gap-4 border-t px-5 py-5 md:grid-cols-[1fr_1fr] xl:grid-cols-[1fr_1fr_auto] md:px-7"
            style="border-color: var(--line); background: var(--surface-soft)"
          >
            <label class="grid gap-2 text-sm font-bold">
              <span class="soft-text">周期</span>
              <span class="field-shell flex items-center gap-3 px-4 py-3">
                <Timer :size="18" class="soft-text" aria-hidden="true" />
                <input
                  v-model.number="form.durationDays"
                  type="number"
                  min="1"
                  max="180"
                  class="w-full border-0 bg-transparent text-base font-bold outline-none"
                />
                <span class="text-sm soft-text">天</span>
              </span>
            </label>

            <label class="grid gap-2 text-sm font-bold">
              <span class="soft-text">每天</span>
              <span class="field-shell flex items-center gap-3 px-4 py-3">
                <Clock3 :size="18" class="soft-text" aria-hidden="true" />
                <input
                  v-model.number="form.dailyMinutes"
                  type="number"
                  min="10"
                  max="480"
                  class="w-full border-0 bg-transparent text-base font-bold outline-none"
                />
                <span class="text-sm soft-text">分钟</span>
              </span>
            </label>

            <div class="grid items-end md:col-span-2 xl:col-span-1">
              <button class="primary-button w-full xl:min-w-48" :disabled="loading" @click="submit">
                {{ heroCopy.submitLabel }}
                <ArrowUpRight :size="18" aria-hidden="true" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <aside :class="['start-preview-panel', isDark ? 'start-preview-panel-hud' : 'start-preview-panel-clean']">
        <p class="text-xs font-black uppercase soft-text">{{ heroCopy.previewEyebrow }}</p>
        <h2 class="mt-3 text-2xl font-black">{{ heroCopy.previewTitle }}</h2>
        <div class="mt-5 grid gap-3">
          <div v-for="row in previewRows" :key="row[0]" class="metric-row">
            <span>{{ row[0] }}</span>
            <strong>{{ row[1] }}</strong>
          </div>
        </div>
      </aside>
    </div>
  </section>
</template>
