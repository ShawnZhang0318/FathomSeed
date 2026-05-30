import type { FeedbackEvent } from '../types'
import { api } from './api'

const DB_NAME = 'fullmind-offline'
const STORE = 'feedback-events'
const VERSION = 1

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, VERSION)
    request.onupgradeneeded = () => {
      const db = request.result
      if (!db.objectStoreNames.contains(STORE)) {
        db.createObjectStore(STORE, { keyPath: 'id' })
      }
    }
    request.onerror = () => reject(request.error)
    request.onsuccess = () => resolve(request.result)
  })
}

export async function queueFeedbackEvent(event: FeedbackEvent): Promise<void> {
  const db = await openDb()
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite')
    tx.objectStore(STORE).put(event)
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
  db.close()
}

export async function listQueuedFeedbackEvents(): Promise<FeedbackEvent[]> {
  const db = await openDb()
  const events = await new Promise<FeedbackEvent[]>((resolve, reject) => {
    const tx = db.transaction(STORE, 'readonly')
    const request = tx.objectStore(STORE).getAll()
    request.onsuccess = () => resolve(request.result as FeedbackEvent[])
    request.onerror = () => reject(request.error)
  })
  db.close()
  return events
}

export async function clearQueuedFeedbackEvents(ids: string[]): Promise<void> {
  const db = await openDb()
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite')
    const store = tx.objectStore(STORE)
    ids.forEach((id) => store.delete(id))
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
  db.close()
}

export async function syncQueuedFeedbackEvents(): Promise<number> {
  const events = await listQueuedFeedbackEvents()
  if (events.length === 0 || !navigator.onLine) {
    return 0
  }
  const result = await api.syncFeedbackEvents(events)
  const syncedIds = [...result.accepted.map((event) => event.id), ...result.duplicates]
  await clearQueuedFeedbackEvents(syncedIds)
  return syncedIds.length
}

export function makeClientEventId(): string {
  if ('randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

