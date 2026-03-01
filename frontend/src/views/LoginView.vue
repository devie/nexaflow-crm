<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600">
    <div class="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
      <h1 class="text-2xl font-bold text-center mb-1">NexaFlow CRM</h1>
      <p class="text-gray-500 text-center mb-6 text-sm">Manage your clients, projects & invoices</p>

      <div v-if="error" class="bg-red-100 text-red-700 p-2 rounded mb-3 text-sm">{{ error }}</div>

      <input
        v-if="!isLogin"
        v-model="form.name"
        type="text"
        placeholder="Name"
        class="w-full border rounded-lg px-4 py-2 mb-3"
      />
      <input v-model="form.email" type="email" placeholder="Email" class="w-full border rounded-lg px-4 py-2 mb-3" />
      <input
        v-model="form.password"
        type="password"
        placeholder="Password"
        class="w-full border rounded-lg px-4 py-2 mb-4"
        @keyup.enter="submit"
      />

      <button
        @click="submit"
        :disabled="submitting"
        class="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-500 font-medium disabled:opacity-50"
      >
        {{ isLogin ? 'Login' : 'Register' }}
      </button>

      <p class="text-center mt-4 text-sm text-gray-500">
        {{ isLogin ? "Don't have an account?" : 'Already have an account?' }}
        <button @click="isLogin = !isLogin" class="text-indigo-600 font-medium ml-1">
          {{ isLogin ? 'Register' : 'Login' }}
        </button>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const isLogin = ref(true)
const submitting = ref(false)
const error = ref('')
const form = reactive({ email: '', password: '', name: '' })

async function submit() {
  error.value = ''
  submitting.value = true
  try {
    if (isLogin.value) {
      await auth.login(form.email, form.password)
    } else {
      await auth.register(form.email, form.name, form.password)
    }
    if (auth.isAuthenticated) {
      router.push({ name: 'dashboard' })
    }
  } catch (e) {
    error.value = e.message
  } finally {
    submitting.value = false
  }
}
</script>
