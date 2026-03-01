<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Dashboard</h2>

    <div v-if="dashboard.stats" class="space-y-6">
      <!-- Stat Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard title="Total Contacts" :value="dashboard.stats.total_contacts" color="bg-blue-500" />
        <StatCard title="Active Projects" :value="dashboard.stats.active_projects" color="bg-green-500" />
        <StatCard title="Completed" :value="dashboard.stats.completed_projects" color="bg-purple-500" />
        <StatCard title="Project Value" :value="fmt(dashboard.stats.total_project_value)" color="bg-indigo-500" />
      </div>

      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard title="Unpaid Invoices" :value="fmt(dashboard.stats.unpaid_total)" color="bg-red-500" />
        <StatCard title="Paid Invoices" :value="fmt(dashboard.stats.paid_total)" color="bg-emerald-500" />
        <StatCard title="Overdue" :value="dashboard.stats.overdue_invoices" :color="dashboard.stats.overdue_invoices > 0 ? 'bg-red-500' : 'bg-gray-300'" />
        <StatCard title="Over Budget" :value="dashboard.stats.projects_over_budget" :color="dashboard.stats.projects_over_budget > 0 ? 'bg-orange-500' : 'bg-gray-300'" />
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Revenue Chart -->
        <div class="bg-white rounded-xl shadow p-5">
          <h3 class="font-bold mb-4">Monthly Revenue (6 months)</h3>
          <div v-if="dashboard.stats.monthly_revenue.length" class="flex items-end gap-2 h-40">
            <div
              v-for="m in dashboard.stats.monthly_revenue"
              :key="m.month"
              class="flex-1 flex flex-col items-center justify-end"
            >
              <span class="text-xs font-medium mb-1">{{ fmt(m.revenue) }}</span>
              <div
                class="w-full bg-indigo-500 rounded-t transition-all"
                :style="{ height: barHeight(m.revenue) + '%' }"
              ></div>
              <span class="text-xs text-gray-400 mt-1">{{ m.month.slice(5) }}</span>
            </div>
          </div>
          <p v-else class="text-gray-400 text-sm">No revenue data</p>
        </div>

        <!-- Upcoming Milestones -->
        <div class="bg-white rounded-xl shadow p-5">
          <h3 class="font-bold mb-4">Upcoming Milestones</h3>
          <div v-if="dashboard.stats.upcoming_milestones.length" class="space-y-3">
            <div v-for="ms in dashboard.stats.upcoming_milestones" :key="ms.id" class="flex items-center gap-3">
              <div class="w-2 h-2 rounded-full" :class="isOverdue(ms.due_date) ? 'bg-red-500' : 'bg-green-500'"></div>
              <div class="flex-1">
                <p class="text-sm font-medium">{{ ms.title }}</p>
                <p class="text-xs text-gray-400">Due: {{ ms.due_date }}</p>
              </div>
            </div>
          </div>
          <p v-else class="text-gray-400 text-sm">No upcoming milestones</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, watch } from 'vue'
import StatCard from '../components/StatCard.vue'
import { useDashboardStore } from '../stores/dashboard'
import { useAuthStore } from '../stores/auth'
import { formatCurrency } from '../utils/currency'

const dashboard = useDashboardStore()
const auth = useAuthStore()

const currency = computed(() => auth.user?.preferred_currency || 'USD')

onMounted(() => dashboard.fetchStats())

// Re-fetch when currency changes — backend now converts per-item
watch(currency, () => dashboard.fetchStats())

function fmt(amount) {
  return formatCurrency(amount, currency.value)
}

function barHeight(revenue) {
  if (!dashboard.stats?.monthly_revenue.length) return 0
  const max = Math.max(...dashboard.stats.monthly_revenue.map(m => m.revenue), 1)
  return Math.max((revenue / max) * 100, 2)
}

function isOverdue(dueDate) {
  if (!dueDate) return false
  return new Date(dueDate) < new Date()
}
</script>
