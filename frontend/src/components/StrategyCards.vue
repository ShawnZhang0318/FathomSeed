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
        <span class="signal-chip">成果方向</span>
        <h2 class="mt-3 text-2xl font-black tracking-[-0.035em] md:text-3xl">选择这次学习的成果形态</h2>
        <p class="mt-2 max-w-2xl text-sm leading-7 muted-text">
          你不是只在“学一个知识点”，而是在选择这段时间要抵达的状态。
        </p>
      </div>
    </div>

    <div class="grid auto-rows-fr grid-cols-1 gap-5 md:grid-cols-3">
      <button
        v-for="strategy in strategies"
        :key="strategy.mode"
        class="choice-card group"
        :class="{ 'is-active': selected === strategy.mode }"
        @click="emit('select', strategy.mode)"
      >
        <span class="choice-icon transition group-hover:scale-105">
          <component :is="icons[strategy.mode] ?? Layers" :size="29" aria-hidden="true" />
        </span>
        <div class="mt-5 text-lg font-black">{{ strategy.title }}</div>
        <p class="mt-3 text-sm leading-7 muted-text">{{ strategy.description }}</p>
        <p class="mt-5 text-xs font-bold uppercase tracking-[0.14em] soft-text">{{ strategy.best_for }}</p>
      </button>
    </div>
  </section>
</template>
