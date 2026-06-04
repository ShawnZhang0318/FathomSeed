<script setup lang="ts">
import {
  BookOpen,
  Brain,
  CheckCircle2,
  Clapperboard,
  Dumbbell,
  Eye,
  Film,
  FolderGit2,
  Gamepad2,
  Headphones,
  Layers3,
  Loader2,
  MessageCircleQuestion,
  Pause,
  Play,
  RotateCcw,
  Save,
  Sparkles,
  Trophy,
  Volume2
} from 'lucide-vue-next'
import type { Component } from 'vue'
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import type { ExerciseItem, ExerciseResponse, PlanTask } from '../types'

const props = defineProps<{
  task: PlanTask | null
  exercises: ExerciseResponse | null
  loading: boolean
  progress: number
  layout?: 'side' | 'page'
}>()

const emit = defineEmits<{
  progress: [payload: { task: PlanTask; progressPercent: number }]
}>()

type StudioTab = 'experience' | 'practice' | 'review'

interface ExperienceMeta {
  label: string
  eyebrow: string
  description: string
  icon: Component
}

const activeTab = ref<StudioTab>('experience')
const selectedIndex = ref(0)
const mixedMode = ref('drill')
const answers = ref<Record<string, string>>({})
const revealedAnswers = ref<Record<string, boolean>>({})
const completed = ref<Record<string, boolean>>({})
const isPlaying = ref(false)
const audioProgress = ref(18)
let playbackTimer: ReturnType<typeof setInterval> | null = null

const experienceMeta: Record<string, ExperienceMeta> = {
  drill: {
    label: '刷题训练场',
    eyebrow: 'Drill',
    description: '连续小题建立手感，再用错因记录反推理解漏洞。',
    icon: Dumbbell
  },
  game: {
    label: '学习游戏舱',
    eyebrow: 'Game',
    description: '把知识点变成模拟、选择、解谜或角色扮演，完成后结算奖励。',
    icon: Gamepad2
  },
  quest: {
    label: '学习游戏舱',
    eyebrow: 'Game',
    description: '把知识点变成模拟、选择、解谜或角色扮演，完成后结算奖励。',
    icon: Gamepad2
  },
  podcast: {
    label: '播客讲解舱',
    eyebrow: 'Podcast',
    description: '用口语化讲解、类比和复盘问题帮助听懂。',
    icon: Headphones
  },
  video: {
    label: '短视频剧场',
    eyebrow: 'Video',
    description: '把知识点拆成镜头、旁白、场景和记忆锚点。',
    icon: Clapperboard
  },
  cinematic: {
    label: '电影故事线',
    eyebrow: 'Story',
    description: '用角色、冲突和反转承载抽象概念。',
    icon: Film
  },
  project_lab: {
    label: '项目实验室',
    eyebrow: 'Project',
    description: '把知识点落成可验收的小交付。',
    icon: FolderGit2
  },
  mentor: {
    label: '导师对话',
    eyebrow: 'Mentor',
    description: '通过追问、提示和重写检查理解。',
    icon: MessageCircleQuestion
  },
  memory: {
    label: '闪卡记忆馆',
    eyebrow: 'Memory',
    description: '用主动回忆和间隔复习稳住长期记忆。',
    icon: Brain
  },
  mixed: {
    label: '混合学习舱',
    eyebrow: 'Adaptive',
    description: '在讲解、练习、项目和复盘之间切换。',
    icon: Sparkles
  }
}

const mixedModeOptions = [
  { code: 'drill', label: '刷题', description: '进入题目工作区', icon: Dumbbell },
  { code: 'game', label: '游戏', description: '挑战与奖励结算', icon: Gamepad2 },
  { code: 'podcast', label: '播客', description: '听读脚本和复盘', icon: Headphones },
  { code: 'project_lab', label: '项目', description: '完成小交付', icon: FolderGit2 },
  { code: 'memory', label: '闪卡', description: '主动回忆', icon: Brain },
  { code: 'video', label: '短视频', description: '镜头脚本', icon: Clapperboard },
  { code: 'mentor', label: '对话', description: '导师追问', icon: MessageCircleQuestion }
]

