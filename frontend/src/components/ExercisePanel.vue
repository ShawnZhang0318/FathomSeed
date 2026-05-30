<script setup lang="ts">
import {
  BookOpen,
  Brain,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
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
  Target,
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
const isPlaying = ref(false)
const podcastProgress = ref(18)
const flashIndex = ref(0)
const flashFlipped = ref(false)
const activeQuestionIndex = ref(0)
const selectedQuestIndex = ref(0)
const selectedFrame = ref(0)
const checkedObjectives = ref<Record<string, boolean>>({})
const answers = ref<Record<string, string>>({})
const revealedAnswers = ref<Record<string, boolean>>({})
const mixedMode = ref('drill')
let playbackTimer: ReturnType<typeof setInterval> | null = null

const experienceMeta: Record<string, ExperienceMeta> = {
  drill: {
    label: '题库训练场',
    eyebrow: '题库训练',
    description: '用连续小题建立手感，再用错因记录反推理解漏洞。',
    icon: Dumbbell
  },
  game: {
    label: '学习游戏舱',
    eyebrow: '互动游戏',
    description: '根据知识点生成模拟实验、情景选择、角色扮演、策略推演或解谜挑战。',
    icon: Gamepad2
  },
  quest: {
    label: '学习游戏舱',
    eyebrow: '互动游戏',
    description: '根据知识点生成模拟实验、情景选择、角色扮演、策略推演或解谜挑战。',
    icon: Gamepad2
  },
  podcast: {
    label: '播客讲解舱',
    eyebrow: '播客学习',
    description: '把抽象概念改写成能听懂的故事、类比和口语化复盘。',
    icon: Headphones
  },
  video: {
    label: '短视频剧场',
    eyebrow: '微电影学习',
    description: '把历史、人物、诗词或案例变成短视频脚本，用画面和情绪帮助记忆。',
    icon: Clapperboard
  },
  cinematic: {
    label: '电影故事线',
    eyebrow: '故事学习',
    description: '用角色、冲突和反转承载概念，让知识点进入情境记忆。',
    icon: Film
  },
  project_lab: {
    label: '项目实验室',
    eyebrow: '项目工坊',
    description: '用一个可交付的小作品，把今天的知识点变成真实产出。',
    icon: FolderGit2
  },
  mentor: {
    label: '导师对话',
    eyebrow: '导师引导',
    description: '通过追问、提示和反问，检查你是不是真的理解了。',
    icon: MessageCircleQuestion
  },
  memory: {
    label: '闪卡记忆馆',
    eyebrow: '记忆卡组',
    description: '把知识拆成可翻转卡片，用主动回忆稳住长期记忆。',
    icon: Brain
  },
  mixed: {
    label: '混合学习舱',
    eyebrow: '自适应混合',
    description: '在讲解、练习、项目和复盘之间自动切换节奏。',
    icon: Sparkles
  }
}

const mode = computed(() => props.task?.experience_mode || props.task?.method_code || 'mixed')
const canonicalMode = (value: string) => (value === 'quest' ? 'game' : value)
const effectiveMode = computed(() => canonicalMode(mode.value === 'mixed' ? mixedMode.value : mode.value))
const meta = computed(() => experienceMeta[effectiveMode.value] ?? experienceMeta.mixed)
const exerciseItems = computed(() => props.exercises?.exercises ?? [])
const activityItems = computed(() => {
  const items = exerciseItems.value.length ? exerciseItems.value : fallbackItems.value
  if (mode.value !== 'mixed') return items
  const filtered = items.filter((item) => itemMatchesMode(item, effectiveMode.value))
  return filtered.length ? filtered : fallbackItems.value
})
const primaryExercise = computed(() => exerciseItems.value[0])

const providerLabel = computed(() => {
  const provider = props.exercises?.provider ?? ''
  if (provider.includes('question') || provider.includes('experience')) return '内置体验库'
  if (provider.includes('template')) return '模板生成'
  if (provider.includes('llm')) return '模型增强'
  return '本地内容引擎'
})

const flashcards = computed(() => {
  const source = activityItems.value
  return source.slice(0, 5).map((item, index) => ({
    front: item.prompt,
    back: item.expected_output,
    hint: item.hints[0] ?? '先用自己的话说出关键关系，再看答案。',
    label: `第 ${index + 1} 张`
  }))
})

const storyboardFrames = computed(() => {
  const topic = props.task?.title ?? '今天的知识点'
  const items = activityItems.value
  if (effectiveMode.value === 'video') {
    return [
      {
        title: '片头画面',
        body: `用一个有情绪的画面打开「${topic}」。`,
        note: items[0]?.prompt ?? '先让学习者看到场景，再进入知识点。'
      },
      {
        title: '人物与场景',
        body: '放入人物、物件、地点或时代背景，让知识有落点。',
        note: items[0]?.hints[0] ?? '历史、人物、诗词和案例都需要一个可记住的视觉锚点。'
      },
      {
        title: '关键冲突',
        body: '用一次选择、误解、转折或情绪变化推动理解。',
        note: items[1]?.prompt ?? '冲突不一定夸张，但必须能解释知识点为什么重要。'
      },
      {
        title: '记忆锚点',
        body: '设计一句台词或一个画面符号，让用户以后能想起知识线索。',
        note: items[1]?.expected_output ?? '锚点要短、鲜明、能回扣知识。'
      },
      {
        title: '结尾回望',
        body: '用 3 个问题收束短片：发生了什么？为什么？我记住了什么？',
        note: items[2]?.prompt ?? '结尾不是总结大道理，而是帮用户主动回忆。'
      }
    ]
  }
  const base = [
    {
      title: '开场钩子',
      body: `用一个真实问题引出「${topic}」。`,
      note: items[0]?.prompt ?? '先制造一个让人想继续看的疑问。'
    },
    {
      title: '概念可视化',
      body: '把抽象关系画成一个动作、空间或角色关系。',
      note: items[0]?.hints[0] ?? '只保留一个核心概念，不要一次讲太多。'
    },
    {
      title: '误区反转',
      body: '展示一个常见错误，再让正确方法解决冲突。',
      note: items[1]?.prompt ?? '让错误有代价，观众才会记住。'
    },
    {
      title: '练习收束',
      body: '给出一个 3 分钟可完成的小挑战。',
      note: items[1]?.expected_output ?? '让学习者立刻做一次迁移。'
    }
  ]
  return base
})

const questSteps = computed(() => {
  const items = activityItems.value
  return [
    {
      key: 'setup',
      title: '玩法设定',
      body: items[0]?.prompt ?? '先判断今天最适合哪种游戏形态：模拟、选择、角色扮演、策略推演还是解谜。',
      reward: '理解目标'
    },
    {
      key: 'loop',
      title: '核心回合',
      body: items[0]?.hints[0] ?? '完成一轮操作、选择或实验，并记录系统反馈。',
      reward: '形成反馈'
    },
    {
      key: 'challenge',
      title: '挑战任务',
      body: items[1]?.prompt ?? props.task?.expected_outcome ?? '独立完成一个综合挑战。',
      reward: '完成复盘'
    }
  ]
})

const projectMilestones = computed(() => {
  const title = props.task?.title ?? '小项目'
  return [
    { key: 'scope', title: '定义交付物', body: `把「${title}」收敛成 30 分钟内能完成的版本。` },
    { key: 'build', title: '完成核心功能', body: primaryExercise.value?.prompt ?? '先做最小闭环，再补细节。' },
    { key: 'accept', title: '写验收标准', body: primaryExercise.value?.expected_output ?? '列出 3 条可以判断完成的标准。' }
  ]
})

const fallbackItems = computed<ExerciseItem[]>(() => [
  {
    type: effectiveMode.value,
    prompt: props.task?.description ?? '选择左侧任务后，这里会展示对应的学习体验。',
    expected_output: props.task?.expected_outcome ?? '完成一次可记录、可反馈、可调整的学习动作。',
    hints: ['先完成最小动作，再根据反馈调整下一步。']
  }
])

const practiceItems = computed(() => activityItems.value.length ? activityItems.value : fallbackItems.value)
const currentPracticeItem = computed(() => practiceItems.value[activeQuestionIndex.value] ?? practiceItems.value[0])
const currentQuestStep = computed(() => questSteps.value[selectedQuestIndex.value] ?? questSteps.value[0])

const completedQuestCount = computed(() =>
  questSteps.value.filter((step) => checkedObjectives.value[step.key]).length
)

const currentFlashcard = computed(() => flashcards.value[flashIndex.value] ?? flashcards.value[0])
const normalizedProgress = computed(() => Math.max(0, Math.min(100, props.progress ?? 0)))
const panelClass = computed(() => [
  'studio-panel overflow-hidden',
  props.layout === 'page' ? 'activity-panel' : 'sticky top-24'
])
const mixedModeOptions = [
  { code: 'video', label: '短视频', description: '微电影、人物小传或意象短片', icon: Clapperboard },
  { code: 'cinematic', label: '故事', description: '用剧情理解概念', icon: Film },
  { code: 'mentor', label: '对话', description: '追问、复述、诊断', icon: MessageCircleQuestion },
  { code: 'drill', label: '刷题', description: '进入可作答题库', icon: Dumbbell },
  { code: 'game', label: '游戏', description: '模拟、选择、解谜或角色扮演', icon: Gamepad2 },
  { code: 'podcast', label: '播客', description: '阅读讲解文字稿', icon: Headphones },
  { code: 'memory', label: '闪卡', description: '翻卡主动回忆', icon: Brain },
  { code: 'project_lab', label: '项目', description: '完成交付物步骤', icon: FolderGit2 }
]

function resetStudioState() {
  activeTab.value = 'experience'
  mixedMode.value = mode.value === 'mixed' ? 'drill' : canonicalMode(mode.value)
  flashIndex.value = 0
  flashFlipped.value = false
  activeQuestionIndex.value = 0
  selectedQuestIndex.value = 0
  selectedFrame.value = 0
  checkedObjectives.value = hydratedObjectives()
  stopPlayback()
  podcastProgress.value = Math.max(18, normalizedProgress.value)
}

function toggleObjective(key: string) {
  const nextObjectives = {
    ...checkedObjectives.value,
    [key]: !checkedObjectives.value[key]
  }
  checkedObjectives.value = nextObjectives
  const total = effectiveMode.value === 'project_lab' ? projectMilestones.value.length : questSteps.value.length
  const completeCount = Object.values(nextObjectives).filter(Boolean).length
  emitProgress(Math.round((completeCount / Math.max(1, total)) * 100))
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
    podcastProgress.value = Math.min(100, podcastProgress.value + 2)
    if (podcastProgress.value % 10 === 0 || podcastProgress.value >= 100) {
      emitProgress(podcastProgress.value)
    }
    if (podcastProgress.value >= 100) stopPlayback()
  }, 700)
}

