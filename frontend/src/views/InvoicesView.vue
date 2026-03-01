<template>
  <div>
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold">Invoices</h2>
      <button @click="openWizard" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-500">
        + New Invoice
      </button>
    </div>

    <!-- Status filter tabs -->
    <div class="flex gap-2 mb-4 text-sm">
      <button v-for="s in ['all', 'unpaid', 'paid', 'overdue', 'cancelled']" :key="s"
        @click="filterStatus = s; loadInvoices()"
        class="px-3 py-1 rounded-full border transition-colors"
        :class="filterStatus === s ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-gray-600 hover:bg-gray-50'">
        {{ s === 'all' ? 'All' : s }}
      </button>
    </div>

    <div class="bg-white rounded-xl shadow overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="text-left p-3">#</th>
            <th class="text-left p-3">Title</th>
            <th class="text-left p-3">Project</th>
            <th class="text-left p-3">Amount</th>
            <th class="text-left p-3">Status</th>
            <th class="text-left p-3">Due</th>
            <th class="text-left p-3">Sent</th>
            <th class="p-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="inv in store.invoices" :key="inv.id" class="border-t hover:bg-gray-50">
            <td class="p-3 font-mono text-xs">{{ inv.invoice_number || `INV-${inv.id}` }}</td>
            <td class="p-3">{{ inv.title || '-' }}</td>
            <td class="p-3">{{ projectName(inv.project_id) }}</td>
            <td class="p-3 font-medium">{{ inv.currency || 'USD' }} {{ Number(inv.amount).toLocaleString() }}</td>
            <td class="p-3"><Badge :label="inv.status" :variant="inv.status" /></td>
            <td class="p-3">{{ inv.due_date || '-' }}</td>
            <td class="p-3">
              <span v-if="inv.sent_at" class="text-green-600 text-xs">Sent</span>
              <span v-if="inv.opened_at" class="text-blue-600 text-xs ml-1">Opened</span>
              <span v-if="!inv.sent_at" class="text-gray-400 text-xs">Not sent</span>
            </td>
            <td class="p-3 text-center space-x-1">
              <button @click="openDetail(inv)" class="text-indigo-500 text-xs hover:text-indigo-700">Details</button>
              <button v-if="inv.status === 'unpaid'" @click="markPaid(inv.id)" class="text-green-600 text-xs hover:text-green-800">
                Paid
              </button>
              <button @click="handleDelete(inv.id)" class="text-red-500 text-xs hover:text-red-700">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="store.invoices.length === 0" class="p-6 text-center text-gray-400">No invoices yet</p>
    </div>

    <!-- Invoice Wizard (3 steps) -->
    <Modal v-if="showWizard" :title="wizardStepTitle" @close="showWizard = false">
      <!-- Step 1: Select Project -->
      <div v-if="wizardStep === 1">
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Project <span class="text-red-500">*</span></label>
            <select v-model="wizard.project_id" class="w-full border rounded-lg px-3 py-2">
              <option :value="null" disabled>Select project...</option>
              <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.title }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Invoice Title</label>
            <input v-model="wizard.title" placeholder="e.g. Website Development - Phase 1" class="w-full border rounded-lg px-3 py-2" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
              <input v-model="wizard.due_date" type="date" class="w-full border rounded-lg px-3 py-2" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Currency</label>
              <select v-model="wizard.currency" class="w-full border rounded-lg px-3 py-2">
                <option v-for="c in currencies" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea v-model="wizard.notes" placeholder="Payment terms, bank details, etc." class="w-full border rounded-lg px-3 py-2" rows="2"></textarea>
          </div>
        </div>
        <button @click="wizardStep = 2" :disabled="!wizard.project_id" class="w-full mt-4 bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-500 disabled:opacity-50">
          Next: Line Items
        </button>
      </div>

      <!-- Step 2: Line Items -->
      <div v-if="wizardStep === 2">
        <div v-for="(item, i) in wizard.lineItems" :key="i" class="flex gap-2 mb-2 items-center">
          <input v-model="item.description" placeholder="Description" class="flex-1 border rounded px-2 py-1.5 text-sm" />
          <input v-model.number="item.quantity" type="number" min="1" class="w-16 border rounded px-2 py-1.5 text-sm text-center" />
          <input v-model.number="item.unit_price" type="number" step="0.01" placeholder="Price" class="w-24 border rounded px-2 py-1.5 text-sm text-right" />
          <span class="w-24 text-right text-sm py-1 font-medium text-gray-700">{{ wizard.currency }} {{ (item.quantity * item.unit_price).toFixed(2) }}</span>
          <button @click="wizard.lineItems.splice(i, 1)" class="text-red-400 hover:text-red-600 text-lg leading-none">&times;</button>
        </div>
        <button @click="wizard.lineItems.push({ description: '', quantity: 1, unit_price: 0 })" class="text-indigo-600 text-sm hover:text-indigo-800 mb-4">
          + Add Line Item
        </button>
        <div class="text-right font-bold text-lg mb-4 border-t pt-3">
          Total: {{ wizard.currency }} {{ wizardTotal.toFixed(2) }}
        </div>
        <div class="flex gap-2">
          <button @click="wizardStep = 1" class="flex-1 bg-gray-200 py-2 rounded-lg hover:bg-gray-300">Back</button>
          <button @click="wizardStep = 3" class="flex-1 bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-500">
            Next: Review
          </button>
        </div>
      </div>

      <!-- Step 3: Review & Send -->
      <div v-if="wizardStep === 3">
        <div class="bg-gray-50 rounded-lg p-4 mb-4 text-sm space-y-1">
          <p><span class="text-gray-500">Project:</span> <strong>{{ projects.find(p => p.id === wizard.project_id)?.title }}</strong></p>
          <p><span class="text-gray-500">Title:</span> <strong>{{ wizard.title || 'Untitled' }}</strong></p>
          <p><span class="text-gray-500">Due:</span> <strong>{{ wizard.due_date || 'None' }}</strong></p>
          <p><span class="text-gray-500">Items:</span> <strong>{{ wizard.lineItems.filter(i => i.description).length }}</strong></p>
          <p class="text-xl font-bold mt-3 pt-2 border-t">{{ wizard.currency }} {{ wizardTotal.toFixed(2) }}</p>
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Recipient Email (for sending)</label>
          <input v-model="wizard.sendToEmail" placeholder="client@example.com" class="w-full border rounded-lg px-3 py-2" />
        </div>

        <div class="flex gap-2">
          <button @click="wizardStep = 2" class="flex-1 bg-gray-200 py-2 rounded-lg hover:bg-gray-300">Back</button>
          <button @click="submitWizard" :disabled="submitting" class="flex-1 bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-500 disabled:opacity-50">
            Create Invoice
          </button>
        </div>
      </div>
    </Modal>

    <!-- Invoice Detail Slide-over -->
    <div v-if="detailInvoice" class="fixed inset-0 bg-black/50 flex justify-end z-50" @click.self="detailInvoice = null">
      <div class="bg-white w-full max-w-2xl h-full overflow-y-auto">
        <!-- Header -->
        <div class="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-start z-10">
          <div>
            <h3 class="text-xl font-bold">{{ detailInvoice.invoice_number || `INV-${detailInvoice.id}` }}</h3>
            <div class="flex items-center gap-2 mt-1">
              <Badge :label="detailInvoice.status" :variant="detailInvoice.status" />
              <span class="text-sm text-gray-500">{{ projectName(detailInvoice.project_id) }}</span>
            </div>
          </div>
          <button @click="detailInvoice = null" class="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
        </div>

        <div class="p-6 space-y-6">
          <!-- Invoice Info -->
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-indigo-50 rounded-lg p-4">
              <div class="text-xs text-gray-500">Amount</div>
              <div class="text-2xl font-bold text-indigo-600">{{ detailInvoice.currency || 'USD' }} {{ Number(detailInvoice.amount).toLocaleString() }}</div>
            </div>
            <div class="bg-gray-50 rounded-lg p-4">
              <div class="text-xs text-gray-500">Due Date</div>
              <div class="text-lg font-medium">{{ detailInvoice.due_date || 'Not set' }}</div>
            </div>
          </div>

          <div v-if="detailInvoice.title" class="text-gray-700 font-medium">{{ detailInvoice.title }}</div>
          <div v-if="detailInvoice.notes" class="text-sm text-gray-500 bg-gray-50 rounded-lg p-3">{{ detailInvoice.notes }}</div>

          <!-- Send/Open Status -->
          <div v-if="detailInvoice.sent_at || detailInvoice.opened_at" class="flex gap-3 text-sm">
            <div v-if="detailInvoice.sent_at" class="bg-green-50 text-green-700 px-3 py-2 rounded-lg flex-1">
              Sent to <strong>{{ detailInvoice.sent_to_email }}</strong> on {{ new Date(detailInvoice.sent_at).toLocaleDateString() }}
            </div>
            <div v-if="detailInvoice.opened_at" class="bg-blue-50 text-blue-700 px-3 py-2 rounded-lg">
              Opened {{ new Date(detailInvoice.opened_at).toLocaleDateString() }}
            </div>
          </div>

          <!-- Line Items -->
          <div>
            <h4 class="font-bold mb-3">Line Items</h4>
            <div class="bg-white border rounded-lg overflow-hidden">
              <table class="w-full text-sm">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="text-left px-4 py-2 text-gray-500 font-medium">Description</th>
                    <th class="text-center px-4 py-2 text-gray-500 font-medium w-16">Qty</th>
                    <th class="text-right px-4 py-2 text-gray-500 font-medium w-24">Price</th>
                    <th class="text-right px-4 py-2 text-gray-500 font-medium w-24">Total</th>
                    <th class="w-8"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in lineItems" :key="item.id" class="border-t">
                    <td class="px-4 py-2">{{ item.description }}</td>
                    <td class="px-4 py-2 text-center">{{ item.quantity }}</td>
                    <td class="px-4 py-2 text-right">{{ item.unit_price.toFixed(2) }}</td>
                    <td class="px-4 py-2 text-right font-medium">{{ item.total.toFixed(2) }}</td>
                    <td class="px-2 py-2">
                      <button @click="removeLineItem(item.id)" class="text-red-400 hover:text-red-600 text-xs">&times;</button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <p v-if="lineItems.length === 0" class="p-4 text-center text-gray-400 text-sm">No line items</p>
            </div>
          </div>

          <!-- Actions: Send / PDF / Email+PDF -->
          <div class="border-t pt-4">
            <h4 class="font-bold mb-3">Actions</h4>

            <!-- Preview -->
            <div class="mb-4">
              <a :href="`/api/invoices/${detailInvoice.id}/preview`" target="_blank"
                class="text-indigo-600 text-sm hover:text-indigo-800 underline">
                Preview Invoice HTML
              </a>
            </div>

            <!-- PDF Download -->
            <div class="mb-4">
              <button @click="downloadPdf" class="w-full flex items-center justify-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 py-2.5 rounded-lg text-sm font-medium transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                Download PDF
              </button>
            </div>

            <!-- Email Section -->
            <div class="space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Recipient Email</label>
                <input v-model="sendEmail" placeholder="client@example.com" class="w-full border rounded-lg px-3 py-2 text-sm" />
              </div>

              <div class="grid grid-cols-2 gap-2">
                <button @click="sendInvoiceEmail('email_only')" :disabled="!sendEmail || sending"
                  class="flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white py-2.5 rounded-lg text-sm font-medium disabled:opacity-50 transition-colors">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
                  Email Only
                </button>
                <button @click="sendInvoiceEmail('email_and_pdf')" :disabled="!sendEmail || sending"
                  class="flex items-center justify-center gap-2 bg-green-600 hover:bg-green-500 text-white py-2.5 rounded-lg text-sm font-medium disabled:opacity-50 transition-colors">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"/></svg>
                  Email + PDF
                </button>
              </div>

              <p v-if="sendStatus" class="text-sm text-center" :class="sendStatus.ok ? 'text-green-600' : 'text-red-600'">
                {{ sendStatus.message }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import Modal from '../components/Modal.vue'
import Badge from '../components/Badge.vue'
import { useInvoicesStore } from '../stores/invoices'
import { api, getToken } from '../api'

const store = useInvoicesStore()
const showWizard = ref(false)
const wizardStep = ref(1)
const submitting = ref(false)
const projects = ref([])
const detailInvoice = ref(null)
const lineItems = ref([])
const sendEmail = ref('')
const sending = ref(false)
const sendStatus = ref(null)
const filterStatus = ref('all')
const currencies = ['USD', 'EUR', 'GBP', 'IDR', 'JPY', 'AUD', 'SGD', 'MYR', 'CNY', 'CAD']

const wizard = reactive({
  project_id: null,
  title: '',
  due_date: '',
  currency: 'USD',
  notes: '',
  lineItems: [{ description: '', quantity: 1, unit_price: 0 }],
  sendToEmail: '',
})

const wizardTotal = computed(() =>
  wizard.lineItems.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0)
)

