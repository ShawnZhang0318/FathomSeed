<script setup lang="ts">
import {
  Brain,
  Clapperboard,
  Dumbbell,
  Film,
  FolderGit2,
  Gamepad2,
  Headphones,
  MessageCircleQuestion,
  SlidersHorizontal
} from 'lucide-vue-next'
import type { Component } from 'vue'
import type { MethodOption } from '../types'

defineProps<{
  methods: MethodOption[]
  selected: string[]
}>()

const emit = defineEmits<{
  toggle: [code: string]
}>()

const icons: Record<string, Component> = {
  drill: Dumbbell,
  game: Gamepad2,
  quest: Gamepad2,
  podcast: Headphones,
  video: Clapperboard,
  cinematic: Film,
  project_lab: FolderGit2,
  mentor: MessageCircleQuestion,
  memory: Brain,
  mixed: SlidersHorizontal
}
</script>

<template>
  <section class="mx-auto max-w-6xl px-4 py-10">
    <div class="mb-7 flex flex-wrap items-end justify-between gap-4">
      <div>
        <span class="signal-chip">第 2 步 · 入口偏好</span>
        <h2 class="mt-3 text-2xl font-black tracking-normal md:text-3xl">选择要编排进大厅的入口</h2>
        <p class="mt-2 max-w-2xl text-sm leading-7 muted-text">
          确认后，系统会把这些入口生成到今日大厅，真正的进入按钮会出现在生成后的任务里。
        </p>
      </div>
    </div>

    <div class="grid auto-rows-fr grid-cols-1 gap-4 md:grid-cols-3">
      <button
        v-for="method in methods"
        :key="method.code"
        class="choice-card group"
        :class="{ 'is-active': selected.includes(method.code) }"
        @click="emit('toggle', method.code)"
      >
        <span class="choice-icon transition group-hover:scale-105">
          <component :is="icons[method.code] ?? SlidersHorizontal" :size="26" aria-hidden="true" />
        </span>
        <div class="mt-5 text-lg font-black">{{ method.title }}</div>
        <p class="mt-3 text-sm leading-7 muted-text">{{ method.description }}</p>
      </button>
    </div>
  </section>
</template>
