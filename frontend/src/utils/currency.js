import { ref } from 'vue'
import { api } from '../api'

const ratesCache = ref({})
const loading = ref(false)

export async function fetchRates(base = 'USD') {
  if (ratesCache.value[base]) return ratesCache.value[base]
  loading.value = true
  try {
    const data = await api(`/api/currencies/rates?base=${base}`)
    if (data?.rates) {
      ratesCache.value[base] = data.rates
      return data.rates
    }
  } finally {
    loading.value = false
  }
  return {}
}

export function convert(amount, fromCurrency, toCurrency, rates) {
  if (fromCurrency === toCurrency) return amount
  if (!rates || !rates[toCurrency]) return amount
  return amount * rates[toCurrency]
}

export function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount)
}

export { ratesCache, loading }