function nextFlashcard() {
  flashIndex.value = (flashIndex.value + 1) % flashcards.value.length
  flashFlipped.value = false
  emitProgress(Math.max(normalizedProgress.value, Math.round(((flashIndex.value + 1) / flashcards.value.length) * 100)))
}

function previousFlashcard() {
  flashIndex.value = (flashIndex.value - 1 + flashcards.value.length) % flashcards.value.length
  flashFlipped.value = false
}

function nextFrame() {
  selectedFrame.value = (selectedFrame.value + 1) % storyboardFrames.value.length
  emitProgress(Math.max(normalizedProgress.value, Math.round(((selectedFrame.value + 1) / storyboardFrames.value.length) * 100)))
}

function previousFrame() {
  selectedFrame.value = (selectedFrame.value - 1 + storyboardFrames.value.length) % storyboardFrames.value.length
}

function emitProgress(progressPercent: number) {
  if (!props.task) return
  emit('progress', {
    task: props.task,
    progressPercent: Math.max(0, Math.min(100, Math.round(progressPercent)))
  })
}

function completeCurrentPractice(index: number, total: number) {
  checkedObjectives.value = {
    ...checkedObjectives.value,
    [`practice-${index}`]: true
  }
  const completed = Object.keys(checkedObjectives.value).filter((key) => key.startsWith('practice-')).length
  emitProgress(Math.round((completed / Math.max(1, total)) * 100))
}

