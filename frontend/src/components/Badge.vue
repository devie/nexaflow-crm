<template>
  <span class="px-2 py-0.5 rounded text-xs" :class="colorClass">{{ label }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: String,
  variant: { type: String, default: 'default' },
})

const colorMap = {
  active: 'bg-green-100 text-green-800',
  completed: 'bg-blue-100 text-blue-800',
  on_hold: 'bg-yellow-100 text-yellow-800',
  cancelled: 'bg-gray-100 text-gray-800',
  paid: 'bg-green-100 text-green-800',
  unpaid: 'bg-red-100 text-red-800',
  overdue: 'bg-orange-100 text-orange-800',
  default: 'bg-gray-100 text-gray-800',
}

const colorClass = computed(() => colorMap[props.variant] || colorMap.default)
</script>
