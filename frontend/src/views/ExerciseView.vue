<script setup lang="ts">
import ExercisePanel from '../components/ExercisePanel.vue'
import { planStore } from '../stores/planStore'
</script>

<template>
  <ExercisePanel
    :task="planStore.selectedTask"
    :exercises="null"
    :loading="false"
    :progress="planStore.selectedTask?.progress_percent ?? 0"
  />
</template>
