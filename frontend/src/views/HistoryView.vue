<script setup lang="ts">
import { planStore } from '../stores/planStore'
</script>

<template>
  <section class="mx-auto max-w-6xl px-4 py-5">
    <div v-if="planStore.plan" class="rounded-md border border-line bg-white p-4">
      <div class="text-sm font-semibold text-ink">{{ planStore.plan.title }}</div>
      <div class="mt-1 text-sm text-stone-600">V{{ planStore.plan.version }}</div>
    </div>
  </section>
</template>

