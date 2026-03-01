<template>
  <nav class="bg-white border-b px-6 py-3 flex items-center justify-between">
    <h1 class="text-xl font-bold text-indigo-600">NexaFlow</h1>

    <!-- Navigation tabs -->
    <div class="flex items-center gap-1">
      <router-link
        v-for="tab in tabs"
        :key="tab.to"
        :to="tab.to"
        class="px-3 py-1.5 rounded text-sm font-medium"
        :class="$route.path === tab.to ? 'bg-indigo-100 text-indigo-700' : 'text-gray-600 hover:text-gray-900'"
      >
        {{ tab.label }}
      </router-link>
    </div>

    <!-- Right side: currency + account -->
    <div class="flex items-center gap-3">
      <!-- Currency selector -->
      <div class="flex items-center gap-1">
        <span class="text-xs text-gray-400">Display:</span>
        <select
          :value="auth.user?.preferred_currency || 'USD'"
          @change="changeCurrency($event.target.value)"
          class="border rounded px-2 py-1 text-sm bg-white"
        >
          <option v-for="c in currencies" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>

      <!-- Account dropdown -->
      <div class="relative">
        <button @click="showMenu = !showMenu" class="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900">
          <span class="w-7 h-7 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center text-xs font-bold">
            {{ initials }}
          </span>
          <span class="hidden sm:inline">{{ auth.user?.name || 'Account' }}</span>
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
        </button>
        <div v-if="showMenu" class="absolute right-0 mt-2 w-44 bg-white rounded-lg shadow-lg border py-1 z-50">
          <router-link to="/account" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50" @click="showMenu = false">
            Account Settings
          </router-link>
          <hr class="my-1" />
          <button @click="doLogout" class="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50">
            Logout
          </button>
        </div>
      </div>
    </div>
  </nav>

  <!-- Click-away overlay -->
  <div v-if="showMenu" class="fixed inset-0 z-40" @click="showMenu = false"></div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const showMenu = ref(false)
const currencies = ['USD', 'EUR', 'GBP', 'IDR', 'JPY', 'AUD', 'SGD', 'MYR', 'CNY', 'CAD', 'CHF', 'NZD', 'KRW', 'INR', 'THB']

const tabs = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/contacts', label: 'Contacts' },
  { to: '/projects', label: 'Projects' },
  { to: '/invoices', label: 'Invoices' },
]

const initials = computed(() => {
  const name = auth.user?.name || ''
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) || '?'
})

async function changeCurrency(currency) {
  await auth.updateUser({ preferred_currency: currency })
}

function doLogout() {
  showMenu.value = false
  auth.logout()
  router.push({ name: 'login' })
}
</script>
