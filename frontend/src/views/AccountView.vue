<template>
  <div class="max-w-lg">
    <h2 class="text-2xl font-bold mb-6">Account Settings</h2>

    <div v-if="saved" class="bg-green-100 text-green-700 p-3 rounded-lg mb-4 text-sm">
      Settings saved successfully.
    </div>
    <div v-if="error" class="bg-red-100 text-red-700 p-3 rounded-lg mb-4 text-sm">
      {{ error }}
    </div>

    <div class="bg-white rounded-xl shadow p-6 space-y-5">
      <!-- Profile -->
      <div>
        <h3 class="font-bold text-gray-700 mb-3">Profile</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1">Name</label>
            <input v-model="form.name" type="text" class="w-full border rounded-lg px-4 py-2" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1">Email</label>
            <input v-model="form.email" type="email" class="w-full border rounded-lg px-4 py-2" />
          </div>
        </div>
      </div>

      <!-- Preferences -->
      <div class="border-t pt-5">
        <h3 class="font-bold text-gray-700 mb-3">Preferences</h3>
        <div>
          <label class="block text-sm font-medium text-gray-600 mb-1">Default Currency</label>
          <select v-model="form.preferred_currency" class="w-full border rounded-lg px-4 py-2">
            <option v-for="c in currencies" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
      </div>

      <!-- Change Password -->
      <div class="border-t pt-5">
        <h3 class="font-bold text-gray-700 mb-3">Change Password</h3>
        <div>
          <label class="block text-sm font-medium text-gray-600 mb-1">New Password</label>
          <input v-model="form.password" type="password" placeholder="Leave blank to keep current" class="w-full border rounded-lg px-4 py-2" />
          <p class="text-xs text-gray-400 mt-1">Minimum 6 characters</p>
        </div>
      </div>

      <!-- Save -->
      <div class="border-t pt-5">
        <button @click="saveProfile" :disabled="saving" class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-500 font-medium disabled:opacity-50">
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const saving = ref(false)
const saved = ref(false)
const error = ref('')
const currencies = ['USD', 'EUR', 'GBP', 'IDR', 'JPY', 'AUD', 'SGD', 'MYR', 'CNY', 'CAD', 'CHF', 'NZD', 'SEK', 'NOK', 'KRW', 'INR', 'BRL', 'THB', 'PHP', 'PLN']

const form = reactive({
  name: '',
  email: '',
  preferred_currency: 'USD',
  password: '',
})

function loadFromUser() {
  if (auth.user) {
    form.name = auth.user.name || ''
    form.email = auth.user.email || ''
    form.preferred_currency = auth.user.preferred_currency || 'USD'
    form.password = ''
  }
}

onMounted(async () => {
  if (!auth.user) await auth.fetchUser()
  loadFromUser()
})

watch(() => auth.user, loadFromUser)

async function saveProfile() {
  saved.value = false
  error.value = ''
  saving.value = true
  try {
    const payload = {
      name: form.name,
      email: form.email,
      preferred_currency: form.preferred_currency,
    }
    if (form.password) payload.password = form.password
    await auth.updateUser(payload)
    form.password = ''
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}
</script>
