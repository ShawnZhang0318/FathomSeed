<script setup lang="ts">
import { BookOpen, CheckCircle2, Dumbbell, Frown, HelpCircle, ThumbsUp } from 'lucide-vue-next'

defineEmits<{
  feedback: [eventType: string]
}>()
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <button class="text-button" title="有帮助" @click="$emit('feedback', 'HELPFUL')">
      <ThumbsUp :size="16" aria-hidden="true" />
      有帮助
    </button>
    <button class="text-button" title="太难了" @click="$emit('feedback', 'TOO_HARD')">
      <Frown :size="16" aria-hidden="true" />
      太难了
    </button>
    <button class="text-button" title="没理解" @click="$emit('feedback', 'NOT_UNDERSTOOD')">
      <HelpCircle :size="16" aria-hidden="true" />
      没理解
    </button>
    <button class="text-button" title="想多练题" @click="$emit('feedback', 'WANT_MORE_PRACTICE')">
      <Dumbbell :size="16" aria-hidden="true" />
      多练题
    </button>
    <button class="text-button" title="想多看讲解" @click="$emit('feedback', 'WANT_MORE_EXPLANATION')">
      <BookOpen :size="16" aria-hidden="true" />
      多讲解
    </button>
    <button class="text-button" title="我理解了" @click="$emit('feedback', 'UNDERSTOOD')">
      <CheckCircle2 :size="16" aria-hidden="true" />
      理解了
    </button>
  </div>
</template>