const wizardStepTitle = computed(() => {
  const titles = { 1: 'New Invoice - Project', 2: 'New Invoice - Line Items', 3: 'New Invoice - Review' }
  return titles[wizardStep.value]
})

onMounted(async () => {
  loadInvoices()
  projects.value = (await api('/api/projects')) || []
})

function loadInvoices() {
  store.fetchInvoices(filterStatus.value === 'all' ? '' : filterStatus.value)
}

function projectName(projectId) {
  const p = projects.value.find(pr => pr.id === projectId)
  return p ? p.title : `Project #${projectId}`
}

function openWizard() {
  wizardStep.value = 1
  Object.assign(wizard, {
    project_id: null, title: '', due_date: '', currency: 'USD', notes: '',
    lineItems: [{ description: '', quantity: 1, unit_price: 0 }],
    sendToEmail: '',
  })
  showWizard.value = true
}

async function submitWizard() {
  submitting.value = true
  try {
    const amount = wizardTotal.value || 0.01
    const inv = await store.createInvoice({
      project_id: wizard.project_id,
      amount,
      due_date: wizard.due_date,
      currency: wizard.currency,
      title: wizard.title,
      notes: wizard.notes,
    })

    if (inv?.id) {
      for (const item of wizard.lineItems) {
        if (item.description) {
          await api(`/api/invoices/${inv.id}/line-items`, {
            method: 'POST',
            body: JSON.stringify(item),
          })
        }
      }

      if (wizard.sendToEmail) {
        try {
          await api(`/api/invoices/${inv.id}/send?to_email=${encodeURIComponent(wizard.sendToEmail)}&mode=email_only`, { method: 'POST' })
        } catch { /* SMTP might not be configured */ }
      }
    }

    showWizard.value = false
    loadInvoices()
  } finally {
    submitting.value = false
  }
}

