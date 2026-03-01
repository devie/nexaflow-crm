<template>
  <div v-if="budget > 0">
    <div class="flex justify-between text-xs text-gray-500 mb-1">
      <span>Budget: {{ currency }} {{ budget.toLocaleString() }}</span>
      <span :class="percentClass">{{ percent }}%</span>
    </div>
    <div class="w-full bg-gray-200 rounded-full h-2">
      <div class="h-2 rounded-full transition-all" :class="barClass" :style="{ width: Math.min(percent, 100) + '%' }"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  budget: { type: Number, default: 0 },
  spent: { type: Number, default: 0 },
  currency: { type: String, default: 'USD' },
})

const percent = computed(() => props.budget > 0 ? Math.round((props.spent / props.budget) * 100) : 0)

const barClass = computed(() => {
  if (percent.value >= 100) return 'bg-red-500'
  if (percent.value >= 80) return 'bg-yellow-500'
  return 'bg-green-500'
})

const percentClass = computed(() => {
  if (percent.value >= 100) return 'text-red-600 font-medium'
  if (percent.value >= 80) return 'text-yellow-600'
  return 'text-green-600'
})
</script>
