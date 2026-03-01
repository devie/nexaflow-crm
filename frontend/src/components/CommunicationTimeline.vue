<template>
  <div class="mt-6 border-t pt-4">
    <div class="flex justify-between items-center mb-3">
      <h4 class="font-bold">Communication History</h4>
      <button @click="showAddLog = true" class="text-xs text-indigo-600 hover:text-indigo-800">+ Add Note</button>
    </div>

    <div v-if="logs.length" class="space-y-3">
      <div v-for="log in logs" :key="log.id" class="flex gap-3">
        <div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold" :class="iconClass(log.type)">
          {{ iconLabel(log.type) }}
        </div>
        <div class="flex-1">
          <p class="text-sm">{{ log.summary }}</p>
          <p class="text-xs text-gray-400 mt-0.5">{{ formatDate(log.created_at) }}</p>
        </div>
      </div>
    </div>
    <p v-else class="text-gray-400 text-sm">No history yet</p>

    <!-- Add Log Modal -->
    <Modal v-if="showAddLog" title="Add Communication Log" @close="showAddLog = false">
      <select v-model="logForm.type" class="w-full border rounded px-3 py-2 mb-2">
        <option value="note">Note</option>
        <option value="call">Call</option>
        <option value="email">Email</option>
        <option value="payment_received">Payment Received</option>
      </select>
      <textarea v-model="logForm.summary" placeholder="Summary..." class="w-full border rounded px-3 py-2 mb-4" rows="3"></textarea>
      <div class="flex gap-2">
        <button @click="addLog" class="flex-1 bg-indigo-600 text-white py-2 rounded hover:bg-indigo-500">Save</button>
        <button @click="showAddLog = false" class="flex-1 bg-gray-200 py-2 rounded hover:bg-gray-300">Cancel</button>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import Modal from './Modal.vue'
import { api } from '../api'

const props = defineProps({
  contactId: { type: Number, default: null },
  projectId: { type: Number, default: null },
})

const logs = ref([])
const showAddLog = ref(false)
const logForm = reactive({ type: 'note', summary: '' })

async function fetchLogs() {
  if (props.contactId) {
    logs.value = (await api(`/api/contacts/${props.contactId}/history`)) || []
  } else if (props.projectId) {
    logs.value = (await api(`/api/projects/${props.projectId}/history`)) || []
  }
}

async function addLog() {
  await api('/api/communication-log', {
    method: 'POST',
    body: JSON.stringify({
      contact_id: props.contactId,
      project_id: props.projectId,
      type: logForm.type,
      summary: logForm.summary,
    }),
  })
  showAddLog.value = false
  logForm.type = 'note'
  logForm.summary = ''
  await fetchLogs()
}

function iconClass(type) {
  const map = {
    invoice_sent: 'bg-blue-100 text-blue-700',
    payment_received: 'bg-green-100 text-green-700',
    note: 'bg-gray-100 text-gray-700',
    call: 'bg-yellow-100 text-yellow-700',
    email: 'bg-purple-100 text-purple-700',
  }
  return map[type] || 'bg-gray-100 text-gray-700'
}

function iconLabel(type) {
  const map = { invoice_sent: 'IN', payment_received: '$', note: 'N', call: 'C', email: 'E' }
  return map[type] || '?'
}

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : ''
}

onMounted(fetchLogs)
watch(() => [props.contactId, props.projectId], fetchLogs)
</script>