async function markPaid(id) {
  await store.updateInvoice(id, { status: 'paid' })
  loadInvoices()
}

async function handleDelete(id) {
  if (confirm('Delete invoice?')) {
    await store.deleteInvoice(id)
    loadInvoices()
    if (detailInvoice.value?.id === id) detailInvoice.value = null
  }
}

async function openDetail(inv) {
  detailInvoice.value = inv
  sendEmail.value = inv.sent_to_email || ''
  sendStatus.value = null
  lineItems.value = (await api(`/api/invoices/${inv.id}/line-items`)) || []
}

async function removeLineItem(itemId) {
  await api(`/api/invoices/${detailInvoice.value.id}/line-items/${itemId}`, { method: 'DELETE' })
  lineItems.value = (await api(`/api/invoices/${detailInvoice.value.id}/line-items`)) || []
}

function downloadPdf() {
  const token = getToken()
  const url = `/api/invoices/${detailInvoice.value.id}/pdf`
  // Open in new tab with auth — use fetch + blob
  fetch(url, { headers: { 'Authorization': `Bearer ${token}` } })
    .then(r => r.blob())
    .then(blob => {
      const blobUrl = URL.createObjectURL(blob)
      window.open(blobUrl, '_blank')
    })
    .catch(() => alert('Failed to generate PDF'))
}

async function sendInvoiceEmail(mode) {
  sending.value = true
  sendStatus.value = null
  try {
    const result = await api(
      `/api/invoices/${detailInvoice.value.id}/send?to_email=${encodeURIComponent(sendEmail.value)}&mode=${mode}`,
      { method: 'POST' }
    )
    sendStatus.value = { ok: true, message: result.message || 'Invoice sent successfully' }
    loadInvoices()
  } catch (e) {
    sendStatus.value = { ok: false, message: e.message || 'Failed to send' }
  } finally {
    sending.value = false
  }
}
</script>
