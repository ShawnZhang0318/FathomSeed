<script setup lang="ts">
import { BookOpenCheck, Moon, Sun, Trophy } from 'lucide-vue-next'
import { computed, onMounted, ref, watchEffect } from 'vue'
import OfflineBanner from './components/OfflineBanner.vue'
import OnboardingView from './views/OnboardingView.vue'
import PlanView from './views/PlanView.vue'
import { planStore } from './stores/planStore'

type ThemeMode = 'light' | 'dark'

const theme = ref<ThemeMode>('light')
const themeClass = computed(() => (theme.value === 'dark' ? 'theme-dark' : 'theme-light'))

function setTheme(nextTheme: ThemeMode) {
  theme.value = nextTheme
  localStorage.setItem('fullmind:theme', nextTheme)
}

onMounted(() => {
  planStore.loadCachedPlan()
  const savedTheme = localStorage.getItem('fullmind:theme')
  if (savedTheme === 'dark' || savedTheme === 'light') {
    theme.value = savedTheme
  }
  if (savedTheme === 'space') {
    theme.value = 'dark'
  }
})

watchEffect(() => {
  document.documentElement.dataset.theme = theme.value
})
</script>

<template>
  <div class="app-shell" :class="themeClass">
    <div class="space-layer" aria-hidden="true"></div>
    <div class="app-content">
      <header class="app-header sticky top-0 z-20">
        <div class="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-4">
          <div class="flex items-center gap-3">
            <span class="brand-mark">
              <BookOpenCheck :size="22" aria-hidden="true" />
            </span>
            <div>
              <span class="block text-lg font-black tracking-tight">FathomSeed</span>
              <span class="hidden text-xs font-semibold soft-text sm:block">悟道星火 · 学习体验引擎</span>
            </div>
          </div>

          <nav v-if="planStore.plan" class="app-nav" aria-label="学习导航">
            <a href="#learning-lobby">今日开局</a>
            <a href="#route-map">路线</a>
            <a href="#honor-room">
              <Trophy :size="14" aria-hidden="true" />
              荣誉室
            </a>
          </nav>

          <div class="theme-switch" aria-label="面板主题切换">
            <button
              type="button"
              :class="{ 'is-active': theme === 'light' }"
              @click="setTheme('light')"
            >
              <Sun :size="15" aria-hidden="true" />
              Light
            </button>
            <button
              type="button"
              :class="{ 'is-active': theme === 'dark' }"
              @click="setTheme('dark')"
            >
              <Moon :size="15" aria-hidden="true" />
              Dark
            </button>
          </div>
        </div>
      </header>

      <OfflineBanner />
      <OnboardingView v-if="!planStore.plan" />
      <PlanView v-else />
    </div>
  </div>
</template>
