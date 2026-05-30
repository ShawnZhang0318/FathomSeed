import { reactive } from 'vue'
import { listQueuedFeedbackEvents, syncQueuedFeedbackEvents } from '../services/offlineQueue'

export const offlineQueueStore = reactive({
  queuedCount: 0,
  syncing: false,
  async refresh() {
    this.queuedCount = (await listQueuedFeedbackEvents()).length
  },
  async sync() {
    if (this.syncing || !navigator.onLine) return
    this.syncing = true
    try {
      await syncQueuedFeedbackEvents()
      await this.refresh()
    } finally {
      this.syncing = false
    }
  }
})

