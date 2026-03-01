<template>
  <div>
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold">Projects</h2>
      <button @click="openAddForm" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-500">
        + Add Project
      </button>
    </div>

    <!-- Status filter tabs -->
    <div class="flex gap-2 mb-4 text-sm">
      <button v-for="s in ['all', 'active', 'on_hold', 'completed', 'cancelled']" :key="s"
        @click="filterStatus = s; loadProjects()"
        class="px-3 py-1 rounded-full border transition-colors"
        :class="filterStatus === s ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-gray-600 hover:bg-gray-50'">
        {{ s === 'all' ? 'All' : s.replace('_', ' ') }}
      </button>
    </div>

    <!-- Project Cards Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="p in store.projects" :key="p.id"
        class="bg-white rounded-xl shadow hover:shadow-md transition-shadow cursor-pointer overflow-hidden"
        @click="openDetail(p)">
        <!-- Card Header -->
        <div class="p-5 pb-3">
          <div class="flex justify-between items-start mb-2">
            <h3 class="font-bold text-gray-900 leading-tight">{{ p.title }}</h3>
            <Badge :label="p.status" :variant="p.status" />
          </div>
          <p class="text-sm text-gray-500 line-clamp-2">{{ p.description || 'No description' }}</p>
        </div>

        <!-- Level 1: Executive Summary -->
        <div class="px-5 pb-3">
          <div class="flex justify-between items-baseline mb-2">
            <span class="text-xl font-bold text-indigo-600">{{ p.currency }} {{ fmtNum(p.value) }}</span>
            <span class="text-xs text-gray-400">project value</span>
          </div>
          <BudgetBar :budget="p.budget" :spent="p.actual_cost || 0" :currency="p.currency" />
        </div>

        <!-- Card Footer -->
        <div class="px-5 py-3 bg-gray-50 flex justify-between items-center text-xs text-gray-500">
          <div class="flex gap-3">
            <span v-if="p.start_date">{{ p.start_date }}</span>
            <span v-if="p.start_date && p.end_date">→</span>
            <span v-if="p.end_date">{{ p.end_date }}</span>
            <span v-if="!p.start_date && !p.end_date">No dates</span>
          </div>
          <button @click.stop="handleDelete(p.id)" class="text-red-400 hover:text-red-600">Delete</button>
        </div>
      </div>
    </div>
    <p v-if="store.projects.length === 0" class="text-center text-gray-400 mt-8">No projects yet</p>

    <!-- Add/Edit Modal -->
    <Modal v-if="showForm" :title="editing ? 'Edit Project' : 'New Project'" @close="closeForm">
      <div class="space-y-4">
        <!-- Basic Info -->
        <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider">Basic Information</div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Project Title <span class="text-red-500">*</span></label>
          <input v-model="form.title" type="text" placeholder="e.g. Website Redesign" class="w-full border rounded-lg px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea v-model="form.description" placeholder="Brief project description..." class="w-full border rounded-lg px-3 py-2" rows="2"></textarea>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select v-model="form.status" class="w-full border rounded-lg px-3 py-2">
              <option value="active">Active</option>
              <option value="on_hold">On Hold</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Currency</label>
            <select v-model="form.currency" class="w-full border rounded-lg px-3 py-2">
              <option v-for="c in currencies" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
        </div>

        <!-- Financials -->
        <div class="border-t pt-4">
          <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Financials</div>
          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Project Value</label>
              <input v-model.number="form.value" type="number" min="0" step="0.01" placeholder="0.00" class="w-full border rounded-lg px-3 py-2" />
              <p class="text-xs text-gray-400 mt-0.5">Revenue</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Budget</label>
              <input v-model.number="form.budget" type="number" min="0" step="0.01" placeholder="0.00" class="w-full border rounded-lg px-3 py-2" />
              <p class="text-xs text-gray-400 mt-0.5">Max spend</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Actual Cost</label>
              <input v-model.number="form.actual_cost" type="number" min="0" step="0.01" placeholder="0.00" class="w-full border rounded-lg px-3 py-2" />
              <p class="text-xs text-gray-400 mt-0.5">Spent so far</p>
            </div>
          </div>
        </div>

        <!-- Schedule -->
        <div class="border-t pt-4">
          <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Schedule</div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <input v-model="form.start_date" type="date" class="w-full border rounded-lg px-3 py-2" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
              <input v-model="form.end_date" type="date" class="w-full border rounded-lg px-3 py-2" />
            </div>
          </div>
        </div>

        <div class="flex gap-2 pt-2">
          <button @click="save" class="flex-1 bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-500 font-medium">Save</button>
          <button @click="closeForm" class="flex-1 bg-gray-200 py-2 rounded-lg hover:bg-gray-300">Cancel</button>
        </div>
      </div>
    </Modal>

    <!-- Project Detail Slide-over -->
    <div v-if="detailProject" class="fixed inset-0 bg-black/50 flex justify-end z-50" @click.self="detailProject = null">
      <div class="bg-white w-full max-w-2xl h-full overflow-y-auto">
        <!-- Header -->
        <div class="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-start z-10">
          <div>
            <h3 class="text-xl font-bold">{{ detailProject.title }}</h3>
            <div class="flex items-center gap-2 mt-1">
              <Badge :label="detailProject.status" :variant="detailProject.status" />
              <span v-if="summary" class="text-xs text-gray-400">{{ summary.currency }}</span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button @click="startEdit(detailProject)" class="text-sm text-indigo-600 hover:text-indigo-800 border border-indigo-200 px-3 py-1 rounded-lg">Edit</button>
            <button @click="detailProject = null" class="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
          </div>
        </div>

        <div class="p-6 space-y-6">
          <!-- Description -->
          <p v-if="detailProject.description" class="text-gray-600">{{ detailProject.description }}</p>

          <!-- Loading -->
          <div v-if="summaryLoading" class="text-center py-8 text-gray-400">Loading summary...</div>

          <template v-if="summary">
            <!-- Level 1: Executive Summary -->
            <div>
              <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Executive Summary</div>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div class="bg-indigo-50 rounded-lg p-3">
                  <div class="text-xs text-gray-500">Project Value</div>
                  <div class="text-lg font-bold text-indigo-600">{{ summary.currency }} {{ fmtNum(summary.project_value) }}</div>
                </div>
                <div class="bg-gray-50 rounded-lg p-3">
                  <div class="text-xs text-gray-500">Budget</div>
                  <div class="text-lg font-bold">{{ summary.currency }} {{ fmtNum(summary.budget) }}</div>
                </div>
                <div class="bg-gray-50 rounded-lg p-3">
                  <div class="text-xs text-gray-500">Actual Cost</div>
                  <div class="text-lg font-bold">{{ summary.currency }} {{ fmtNum(summary.actual_cost) }}</div>
                </div>
                <div class="rounded-lg p-3" :class="summary.net_margin >= 0 ? 'bg-green-50' : 'bg-red-50'">
                  <div class="text-xs text-gray-500">Net Margin</div>
                  <div class="text-lg font-bold" :class="summary.net_margin >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ summary.margin_pct }}%
                  </div>
                  <div class="text-xs" :class="summary.net_margin >= 0 ? 'text-green-500' : 'text-red-500'">
                    {{ summary.currency }} {{ fmtNum(summary.net_margin) }}
                  </div>
                </div>
              </div>

              <!-- Progress bar -->
              <div v-if="summary.milestones_total > 0" class="mt-3">
                <div class="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Progress</span>
                  <span>{{ summary.milestones_completed }}/{{ summary.milestones_total }} milestones ({{ summary.progress_pct }}%)</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div class="h-2 rounded-full bg-indigo-500 transition-all" :style="{ width: summary.progress_pct + '%' }"></div>
                </div>
              </div>
            </div>

            <!-- Level 2: Financial Snapshot -->
            <div>
              <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Financial Snapshot</div>
              <div class="bg-white border rounded-lg divide-y">
                <div class="flex justify-between px-4 py-2.5 text-sm">
                  <span class="text-gray-500">Budget Variance</span>
                  <span class="font-medium" :class="summary.variance >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ summary.variance >= 0 ? '+' : '' }}{{ summary.currency }} {{ fmtNum(summary.variance) }}
                  </span>
                </div>
                <div class="flex justify-between px-4 py-2.5 text-sm">
                  <span class="text-gray-500">Invoiced</span>
                  <span class="font-medium">{{ summary.currency }} {{ fmtNum(summary.invoiced_amount) }}</span>
                </div>
                <div class="flex justify-between px-4 py-2.5 text-sm">
                  <span class="text-gray-500">Received Payment</span>
                  <span class="font-medium text-green-600">{{ summary.currency }} {{ fmtNum(summary.received_payment) }}</span>
                </div>
                <div class="flex justify-between px-4 py-2.5 text-sm">
                  <span class="text-gray-500">Outstanding</span>
                  <span class="font-medium" :class="summary.outstanding_invoice > 0 ? 'text-orange-600' : ''">
                    {{ summary.currency }} {{ fmtNum(summary.outstanding_invoice) }}
                  </span>
                </div>
                <div class="flex justify-between px-4 py-2.5 text-sm">
                  <span class="text-gray-500">Cash Flow Position</span>
                  <span class="font-bold" :class="summary.cashflow_position >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ summary.currency }} {{ fmtNum(summary.cashflow_position) }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Level 3: Operational -->
            <div>
              <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Operational</div>
              <div class="grid grid-cols-2 gap-3 text-sm">
                <div class="bg-gray-50 rounded-lg p-3">
                  <div class="text-xs text-gray-500">Schedule</div>
                  <div class="font-medium">
                    <span v-if="summary.start_date">{{ summary.start_date }}</span>
                    <span v-if="summary.start_date && summary.end_date"> → {{ summary.end_date }}</span>
                    <span v-if="!summary.start_date" class="text-gray-400">Not set</span>
                  </div>
                </div>
                <div class="bg-gray-50 rounded-lg p-3">
                  <div class="text-xs text-gray-500">Project Manager</div>
                  <div class="font-medium">{{ summary.pm_name || 'Not assigned' }}</div>
                </div>
                <div class="bg-gray-50 rounded-lg p-3">
                  <div class="text-xs text-gray-500">Team</div>
                  <div class="font-medium">{{ summary.team_count }} member{{ summary.team_count !== 1 ? 's' : '' }}</div>
                </div>
                <div class="bg-gray-50 rounded-lg p-3" :class="summary.overdue_milestones > 0 ? 'bg-red-50' : ''">
                  <div class="text-xs text-gray-500">Overdue Milestones</div>
                  <div class="font-medium" :class="summary.overdue_milestones > 0 ? 'text-red-600' : ''">{{ summary.overdue_milestones }}</div>
                </div>
              </div>
            </div>
          </template>

          <!-- Budget Bar -->
          <div>
            <BudgetBar :budget="detailProject.budget" :spent="detailProject.actual_cost || 0" :currency="detailProject.currency" />
          </div>

          <!-- Project Contacts -->
          <div class="border-t pt-4">
            <h4 class="font-bold mb-3">Team Members</h4>
            <div v-for="pc in projectContacts" :key="pc.id" class="flex items-center justify-between py-2 border-b">
              <div>
                <span class="font-medium text-sm">{{ pc.contact_name }}</span>
                <span class="text-gray-400 text-xs ml-2">{{ pc.contact_email }}</span>
              </div>
              <div class="flex items-center gap-2">
                <select :value="pc.role" @change="updateRole(pc.contact_id, $event.target.value)" class="text-xs border rounded px-1 py-0.5">
                  <option value="pm">PM</option>
                  <option value="team_member">Team Member</option>
                  <option value="stakeholder">Stakeholder</option>
                  <option value="billing_contact">Billing</option>
                </select>
                <button @click="removeContact(pc.contact_id)" class="text-red-400 hover:text-red-600 text-xs">Remove</button>
              </div>
            </div>
            <p v-if="projectContacts.length === 0" class="text-gray-400 text-sm">No team members assigned</p>

            <div class="mt-3">
              <ContactPicker
                placeholder="Add team member..."
                :exclude="projectContacts.map(pc => pc.contact_id)"
                @select="addContact"
              />
            </div>
          </div>

          <!-- Milestones -->
          <div class="border-t pt-4">
            <div class="flex justify-between items-center mb-3">
              <h4 class="font-bold">Milestones</h4>
              <button @click="showMilestoneForm = true" class="text-xs text-indigo-600 hover:text-indigo-800">+ Add</button>
            </div>
            <div v-for="ms in milestones" :key="ms.id" class="flex items-center gap-2 py-2 border-b">
              <input
                type="checkbox"
                :checked="!!ms.completed_at"
                @change="toggleMilestone(ms.id)"
                class="rounded"
              />
              <div class="flex-1">
                <p class="text-sm" :class="ms.completed_at ? 'line-through text-gray-400' : ''">{{ ms.title }}</p>
                <p v-if="ms.due_date" class="text-xs" :class="!ms.completed_at && isOverdue(ms.due_date) ? 'text-red-500' : 'text-gray-400'">
                  Due: {{ ms.due_date }}
                </p>
              </div>
              <button @click="deleteMilestone(ms.id)" class="text-red-400 hover:text-red-600 text-xs">&times;</button>
            </div>
            <p v-if="milestones.length === 0" class="text-gray-400 text-sm">No milestones</p>

            <!-- Add Milestone inline form -->
            <div v-if="showMilestoneForm" class="mt-3 space-y-2">
              <input v-model="msForm.title" placeholder="Milestone title" class="w-full border rounded px-3 py-2 text-sm" />
              <input v-model="msForm.due_date" type="date" class="w-full border rounded px-3 py-2 text-sm" />
              <div class="flex gap-2">
                <button @click="addMilestone" class="bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-500">Add</button>
                <button @click="showMilestoneForm = false" class="bg-gray-200 px-3 py-1 rounded text-sm hover:bg-gray-300">Cancel</button>
              </div>
            </div>
          </div>

          <!-- Communication History -->
          <CommunicationTimeline :project-id="detailProject.id" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import Modal from '../components/Modal.vue'
