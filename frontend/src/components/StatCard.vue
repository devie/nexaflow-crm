<template>
  <div class="bg-white rounded-xl shadow p-5">
    <div class="text-sm text-gray-500 mb-1">{{ title }}</div>
    <div class="text-2xl font-bold">{{ value }}</div>
    <div :class="color" class="h-1 rounded mt-3"></div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  value: [String, Number],
  color: { type: String, default: 'bg-indigo-500' },
})
</script>
