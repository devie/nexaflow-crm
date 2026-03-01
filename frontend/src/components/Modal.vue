<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="$emit('close')">
    <div class="bg-white rounded-xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
      <h3 class="text-lg font-bold mb-4">{{ title }}</h3>
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({ title: String })
defineEmits(['close'])
</script>
