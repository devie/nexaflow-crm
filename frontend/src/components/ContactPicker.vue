<template>
  <div class="relative">
    <input
      v-model="search"
      :placeholder="placeholder"
      class="w-full border rounded px-3 py-2"
      @focus="open = true"
    />
    <ul v-if="open && filtered.length" class="absolute z-10 w-full bg-white border rounded mt-1 max-h-40 overflow-y-auto shadow-lg">
      <li
        v-for="c in filtered"
        :key="c.id"
        class="px-3 py-2 hover:bg-indigo-50 cursor-pointer text-sm"
        @click="select(c)"
      >
        <span class="font-medium">{{ c.name }}</span>
        <span v-if="c.email" class="text-gray-400 ml-2">{{ c.email }}</span>
      </li>
    </ul>
    <div v-if="open && !filtered.length && search" class="absolute z-10 w-full bg-white border rounded mt-1 p-2 text-sm text-gray-400">
      No contacts found
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'

const props = defineProps({
  placeholder: { type: String, default: 'Search contacts...' },
  exclude: { type: Array, default: () => [] },
})
const emit = defineEmits(['select'])

const search = ref('')
const open = ref(false)
const contacts = ref([])

onMounted(async () => {
  contacts.value = (await api('/api/contacts')) || []
})

const filtered = computed(() => {
  const q = search.value.toLowerCase()
  return contacts.value
    .filter(c => !props.exclude.includes(c.id))
    .filter(c => !q || c.name.toLowerCase().includes(q) || (c.email && c.email.toLowerCase().includes(q)))
    .slice(0, 10)
})

function select(c) {
  emit('select', c)
  search.value = ''
  open.value = false
}
</script>
