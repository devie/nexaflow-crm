import { api } from '../api'

// Simple in-memory cache for exchange rates
const ratesCache = {}

export async function fetchRates(base = 'USD') {
  if (ratesCache[base]) return ratesCache[base]
  try {
    const data = await api(`/api/currencies/rates?base=${base}`)
    if (data?.rates) {
      ratesCache[base] = data.rates
      return data.rates
    }
  } catch {
    // Silently fail — return empty rates
  }
  return {}
}

export function clearRatesCache() {
  Object.keys(ratesCache).forEach(k => delete ratesCache[k])
}

export function convert(amount, fromCurrency, toCurrency, rates) {
  if (!amount || fromCurrency === toCurrency) return amount
  if (!rates) return amount

  // rates is keyed from base currency (e.g. USD-based rates)
  // If converting from USD: just multiply by rate
  if (rates[toCurrency]) {
    return amount * rates[toCurrency]
  }

  return amount
}

export function formatCurrency(amount, currency = 'USD') {
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(amount || 0)
  } catch {
    // Fallback if currency code is invalid
    return `${currency} ${(amount || 0).toLocaleString()}`
  }
}
