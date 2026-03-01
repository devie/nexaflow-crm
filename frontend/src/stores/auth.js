import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api, getToken, setToken, clearToken } from '../api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(!!getToken())

  async function login(email, password) {
    const data = await api('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    if (data?.access_token) {
      setToken(data.access_token)
      isAuthenticated.value = true
      await fetchUser()
    }
    return data
  }

  async function register(email, name, password) {
    const data = await api('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, name, password }),
    })
    if (data?.access_token) {
      setToken(data.access_token)
      isAuthenticated.value = true
      await fetchUser()
    }
    return data
  }

  async function fetchUser() {
    try {
      user.value = await api('/api/auth/me')
    } catch {
      user.value = null
    }
  }

  async function updateUser(data) {
    const updated = await api('/api/auth/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    })
    if (updated) user.value = updated
    return updated
  }

  function logout() {
    clearToken()
    user.value = null
    isAuthenticated.value = false
  }

  return { user, isAuthenticated, login, register, fetchUser, updateUser, logout }
})