import Badge from '../components/Badge.vue'
import BudgetBar from '../components/BudgetBar.vue'
import ContactPicker from '../components/ContactPicker.vue'
import CommunicationTimeline from '../components/CommunicationTimeline.vue'
import { useProjectsStore } from '../stores/projects'
import { api } from '../api'

const store = useProjectsStore()
const showForm = ref(false)
const editing = ref(null)
const detailProject = ref(null)
const summary = ref(null)
const summaryLoading = ref(false)
const projectContacts = ref([])
const milestones = ref([])
const showMilestoneForm = ref(false)
const msForm = reactive({ title: '', due_date: '' })
const filterStatus = ref('all')
const currencies = ['USD', 'EUR', 'GBP', 'IDR', 'JPY', 'AUD', 'SGD', 'MYR', 'CNY', 'CAD']
const form = reactive({
  title: '', description: '', status: 'active', value: 0, budget: 0,
  actual_cost: 0, currency: 'USD', start_date: '', end_date: '',
})

onMounted(() => loadProjects())

function loadProjects() {
  store.fetchProjects(filterStatus.value === 'all' ? '' : filterStatus.value)
}

function fmtNum(n) {
  if (n == null) return '0'
  return Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function openAddForm() {
  editing.value = null
  Object.assign(form, {
    title: '', description: '', status: 'active', value: 0, budget: 0,
    actual_cost: 0, currency: 'USD', start_date: '', end_date: '',
  })
  showForm.value = true
}

function startEdit(project) {
  editing.value = project.id
  Object.assign(form, {
    title: project.title,
    description: project.description,
    status: project.status,
    value: project.value,
    budget: project.budget || 0,
    actual_cost: project.actual_cost || 0,
    currency: project.currency || 'USD',
    start_date: project.start_date || '',
    end_date: project.end_date || '',
  })
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editing.value = null
}

async function save() {
  if (editing.value) {
    await store.updateProject(editing.value, { ...form })
  } else {
    await store.createProject({ ...form })
  }
  closeForm()
  await loadProjects()
  if (detailProject.value) {
    detailProject.value = store.projects.find(p => p.id === detailProject.value.id) || null
    if (detailProject.value) loadSummary(detailProject.value.id)
  }
}

async function handleDelete(id) {
  if (confirm('Delete project?')) {
    await store.deleteProject(id)
    loadProjects()
    if (detailProject.value?.id === id) detailProject.value = null
  }
}

async function openDetail(project) {
  detailProject.value = project
  summary.value = null
  await Promise.all([
    loadSummary(project.id),
    loadProjectContacts(project.id),
    loadMilestones(project.id),
  ])
}

async function loadSummary(projectId) {
  summaryLoading.value = true
  try {
    summary.value = await api(`/api/projects/${projectId}/summary`)
  } catch {
    summary.value = null
  } finally {
    summaryLoading.value = false
  }
}

async function loadProjectContacts(projectId) {
  projectContacts.value = (await api(`/api/projects/${projectId}/contacts`)) || []
}

async function addContact(contact) {
  await api(`/api/projects/${detailProject.value.id}/contacts`, {
    method: 'POST',
    body: JSON.stringify({ contact_id: contact.id, role: 'team_member' }),
  })
  await loadProjectContacts(detailProject.value.id)
}

async function updateRole(contactId, role) {
  await api(`/api/projects/${detailProject.value.id}/contacts/${contactId}`, {
    method: 'PUT',
    body: JSON.stringify({ role }),
  })
  await loadProjectContacts(detailProject.value.id)
}

async function removeContact(contactId) {
  await api(`/api/projects/${detailProject.value.id}/contacts/${contactId}`, { method: 'DELETE' })
  await loadProjectContacts(detailProject.value.id)
}

// Milestones
async function loadMilestones(projectId) {
  milestones.value = (await api(`/api/projects/${projectId}/milestones`)) || []
}

async function addMilestone() {
  if (!msForm.title) return
  await api(`/api/projects/${detailProject.value.id}/milestones`, {
    method: 'POST',
    body: JSON.stringify({ title: msForm.title, due_date: msForm.due_date || null }),
  })
  msForm.title = ''
  msForm.due_date = ''
  showMilestoneForm.value = false
  await Promise.all([loadMilestones(detailProject.value.id), loadSummary(detailProject.value.id)])
}

async function toggleMilestone(msId) {
  await api(`/api/projects/${detailProject.value.id}/milestones/${msId}/complete`, { method: 'PATCH' })
  await Promise.all([loadMilestones(detailProject.value.id), loadSummary(detailProject.value.id)])
}

async function deleteMilestone(msId) {
  await api(`/api/projects/${detailProject.value.id}/milestones/${msId}`, { method: 'DELETE' })
  await Promise.all([loadMilestones(detailProject.value.id), loadSummary(detailProject.value.id)])
}

function isOverdue(dueDate) {
  if (!dueDate) return false
  return new Date(dueDate) < new Date()
}
</script>
