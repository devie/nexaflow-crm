import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../api'

export const useContactsStore = defineStore('contacts', () => {
  const contacts = ref([])
  const loading = ref(false)

  async function fetchContacts(search = '') {
    loading.value = true
    try {
      const params = search ? `?search=${encodeURIComponent(search)}` : ''
      contacts.value = (await api(`/api/contacts${params}`)) || []
    } finally {
      loading.value = false
    }
  }

  async function createContact(data) {
    return api('/api/contacts', { method: 'POST', body: JSON.stringify(data) })
  }

  async function updateContact(id, data) {
    return api(`/api/contacts/${id}`, { method: 'PUT', body: JSON.stringify(data) })
  }

  async function deleteContact(id) {
    await api(`/api/contacts/${id}`, { method: 'DELETE' })
  }

  return { contacts, loading, fetchContacts, createContact, updateContact, deleteContact }
})