function selectQuestion(index: number) {
  activeQuestionIndex.value = Math.max(0, Math.min(index, practiceItems.value.length - 1))
}

function nextQuestion() {
  selectQuestion((activeQuestionIndex.value + 1) % practiceItems.value.length)
}

function previousQuestion() {
  selectQuestion((activeQuestionIndex.value - 1 + practiceItems.value.length) % practiceItems.value.length)
}

function saveActiveAnswer() {
  saveAnswer(activeQuestionIndex.value, practiceItems.value.length)
}

function selectQuest(index: number) {
  selectedQuestIndex.value = Math.max(0, Math.min(index, questSteps.value.length - 1))
}

function completeSelectedQuest() {
  if (!currentQuestStep.value) return
  toggleObjective(currentQuestStep.value.key)
}

function completeMentorTurn(turn: number) {
  checkedObjectives.value = {
    ...checkedObjectives.value,
    [`mentor-${turn}`]: true
  }
  const completed = Object.keys(checkedObjectives.value).filter((key) => key.startsWith('mentor-')).length
  emitProgress(Math.round((completed / 3) * 100))
}

function finishPodcast() {
  podcastProgress.value = 100
  emitProgress(100)
  stopPlayback()
}

function hydratedObjectives(): Record<string, boolean> {
  const progress = normalizedProgress.value
  if (effectiveMode.value === 'game') {
    return hydrateKeys(questSteps.value.map((step) => step.key), progress)
  }
  if (effectiveMode.value === 'project_lab') {
    return hydrateKeys(projectMilestones.value.map((milestone) => milestone.key), progress)
  }
  if (effectiveMode.value === 'mentor') {
    return hydrateKeys(['mentor-1', 'mentor-2', 'mentor-3'], progress)
  }
  const source = activityItems.value
  return hydrateKeys(source.map((_, index) => `practice-${index}`), progress)
}

