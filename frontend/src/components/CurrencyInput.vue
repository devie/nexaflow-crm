<template>
  <div class="relative">
    <input
      ref="inputEl"
      type="text"
      inputmode="decimal"
      :value="displayValue"
      @focus="onFocus"
      @blur="onBlur"
      @input="onInput"
      :placeholder="placeholder"
      :class="inputClass"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Number, default: 0 },
  placeholder: { type: String, default: '0' },
  inputClass: { type: String, default: 'w-full border rounded-lg px-3 py-2' },
})

const emit = defineEmits(['update:modelValue'])
const inputEl = ref(null)
const focused = ref(false)

function formatNumber(n) {
  if (n == null || isNaN(n)) return ''
  return Number(n).toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  })
}

function parseNumber(str) {
  if (!str) return 0
  // Remove thousand separators, keep decimal point
  const cleaned = str.replace(/,/g, '').replace(/[^0-9.\-]/g, '')
  const num = parseFloat(cleaned)
  return isNaN(num) ? 0 : num
}

const displayValue = computed(() => {
  if (focused.value) {
    // When focused, show raw number for easy editing
    return props.modelValue ? String(props.modelValue) : ''
  }
  // When blurred, show formatted
  return props.modelValue ? formatNumber(props.modelValue) : ''
})

function onFocus() {
  focused.value = true
}

function onBlur() {
  focused.value = false
}

function onInput(e) {
  const val = parseNumber(e.target.value)
  emit('update:modelValue', val)
}
</script>
