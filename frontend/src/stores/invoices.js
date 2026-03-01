import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../api'

export const useInvoicesStore = defineStore('invoices', () => {
  const invoices = ref([])
  const loading = ref(false)

  async function fetchInvoices(status = '') {
    loading.value = true
    try {
      const params = status ? `?status=${status}` : ''
      invoices.value = (await api(`/api/invoices${params}`)) || []
    } finally {
      loading.value = false
    }
  }

  async function createInvoice(data) {
    return api('/api/invoices', { method: 'POST', body: JSON.stringify(data) })
  }

  async function updateInvoice(id, data) {
    return api(`/api/invoices/${id}`, { method: 'PUT', body: JSON.stringify(data) })
  }

  async function deleteInvoice(id) {
    await api(`/api/invoices/${id}`, { method: 'DELETE' })
  }

  return { invoices, loading, fetchInvoices, createInvoice, updateInvoice, deleteInvoice }
})
