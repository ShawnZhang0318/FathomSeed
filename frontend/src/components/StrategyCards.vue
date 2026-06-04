<script setup lang="ts">
import { Briefcase, FlaskConical, GraduationCap, Layers, Rocket } from 'lucide-vue-next'
import type { Component } from 'vue'
import type { StrategyCard } from '../types'

defineProps<{
  strategies: StrategyCard[]
  selected: string
}>()

const emit = defineEmits<{
  select: [mode: string]
}>()

const icons: Record<string, Component> = {
  exam: GraduationCap,
  research: FlaskConical,
  job: Briefcase,
  project: Rocket,
  overview: Layers
}
</script>

<template>
  <section class="mx-auto max-w-6xl px-4 py-10">
    <div class="mb-7 flex flex-wrap items-end justify-between gap-4">
      <div>
        <span class="signal-chip">第 2 步 · 成果方向</span>
        <h2 class="mt-3 text-2xl font-black tracking-normal md:text-3xl">选择这次学习要交付什么</h2>
        <p class="mt-2 max-w-2xl text-sm leading-7 muted-text">
          你不是只在学一个知识点，而是在决定这段时间要抵达的状态：考试、项目、求职、研究或快速入门。
        </p>
      </div>
    </div>

    <div class="grid auto-rows-fr grid-cols-1 gap-4 md:grid-cols-3">
      <button
        v-for="strategy in strategies"
        :key="strategy.mode"
        class="choice-card group"
        :class="{ 'is-active': selected === strategy.mode }"
        @click="emit('select', strategy.mode)"
      >
        <span class="choice-icon transition group-hover:scale-105">
          <component :is="icons[strategy.mode] ?? Layers" :size="26" aria-hidden="true" />
        </span>
        <div class="mt-5 text-lg font-black">{{ strategy.title }}</div>
        <p class="mt-3 text-sm leading-7 muted-text">{{ strategy.description }}</p>
        <p class="mt-5 text-xs font-bold uppercase soft-text">{{ strategy.best_for }}</p>
      </button>
    </div>
  </section>
</template>
