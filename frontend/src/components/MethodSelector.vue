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
        <span class="signal-chip">体验装备</span>
        <h2 class="mt-3 text-2xl font-black tracking-normal md:text-3xl">选择可用学习入口</h2>
        <p class="mt-2 max-w-2xl text-sm leading-7 muted-text">
          同一个知识点可以进入刷题、游戏、播客、项目、导师对话、闪卡或短视频。选得越多，系统越能按当天状态调度。
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
