<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <Navbar v-if="auth.isAuthenticated" />
    <main :class="auth.isAuthenticated ? 'flex-1 p-6 max-w-6xl mx-auto w-full' : ''">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import Navbar from './components/Navbar.vue'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()

onMounted(() => {
  if (auth.isAuthenticated) auth.fetchUser()
})
</script>
