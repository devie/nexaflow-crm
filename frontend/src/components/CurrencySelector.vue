<template>
  <select :value="modelValue" @change="$emit('update:modelValue', $event.target.value)" class="border rounded px-2 py-1 text-sm">
    <option v-for="c in currencies" :key="c" :value="c">{{ c }}</option>
  </select>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'

defineProps({ modelValue: { type: String, default: 'USD' } })
defineEmits(['update:modelValue'])

const currencies = ref(['USD', 'EUR', 'GBP', 'IDR', 'JPY', 'AUD', 'SGD', 'MYR', 'CNY', 'CAD'])

onMounted(async () => {
  try {
    const data = await api('/api/currencies/supported')
    if (data?.currencies) currencies.value = data.currencies
  } catch { /* use defaults */ }
})
</script>
