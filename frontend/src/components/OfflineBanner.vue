<script setup lang="ts">
import { CloudOff, RefreshCcw, Wifi } from 'lucide-vue-next'
import { useOnline } from '@vueuse/core'
import { onMounted, watch } from 'vue'
import { offlineQueueStore } from '../stores/offlineQueueStore'

const online = useOnline()

onMounted(() => {
  offlineQueueStore.refresh()
  if (online.value) {
    offlineQueueStore.sync()
  }
})

watch(online, (value) => {
  if (value) {
    offlineQueueStore.sync()
  }
})
</script>

<template>
  <div
    v-if="!online || offlineQueueStore.queuedCount > 0"
    class="border-b backdrop-blur"
    style="border-color: var(--line); background: color-mix(in srgb, var(--surface) 64%, transparent)"
  >
    <div class="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-2 px-4 py-2 text-sm">
      <span class="flex items-center gap-2 muted-text">
        <Wifi v-if="online" :size="16" class="text-emerald-500" aria-hidden="true" />
        <CloudOff v-else :size="16" class="text-coral" aria-hidden="true" />
        {{ online ? '在线' : '离线' }}
      </span>
      <button
        class="text-button min-h-8 px-3 py-1 text-xs"
        :disabled="!online || offlineQueueStore.syncing || offlineQueueStore.queuedCount === 0"
        @click="offlineQueueStore.sync()"
      >
        <RefreshCcw :size="14" aria-hidden="true" />
        同步 {{ offlineQueueStore.queuedCount }}
      </button>
    </div>
  </div>
</template>