const mode = computed(() => props.task?.experience_mode || props.task?.method_code || 'mixed')
const effectiveMode = computed(() => (mode.value === 'mixed' ? mixedMode.value : mode.value === 'quest' ? 'game' : mode.value))
const meta = computed(() => experienceMeta[effectiveMode.value] ?? experienceMeta.mixed)
const exerciseItems = computed(() => props.exercises?.exercises ?? [])
const fallbackItems = computed<ExerciseItem[]>(() => [
  {
    type: effectiveMode.value,
    prompt: props.task?.description ?? '选择一个学习任务后，这里会展示对应的 Activity Room。',
    expected_output: props.task?.expected_outcome ?? '完成一次可记录、可反馈、可调整的学习动作。',
    hints: ['先完成最小动作，再根据反馈调整下一步。']
  }
])
const practiceItems = computed(() => (exerciseItems.value.length ? exerciseItems.value : fallbackItems.value))
const currentItem = computed(() => practiceItems.value[selectedIndex.value] ?? practiceItems.value[0])
const normalizedProgress = computed(() => Math.max(0, Math.min(100, props.progress ?? 0)))
const providerLabel = computed(() => {
  const provider = props.exercises?.provider ?? ''
  if (provider.includes('question') || provider.includes('experience')) return '内置体验库'
  if (provider.includes('template')) return '模板生成'
  if (provider.includes('llm')) return '模型增强'
  return '本地内容引擎'
})
const panelClass = computed(() => [
  'studio-panel overflow-hidden',
  props.layout === 'page' ? 'activity-panel' : 'sticky top-24'
])

function itemKey(index: number): string {
  return `${props.task?.id ?? 'task'}-${effectiveMode.value}-${index}`
}

function selectItem(index: number) {
  selectedIndex.value = Math.max(0, Math.min(index, practiceItems.value.length - 1))
}

function emitProgress(progressPercent: number) {
  if (!props.task) return
  emit('progress', {
    task: props.task,
    progressPercent: Math.max(0, Math.min(100, Math.round(progressPercent)))
  })
}

function completeIndex(index: number) {
  completed.value = {
    ...completed.value,
    [itemKey(index)]: true
  }
  const done = Object.values(completed.value).filter(Boolean).length
  emitProgress(Math.round((done / Math.max(1, practiceItems.value.length)) * 100))
}

function toggleReference(index: number) {
  const key = itemKey(index)
  revealedAnswers.value = {
    ...revealedAnswers.value,
    [key]: !revealedAnswers.value[key]
  }
}

function switchMixedMode(nextMode: string) {
  mixedMode.value = nextMode
  activeTab.value = 'experience'
  selectedIndex.value = 0
  completed.value = {}
  stopPlayback()
}

function stopPlayback() {
  if (playbackTimer) {
    clearInterval(playbackTimer)
    playbackTimer = null
  }
  isPlaying.value = false
}

function togglePlayback() {
  if (isPlaying.value) {
    stopPlayback()
    return
  }
  isPlaying.value = true
  playbackTimer = setInterval(() => {
    audioProgress.value = Math.min(100, audioProgress.value + 3)
    if (audioProgress.value >= 100) {
      emitProgress(100)
      stopPlayback()
    }
  }, 700)
}

function resetStudioState() {
  activeTab.value = 'experience'
  mixedMode.value = mode.value === 'mixed' ? 'drill' : effectiveMode.value
  selectedIndex.value = 0
  answers.value = {}
  revealedAnswers.value = {}
  completed.value = {}
  audioProgress.value = Math.max(18, normalizedProgress.value)
  stopPlayback()
}

watch(() => props.task?.id, resetStudioState)
watch(() => props.progress, () => {
  audioProgress.value = Math.max(audioProgress.value, normalizedProgress.value)
})
onBeforeUnmount(stopPlayback)
</script>

