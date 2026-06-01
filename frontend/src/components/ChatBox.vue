<script setup lang="ts">
import { ArrowUpRight, Clock3, Compass, Timer } from 'lucide-vue-next'
import { reactive } from 'vue'

const emit = defineEmits<{
  clarify: [payload: { text: string; durationDays: number; dailyMinutes: number }]
}>()

defineProps<{
  loading: boolean
}>()

const form = reactive({
  text: '我想学习 Python，目标是能独立做一个小项目',
  durationDays: 14,
  dailyMinutes: 45
})

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
  <section class="panel">
    <div class="mx-auto max-w-6xl px-4 py-10 md:py-16">
      <div class="mx-auto max-w-3xl text-center">
        <span class="signal-chip">
          <Compass :size="14" aria-hidden="true" />
          先说出一个方向
        </span>
        <h1 class="mt-6 text-4xl font-black leading-[1.05] tracking-[-0.045em] md:text-6xl">
          今天想抵达哪里？
        </h1>
        <p class="mx-auto mt-5 max-w-2xl text-base leading-8 muted-text md:text-lg">
          FathomSeed 会把目标拆成学习节奏、体验入口、练习和反馈循环。不开模型也能用，接入模型后会更懂你。
        </p>
      </div>

      <div class="surface-card mx-auto mt-9 max-w-4xl overflow-hidden">
        <div class="px-5 pt-5 md:px-7 md:pt-7">
          <label class="sr-only" for="goal">学习目标</label>
          <textarea
            id="goal"
            v-model="form.text"
            class="min-h-44 w-full resize-none border-0 bg-transparent p-0 text-2xl font-semibold leading-10 outline-none placeholder:soft-text md:text-[32px]"
            maxlength="4000"
            placeholder="例如：我想学离散数学，用来准备计算机考研"
          />
        </div>

        <div class="mt-5 grid gap-4 border-t px-5 py-5 md:grid-cols-[1fr_1fr_auto] md:px-7" style="border-color: var(--line); background: var(--surface-soft)">
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

          <div class="grid items-end">
            <button class="primary-button w-full md:min-w-40" :disabled="loading" @click="submit">
              生成学习方案
              <ArrowUpRight :size="18" aria-hidden="true" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