function itemKey(item: ExerciseItem, index: number): string {
  return `${props.task?.id ?? 'task'}-${effectiveMode.value}-${item.type}-${index}`
}

function saveAnswer(index: number, total: number) {
  completeCurrentPractice(index, total)
}

function toggleReference(item: ExerciseItem, index: number) {
  const key = itemKey(item, index)
  revealedAnswers.value = {
    ...revealedAnswers.value,
    [key]: !revealedAnswers.value[key]
  }
}

function itemMatchesMode(item: ExerciseItem, targetMode: string): boolean {
  const type = item.type.toLowerCase()
  const prompt = item.prompt.toLowerCase()
  const haystack = `${type} ${prompt}`
  const groups: Record<string, string[]> = {
    video: ['video', 'storyboard', 'microfilm', 'short', '短视频', '微电影', '人物', '生平', '诗词', '意象', '视频'],
    cinematic: ['cinematic', 'story', 'movie', '故事', '电影'],
    mentor: ['mentor', 'dialogue', 'probe', '导师', '对话', '追问'],
    drill: ['bank', 'foundation', 'transfer', 'quiz', '题库', '基础题', '单选', '填空', '改错'],
    game: ['game', 'quest', 'level', 'boss', '游戏', '模拟', '实验', '情景', '选择', '角色', '解谜', '关卡'],
    podcast: ['podcast', '播客', '文字稿'],
    memory: ['memory', 'flash', 'recall', '闪卡', '回忆'],
    project_lab: ['project', '项目', 'brief', '验收']
  }
  return (groups[targetMode] ?? []).some((token) => haystack.includes(token))
}

function switchMixedMode(nextMode: string) {
  mixedMode.value = nextMode
  activeTab.value = 'experience'
  activeQuestionIndex.value = 0
  selectedQuestIndex.value = 0
  flashIndex.value = 0
  selectedFrame.value = 0
  checkedObjectives.value = hydratedObjectives()
}

function hydrateKeys(keys: string[], progress: number): Record<string, boolean> {
  const completed = Math.floor((keys.length * progress) / 100)
  return keys.reduce<Record<string, boolean>>((result, key, index) => {
    result[key] = index < completed
    return result
  }, {})
}