<template>
  <section :class="panelClass">
    <div v-if="!task" class="grid min-h-[560px] place-items-center p-6 text-center">
      <div>
        <span class="choice-icon mx-auto">
          <Layers3 :size="24" aria-hidden="true" />
        </span>
        <h2 class="mt-5 text-2xl font-black">选择一个学习任务</h2>
        <p class="mx-auto mt-3 max-w-xs text-sm leading-6 muted-text">
          每个任务都会打开对应的体验空间：刷题、游戏、播客、闪卡、项目、短视频或导师对话。
        </p>
      </div>
    </div>

    <template v-else>
      <section class="studio-hero" :class="`mode-${effectiveMode}`">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div class="min-w-0">
            <p class="studio-eyebrow">{{ meta.eyebrow }}</p>
            <h2 class="mt-2 text-2xl font-black tracking-normal">{{ meta.label }}</h2>
            <p class="mt-2 max-w-2xl text-sm leading-6 text-white/80">{{ meta.description }}</p>
          </div>
          <span class="studio-hero-icon">
            <component :is="meta.icon" :size="24" aria-hidden="true" />
          </span>
        </div>
        <div class="mt-6 rounded-lg border border-white/15 bg-white/10 p-4 backdrop-blur">
          <p class="text-xs font-bold uppercase text-white/60">当前训练</p>
          <h3 class="mt-2 text-lg font-black leading-snug">{{ task.title }}</h3>
          <div class="mt-4 flex flex-wrap gap-2">
            <span class="studio-chip">{{ task.estimated_minutes }} 分钟</span>
            <span class="studio-chip">难度 {{ task.difficulty }}/5</span>
            <span class="studio-chip">进度 {{ normalizedProgress }}%</span>
            <span class="studio-chip">{{ providerLabel }}</span>
          </div>
          <div class="progress-track is-on-dark mt-4" aria-hidden="true">
            <span :style="{ width: `${normalizedProgress}%` }"></span>
          </div>
        </div>
      </section>

      <nav class="studio-tabs" aria-label="学习工作台">
        <button :class="{ 'is-active': activeTab === 'experience' }" @click="activeTab = 'experience'">
          体验
        </button>
        <button :class="{ 'is-active': activeTab === 'practice' }" @click="activeTab = 'practice'">
          练习
        </button>
        <button :class="{ 'is-active': activeTab === 'review' }" @click="activeTab = 'review'">
          复盘
        </button>
      </nav>

      <div v-if="loading" class="grid min-h-72 place-items-center p-6 text-sm muted-text">
        <div class="flex items-center gap-2">
          <Loader2 :size="18" class="animate-spin" aria-hidden="true" />
          正在准备学习内容
        </div>
      </div>

      <section v-else-if="activeTab === 'experience'" class="activity-mode-body p-5">
        <div v-if="mode === 'mixed'" class="mixed-mode-switcher">
          <button
            v-for="option in mixedModeOptions"
            :key="option.code"
            class="mixed-mode-option"
            :class="{ 'is-active': effectiveMode === option.code }"
            @click="switchMixedMode(option.code)"
          >
            <component :is="option.icon" :size="18" aria-hidden="true" />
            <span>
              <strong>{{ option.label }}</strong>
              <small>{{ option.description }}</small>
            </span>
          </button>
        </div>

        <div v-if="effectiveMode === 'drill'" class="answer-workbench">
          <aside class="question-rail">
            <p class="text-xs font-black uppercase soft-text">题目列表</p>
            <button
              v-for="(_, index) in practiceItems"
              :key="itemKey(index)"
              class="question-pill"
              :class="{ 'is-active': selectedIndex === index, 'is-complete': completed[itemKey(index)] }"
              @click="selectItem(index)"
            >
              <span>第 {{ index + 1 }} 题</span>
              <CheckCircle2 v-if="completed[itemKey(index)]" :size="14" aria-hidden="true" />
            </button>
          </aside>

          <article class="answer-main">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <span class="studio-mini-chip">{{ currentItem?.type }}</span>
              <span class="text-sm font-black soft-text">{{ selectedIndex + 1 }} / {{ practiceItems.length }}</span>
            </div>
            <h3 class="question-prompt">{{ currentItem?.prompt }}</h3>
            <div v-if="currentItem?.hints.length" class="flex flex-wrap gap-2">
              <span v-for="hint in currentItem.hints" :key="hint" class="studio-mini-chip">{{ hint }}</span>
            </div>
            <textarea
              v-model="answers[itemKey(selectedIndex)]"
              class="answer-textarea"
              rows="8"
              placeholder="写下你的答案、代码、推理过程或错因记录。"
            ></textarea>
            <div class="flex flex-wrap items-center gap-3">
              <button class="primary-button" @click="completeIndex(selectedIndex)">
                <Save :size="16" aria-hidden="true" />
                保存本题
              </button>
              <button class="text-button" @click="toggleReference(selectedIndex)">
                <Eye :size="16" aria-hidden="true" />
                {{ revealedAnswers[itemKey(selectedIndex)] ? '收起参考' : '查看参考' }}
              </button>
            </div>
            <div v-if="revealedAnswers[itemKey(selectedIndex)]" class="reference-panel">
              <p class="text-xs font-black uppercase soft-text">参考答案 / 解析</p>
              <p class="mt-3 whitespace-pre-wrap text-sm leading-7">{{ currentItem?.expected_output }}</p>
            </div>
          </article>
        </div>

        <div v-else-if="effectiveMode === 'game'" class="quest-stage">
          <div class="quest-hud">
            <span>Game Session</span>
            <strong>{{ Object.values(completed).filter(Boolean).length }}/3</strong>
          </div>
          <div class="quest-map">
            <button
              v-for="(label, index) in ['玩法设定', '核心回合', 'Boss 挑战']"
              :key="label"
              class="quest-node"
              :class="{ 'is-complete': completed[itemKey(index)], 'is-active': selectedIndex === index }"
              @click="selectItem(Math.min(index, practiceItems.length - 1))"
            >
              <span class="quest-orb">
                <Trophy v-if="completed[itemKey(index)]" :size="18" aria-hidden="true" />
                <Gamepad2 v-else :size="18" aria-hidden="true" />
              </span>
              <span>
                <strong>{{ label }}</strong>
                <small>{{ practiceItems[Math.min(index, practiceItems.length - 1)]?.prompt }}</small>
              </span>
              <em>+XP</em>
            </button>
          </div>
          <article class="quest-detail">
            <p class="text-xs font-black uppercase soft-text">当前挑战</p>
            <h3>{{ currentItem?.prompt }}</h3>
            <p class="mt-3 whitespace-pre-wrap text-sm leading-7 muted-text">
              {{ currentItem?.expected_output ?? task.expected_outcome }}
            </p>
            <button class="primary-button mt-5" @click="completeIndex(selectedIndex)">
              <CheckCircle2 :size="16" aria-hidden="true" />
              完成这一回合
            </button>
          </article>
        </div>

        <div v-else-if="effectiveMode === 'podcast'" class="podcast-deck">
          <div class="podcast-disc">
            <Volume2 :size="30" aria-hidden="true" />
          </div>
          <div>
            <p class="text-xs font-black uppercase soft-text">播客脚本</p>
            <h3 class="mt-2 text-xl font-black">{{ task.title }}</h3>
            <p class="mt-3 text-sm leading-7 muted-text">{{ currentItem?.prompt ?? task.description }}</p>
          </div>
          <div class="podcast-controls">
            <button class="primary-button" @click="togglePlayback">
              <Pause v-if="isPlaying" :size="16" aria-hidden="true" />
              <Play v-else :size="16" aria-hidden="true" />
              {{ isPlaying ? '暂停' : '播放' }}
            </button>
            <button class="text-button" @click="emitProgress(100)">
              <CheckCircle2 :size="16" aria-hidden="true" />
              听完本段
            </button>
            <div class="podcast-bar" aria-hidden="true">
              <span :style="{ width: `${audioProgress}%` }"></span>
            </div>
          </div>
          <section class="transcript-list">
            <article v-for="(item, index) in practiceItems" :key="itemKey(index)" class="transcript-card">
              <div class="flex items-center justify-between gap-3">
                <span class="studio-mini-chip">{{ item.type }}</span>
                <span class="text-xs font-black soft-text">Part {{ index + 1 }}</span>
              </div>
              <p class="mt-4 whitespace-pre-wrap text-base font-bold leading-8">{{ item.prompt }}</p>
              <p class="mt-4 whitespace-pre-wrap text-sm leading-7 muted-text">{{ item.expected_output }}</p>
            </article>
          </section>
        </div>

        <div v-else-if="effectiveMode === 'project_lab'" class="grid gap-3">
          <button
            v-for="(label, index) in ['定义交付物', '完成核心功能', '写验收标准']"
            :key="label"
            class="project-step"
            :class="{ 'is-complete': completed[itemKey(index)] }"
            @click="completeIndex(index)"
          >
            <CheckCircle2 :size="18" aria-hidden="true" />
            <span>
              <strong>{{ label }}</strong>
              <small>{{ practiceItems[Math.min(index, practiceItems.length - 1)]?.expected_output ?? task.expected_outcome }}</small>
            </span>
          </button>
        </div>

        <div v-else-if="effectiveMode === 'memory'" class="flashcard-shell">
          <button class="flashcard" @click="toggleReference(selectedIndex)">
            <span class="text-xs font-black uppercase soft-text">Flashcard {{ selectedIndex + 1 }}</span>
            <strong>
              {{ revealedAnswers[itemKey(selectedIndex)] ? currentItem?.expected_output : currentItem?.prompt }}
            </strong>
            <small>{{ revealedAnswers[itemKey(selectedIndex)] ? '点击切回正面' : '点击查看背面解释' }}</small>
          </button>
          <div class="flex flex-wrap items-center justify-between gap-2">
            <button class="text-button" @click="selectItem((selectedIndex - 1 + practiceItems.length) % practiceItems.length)">
              上一张
            </button>
            <button class="primary-button" @click="completeIndex(selectedIndex)">掌握本张</button>
            <button class="text-button" @click="selectItem((selectedIndex + 1) % practiceItems.length)">
              下一张
            </button>
          </div>
        </div>

        <div v-else-if="effectiveMode === 'video' || effectiveMode === 'cinematic'" class="storyboard">
          <div class="storyboard-screen">
            <span>Scene {{ selectedIndex + 1 }}</span>
            <h3>{{ currentItem?.type || '学习镜头' }}</h3>
            <p>{{ currentItem?.prompt }}</p>
          </div>
          <div class="storyboard-note">{{ currentItem?.expected_output }}</div>
          <button class="primary-button w-full" @click="completeIndex(selectedIndex)">
            <CheckCircle2 :size="16" aria-hidden="true" />
            完成当前镜头
          </button>
        </div>

        <div v-else-if="effectiveMode === 'mentor'" class="mentor-room">
          <div class="mentor-bubble">
            <BookOpen :size="16" aria-hidden="true" />
            <span>{{ currentItem?.prompt }}</span>
          </div>
          <div class="mentor-bubble is-user">
            <span>我先尝试用自己的话回答，再标记哪里卡住。</span>
          </div>
          <div class="mentor-bubble">
            <MessageCircleQuestion :size="16" aria-hidden="true" />
            <span>{{ currentItem?.expected_output ?? task.expected_outcome }}</span>
          </div>
          <button class="primary-button" @click="completeIndex(selectedIndex)">完成本轮对话</button>
        </div>
      </section>

      <section v-else-if="activeTab === 'practice'" class="grid gap-3 p-5">
        <article v-for="(item, index) in practiceItems" :key="itemKey(index)" class="practice-card">
          <div class="flex items-center justify-between gap-3">
            <span class="studio-mini-chip">{{ item.type }}</span>
            <span class="text-xs font-bold soft-text">#{{ index + 1 }}</span>
          </div>
          <p class="mt-3 text-sm font-semibold leading-6">{{ item.prompt }}</p>
          <p class="mt-3 text-xs leading-5 muted-text">{{ item.expected_output }}</p>
          <button
            class="text-button mt-4"
            :class="{ 'is-complete': completed[itemKey(index)] }"
            @click="completeIndex(index)"
          >
            <CheckCircle2 :size="16" aria-hidden="true" />
            {{ completed[itemKey(index)] ? '已完成' : '完成这一项' }}
          </button>
        </article>
      </section>

      <section v-else class="grid gap-4 p-5">
        <div class="review-card">
          <p class="text-xs font-black uppercase soft-text">学习反馈</p>
          <h3 class="mt-2 text-xl font-black">系统会根据反馈调整后续体验</h3>
          <p class="mt-3 text-sm leading-7 muted-text">
            如果你点“没理解”，后续会增加导师追问、播客解释和例题拆解；如果你点“多练题”，路线会提高刷题和游戏化练习比例。
          </p>
        </div>
        <button class="text-button w-full" @click="resetStudioState">
          <RotateCcw :size="16" aria-hidden="true" />
          重置当前体验状态
        </button>
      </section>
    </template>
  </section>
</template>
