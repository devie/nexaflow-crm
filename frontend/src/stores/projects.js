import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../api'

export const useProjectsStore = defineStore('projects', () => {
  const projects = ref([])
  const loading = ref(false)

  async function fetchProjects(status = '') {
    loading.value = true
    try {
      const params = status ? `?status=${status}` : ''
      projects.value = (await api(`/api/projects${params}`)) || []
    } finally {
      loading.value = false
    }
  }

  async function createProject(data) {
    return api('/api/projects', { method: 'POST', body: JSON.stringify(data) })
  }

  async function updateProject(id, data) {
    return api(`/api/projects/${id}`, { method: 'PUT', body: JSON.stringify(data) })
  }

  async function deleteProject(id) {
    await api(`/api/projects/${id}`, { method: 'DELETE' })
  }

  return { projects, loading, fetchProjects, createProject, updateProject, deleteProject }
})
