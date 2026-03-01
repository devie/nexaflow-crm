import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../api'

export const useDashboardStore = defineStore('dashboard', () => {
  const stats = ref(null)
  const loading = ref(false)

  async function fetchStats() {
    loading.value = true
    try {
      stats.value = await api('/api/dashboard')
    } finally {
      loading.value = false
    }
  }

  return { stats, loading, fetchStats }
})
