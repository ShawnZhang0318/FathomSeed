<script setup lang="ts">
import { Loader2, Sparkles } from 'lucide-vue-next'
import { computed, onMounted, ref } from 'vue'
import ChatBox from '../components/ChatBox.vue'
import MethodSelector from '../components/MethodSelector.vue'
import StrategyCards from '../components/StrategyCards.vue'
import { api } from '../services/api'
import { methodStore } from '../stores/methodStore'
import { planStore } from '../stores/planStore'
import type { IntentResponse, PlanningMode, StrategyCard } from '../types'

type ThemeMode = 'light' | 'dark'

const props = defineProps<{
  theme: ThemeMode
}>()

const loading = ref(false)
const generating = ref(false)
const intent = ref<IntentResponse | null>(null)
const strategies = ref<StrategyCard[]>([])
const selectedMode = ref('overview')
const selectedPlanningMode = ref<PlanningMode>('adaptive')
const durationDays = ref(14)
const dailyMinutes = ref(45)
const error = ref('')
const finalCtaLabel = computed(() =>
  props.theme === 'dark' ? '生成并进入 Challenge Lobby' : '生成并进入学习大厅'
)
const availabilityLabel = computed(() =>
  props.theme === 'dark' ? '第 2 步已就绪 · 确认后生成挑战大厅' : '第 2 步已就绪 · 确认后生成学习大厅'
)

onMounted(async () => {
  try {
    const response = await api.listMethods()
    methodStore.setMethods(response.methods)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '暂时无法读取体验模式'
  }
})

async function clarify(payload: { text: string; durationDays: number; dailyMinutes: number }) {
  loading.value = true
  error.value = ''
  durationDays.value = payload.durationDays
  dailyMinutes.value = payload.dailyMinutes
  try {
    intent.value = await api.clarify(payload.text)
    const strategyResponse = await api.suggestStrategies(
      intent.value.goal_summary,
      intent.value.subject_area
    )
    strategies.value = strategyResponse.strategies
    selectedMode.value = strategyResponse.strategies[0]?.mode ?? 'overview'
  } catch (err) {
    error.value = err instanceof Error ? err.message : '目标解析暂时不可用'
  } finally {
    loading.value = false
  }
}

async function generatePlan() {
  if (!intent.value) return
  generating.value = true
  error.value = ''
  try {
    const plan = await api.generatePlan({
      goal_summary: intent.value.goal_summary,
      title: intent.value.subject_area === 'general' ? intent.value.goal_summary : `学习${intent.value.subject_area}`,
      subject_area: intent.value.subject_area,
      goal_mode: selectedMode.value,
      planning_mode: selectedPlanningMode.value,
      selected_methods: methodStore.selected,
      selected_experiences: methodStore.selected,
      duration_days: durationDays.value,
      daily_minutes: dailyMinutes.value
    })
    planStore.setPlan(plan)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '计划生成暂时不可用'
  } finally {
    generating.value = false
  }
}
</script>

<template>
  <div>
    <ChatBox
      :loading="loading"
      :planning-mode="selectedPlanningMode"
      :theme="theme"
      @clarify="clarify"
      @select-planning-mode="(mode) => (selectedPlanningMode = mode)"
    />

    <section v-if="intent" class="mx-auto max-w-6xl px-4 py-4">
      <div class="focus-summary-panel">
        <span class="choice-icon shrink-0">
          <Sparkles :size="20" aria-hidden="true" />
        </span>
        <div class="min-w-0">
          <p class="text-xs font-black uppercase soft-text">Goal Confirmed</p>
          <h2 class="mt-2 text-xl font-black">{{ intent.goal_summary }}</h2>
          <div v-if="intent.questions.length" class="mt-3 grid gap-1 text-sm muted-text">
            <p v-for="question in intent.questions" :key="question">{{ question }}</p>
          </div>
        </div>
      </div>
    </section>

    <StrategyCards
      v-if="strategies.length"
      :strategies="strategies"
      :selected="selectedMode"
      @select="(mode) => (selectedMode = mode)"
    />

    <MethodSelector
      v-if="intent && methodStore.methods.length"
      :methods="methodStore.methods"
      :selected="methodStore.selected"
      @toggle="(code) => methodStore.toggle(code)"
    />

    <section
      v-if="intent || error"
      class="build-action-panel mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-6"
    >
      <p v-if="error" class="text-sm font-medium text-coral">{{ error }}</p>
      <span v-else class="signal-chip">{{ availabilityLabel }}</span>
      <button v-if="intent" class="primary-button" :disabled="generating" @click="generatePlan">
        <Loader2 v-if="generating" :size="16" class="animate-spin" aria-hidden="true" />
        {{ finalCtaLabel }}
      </button>
    </section>
  </div>
</template>