watch(() => props.task?.id, resetStudioState)
watch(() => props.progress, () => {
  if (!props.task) return
  podcastProgress.value = Math.max(podcastProgress.value, normalizedProgress.value)
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
          左侧路线里的每个任务都会打开对应的体验空间：题库、游戏、闪卡、播客、短视频或项目工坊。
        </p>
      </div>
    </div>

    <template v-else>
      <section class="studio-hero" :class="`mode-${effectiveMode}`">
        <div class="flex items-start justify-between gap-4">
          <div class="min-w-0">
            <p class="studio-eyebrow">{{ meta.eyebrow }}</p>
            <h2 class="mt-2 text-2xl font-black tracking-[-0.035em]">{{ meta.label }}</h2>
            <p class="mt-2 text-sm leading-6 text-white/76">{{ meta.description }}</p>
          </div>
          <span class="studio-hero-icon">
            <component :is="meta.icon" :size="24" aria-hidden="true" />
          </span>
        </div>
        <div class="mt-6 rounded-[22px] border border-white/14 bg-white/10 p-4 backdrop-blur">
          <p class="text-xs font-bold uppercase tracking-[0.16em] text-white/54">当前训练</p>
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
            <p class="text-xs font-black uppercase tracking-[0.16em] soft-text">题目列表</p>
            <button
              v-for="(item, index) in practiceItems"
              :key="itemKey(item, index)"
              class="question-pill"
              :class="{ 'is-active': activeQuestionIndex === index, 'is-complete': checkedObjectives[`practice-${index}`] }"
              @click="selectQuestion(index)"
            >
              <span>第 {{ index + 1 }} 题</span>
              <CheckCircle2 v-if="checkedObjectives[`practice-${index}`]" :size="14" aria-hidden="true" />
            </button>
          </aside>

          <article class="answer-main">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <span class="studio-mini-chip">{{ currentPracticeItem.type }}</span>
              <span class="text-sm font-black soft-text">{{ activeQuestionIndex + 1 }} / {{ practiceItems.length }}</span>
            </div>
            <h3 class="question-prompt">{{ currentPracticeItem.prompt }}</h3>
            <div v-if="currentPracticeItem.hints.length" class="flex flex-wrap gap-2">
              <span v-for="hint in currentPracticeItem.hints" :key="hint" class="studio-mini-chip">{{ hint }}</span>
            </div>
            <textarea
              v-model="answers[itemKey(currentPracticeItem, activeQuestionIndex)]"
              class="answer-textarea"
              rows="9"
              placeholder="在这里写下你的答案、代码、推理过程或错因记录。"
            ></textarea>
            <div class="flex flex-wrap items-center gap-3">
              <button class="primary-button" @click="saveActiveAnswer">
                <Save :size="16" aria-hidden="true" />
                保存本题
              </button>
              <button class="text-button" @click="toggleReference(currentPracticeItem, activeQuestionIndex)">
                <Eye :size="16" aria-hidden="true" />
                {{ revealedAnswers[itemKey(currentPracticeItem, activeQuestionIndex)] ? '收起参考' : '查看参考' }}
              </button>
              <button class="icon-button" @click="previousQuestion">
                <ChevronLeft :size="16" aria-hidden="true" />
                上一题
              </button>
              <button class="icon-button" @click="nextQuestion">
                下一题
                <ChevronRight :size="16" aria-hidden="true" />
              </button>
            </div>
            <div v-if="revealedAnswers[itemKey(currentPracticeItem, activeQuestionIndex)]" class="reference-panel">
              <p class="text-xs font-black uppercase tracking-[0.16em] soft-text">参考答案 / 解析</p>
              <p class="mt-3 whitespace-pre-wrap text-sm leading-7">{{ currentPracticeItem.expected_output }}</p>
            </div>
          </article>
        </div>

        <div v-else-if="effectiveMode === 'game'" class="quest-stage">
          <div class="quest-hud">
            <span>Game Session</span>
            <strong>{{ completedQuestCount }}/{{ questSteps.length }}</strong>
          </div>
          <div class="quest-map">
            <button
              v-for="(step, index) in questSteps"
              :key="step.key"
              class="quest-node"
              :class="{ 'is-complete': checkedObjectives[step.key], 'is-active': selectedQuestIndex === index }"
              @click="selectQuest(index)"
            >
              <span class="quest-orb">
                <Trophy v-if="checkedObjectives[step.key]" :size="18" aria-hidden="true" />
                <Target v-else :size="18" aria-hidden="true" />
              </span>
              <span>
                <strong>{{ step.title }}</strong>
                <small>{{ step.body }}</small>
              </span>
              <em>{{ step.reward }}</em>
            </button>
          </div>
          <article class="quest-detail">
            <p class="text-xs font-black uppercase tracking-[0.16em] soft-text">当前游戏任务</p>
            <h3>{{ currentQuestStep.title }}</h3>
            <p class="mt-3 whitespace-pre-wrap text-sm leading-7 muted-text">{{ currentQuestStep.body }}</p>
            <div v-if="activityItems[selectedQuestIndex]?.hints?.length" class="mt-4 flex flex-wrap gap-2">
              <span v-for="hint in activityItems[selectedQuestIndex].hints" :key="hint" class="studio-mini-chip">{{ hint }}</span>
            </div>
            <div class="reference-panel mt-5">
              <p class="text-xs font-black uppercase tracking-[0.16em] soft-text">完成目标</p>
              <p class="mt-3 whitespace-pre-wrap text-sm leading-7">
                {{ activityItems[selectedQuestIndex]?.expected_output ?? task.expected_outcome }}
              </p>
            </div>
            <button class="primary-button mt-5" @click="completeSelectedQuest">
              <CheckCircle2 :size="16" aria-hidden="true" />
              {{ checkedObjectives[currentQuestStep.key] ? '取消完成' : '完成这一局' }}
            </button>
          </article>
        </div>

        <div v-else-if="effectiveMode === 'memory'" class="flashcard-shell">
          <button class="flashcard" :class="{ 'is-flipped': flashFlipped }" @click="flashFlipped = !flashFlipped">
            <span class="text-xs font-black uppercase tracking-[0.18em] soft-text">
              {{ currentFlashcard?.label }}
            </span>
            <strong>{{ flashFlipped ? currentFlashcard?.back : currentFlashcard?.front }}</strong>
            <small>{{ flashFlipped ? currentFlashcard?.hint : '点击卡片查看背面解释' }}</small>
          </button>
          <div class="flex items-center justify-between">
            <button class="icon-button" @click="previousFlashcard">
              <ChevronLeft :size="16" aria-hidden="true" />
            </button>
            <button class="text-button" @click="emitProgress(Math.round(((flashIndex + 1) / flashcards.length) * 100))">
              <CheckCircle2 :size="16" aria-hidden="true" />
              掌握本张
            </button>
            <span class="text-xs font-bold soft-text">{{ flashIndex + 1 }} / {{ flashcards.length }}</span>
            <button class="icon-button" @click="nextFlashcard">
              <ChevronRight :size="16" aria-hidden="true" />
            </button>
          </div>
        </div>

        <div v-else-if="effectiveMode === 'podcast'" class="podcast-deck">
          <div class="podcast-disc">
            <Volume2 :size="30" aria-hidden="true" />
          </div>
          <div>
            <p class="text-xs font-black uppercase tracking-[0.16em] soft-text">播客脚本</p>
            <h3 class="mt-2 text-xl font-black">{{ task.title }}</h3>
            <p class="mt-3 text-sm leading-7 muted-text">
              {{ primaryExercise?.prompt ?? task.description }}
            </p>
          </div>
          <div class="podcast-controls">
            <button class="primary-button" @click="togglePlayback">
              <Pause v-if="isPlaying" :size="16" aria-hidden="true" />
              <Play v-else :size="16" aria-hidden="true" />
              {{ isPlaying ? '暂停' : '播放' }}
            </button>
            <button class="text-button" @click="finishPodcast">
              <CheckCircle2 :size="16" aria-hidden="true" />
              听完本段
            </button>
            <div class="podcast-bar" aria-hidden="true">
              <span :style="{ width: `${podcastProgress}%` }"></span>
            </div>
          </div>
          <section class="transcript-list">
            <article v-for="(item, index) in activityItems" :key="itemKey(item, index)" class="transcript-card">
              <div class="flex items-center justify-between gap-3">
                <span class="studio-mini-chip">{{ item.type }}</span>
                <span class="text-xs font-black soft-text">Part {{ index + 1 }}</span>
              </div>
              <p class="mt-4 whitespace-pre-wrap text-base font-bold leading-8">{{ item.prompt }}</p>
              <p class="mt-4 whitespace-pre-wrap text-sm leading-7 muted-text">{{ item.expected_output }}</p>
            </article>
          </section>
        </div>

        <div v-else-if="effectiveMode === 'video' || effectiveMode === 'cinematic'" class="storyboard">
          <div class="storyboard-screen">
            <span>Scene {{ selectedFrame + 1 }}</span>
            <h3>{{ storyboardFrames[selectedFrame]?.title }}</h3>
            <p>{{ storyboardFrames[selectedFrame]?.body }}</p>
          </div>
          <div class="storyboard-note">
            {{ storyboardFrames[selectedFrame]?.note }}
          </div>
          <button class="primary-button w-full" @click="emitProgress(Math.round(((selectedFrame + 1) / storyboardFrames.length) * 100))">
            <CheckCircle2 :size="16" aria-hidden="true" />
            完成当前镜头
          </button>
          <div class="flex items-center justify-between">
            <button class="icon-button" @click="previousFrame">
              <ChevronLeft :size="16" aria-hidden="true" />
            </button>
            <div class="flex gap-1">
              <button
                v-for="(_, index) in storyboardFrames"
                :key="index"
                class="h-2.5 w-2.5 rounded-full transition"
                :class="index === selectedFrame ? 'bg-indigo-500' : 'bg-slate-300'"
                @click="selectedFrame = index"
              ></button>
            </div>
            <button class="icon-button" @click="nextFrame">
              <ChevronRight :size="16" aria-hidden="true" />
            </button>
          </div>
        </div>

        <div v-else-if="effectiveMode === 'project_lab'" class="grid gap-3">
          <button
            v-for="milestone in projectMilestones"
            :key="milestone.key"
            class="project-step"
            :class="{ 'is-complete': checkedObjectives[milestone.key] }"
            @click="toggleObjective(milestone.key)"
          >
            <CheckCircle2 :size="18" aria-hidden="true" />
            <span>
              <strong>{{ milestone.title }}</strong>
              <small>{{ milestone.body }}</small>
            </span>
          </button>
        </div>

        <div v-else-if="effectiveMode === 'mentor'" class="mentor-room">
          <div class="mentor-bubble is-mentor">
            <BookOpen :size="16" aria-hidden="true" />
            <span>{{ primaryExercise?.prompt ?? '先不用看答案，你会怎样向别人解释这个知识点？' }}</span>
          </div>
          <div class="mentor-bubble is-user">
            <span>我先尝试用自己的话回答，然后标记哪里卡住。</span>
          </div>
          <div class="mentor-bubble is-mentor">
            <MessageCircleQuestion :size="16" aria-hidden="true" />
            <span>{{ primaryExercise?.expected_output ?? task.expected_outcome }}</span>
          </div>
          <div class="grid gap-2 sm:grid-cols-3">
            <button class="text-button" @click="completeMentorTurn(1)">完成回答</button>
            <button class="text-button" @click="completeMentorTurn(2)">完成追问</button>
            <button class="primary-button" @click="completeMentorTurn(3)">完成复述</button>
          </div>
        </div>

        <div v-else class="drill-board">
          <article v-for="(item, index) in (exerciseItems.length ? exerciseItems : fallbackItems)" :key="index">
            <span>第 {{ index + 1 }} 题</span>
            <h3>{{ item.prompt }}</h3>
            <p>{{ item.expected_output }}</p>
            <button
              class="text-button mt-4"
              :class="{ 'is-complete': checkedObjectives[`practice-${index}`] }"
              @click="completeCurrentPractice(index, (exerciseItems.length ? exerciseItems : fallbackItems).length)"
            >
              <CheckCircle2 :size="16" aria-hidden="true" />
              {{ checkedObjectives[`practice-${index}`] ? '已完成' : '完成本题' }}
            </button>
          </article>
        </div>
      </section>

      <section v-else-if="activeTab === 'practice'" class="grid gap-3 p-5">
        <article
          v-for="(item, index) in (exerciseItems.length ? exerciseItems : fallbackItems)"
          :key="`${item.type}-${index}`"
          class="practice-card"
        >
          <div class="flex items-center justify-between gap-3">
            <span class="studio-mini-chip">{{ item.type }}</span>
            <span class="text-xs font-bold soft-text">#{index + 1}</span>
          </div>
          <p class="mt-3 text-sm font-semibold leading-6">{{ item.prompt }}</p>
          <p class="mt-3 text-xs leading-5 muted-text">{{ item.expected_output }}</p>
          <div v-if="item.hints.length" class="mt-3 flex flex-wrap gap-2">
            <span v-for="hint in item.hints" :key="hint" class="studio-mini-chip">{{ hint }}</span>
          </div>
          <button
            class="text-button mt-4"
            :class="{ 'is-complete': checkedObjectives[`practice-${index}`] }"
            @click="completeCurrentPractice(index, (exerciseItems.length ? exerciseItems : fallbackItems).length)"
          >
            <CheckCircle2 :size="16" aria-hidden="true" />
            {{ checkedObjectives[`practice-${index}`] ? '已完成' : '完成这一项' }}
          </button>
        </article>
      </section>

      <section v-else class="grid gap-4 p-5">
        <div class="review-card">
          <p class="text-xs font-black uppercase tracking-[0.16em] soft-text">学习反馈</p>
          <h3 class="mt-2 text-xl font-black">系统会根据你的反馈调整后续体验</h3>
          <p class="mt-3 text-sm leading-7 muted-text">
            如果你点“没理解”，后续会增加导师追问、播客解释和例题拆解；如果你点“多练题”，路线会提高题库和游戏化练习比例。
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
