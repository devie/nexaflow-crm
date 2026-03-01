<template>
  <div>
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold">Contacts</h2>
      <button @click="showForm = true" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-500">
        + Add Contact
      </button>
    </div>

    <div class="bg-white rounded-xl shadow overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th class="text-left p-3">Name</th>
            <th class="text-left p-3">Email</th>
            <th class="text-left p-3">Company</th>
            <th class="text-left p-3">Tags</th>
            <th class="p-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in store.contacts" :key="c.id" class="border-t">
            <td class="p-3 font-medium">{{ c.name }}</td>
            <td class="p-3">{{ c.email }}</td>
            <td class="p-3">{{ c.company }}</td>
            <td class="p-3">
              <span
                v-for="tag in parseTags(c.tags)"
                :key="tag"
                class="bg-gray-100 px-2 py-0.5 rounded text-xs mr-1"
              >{{ tag }}</span>
            </td>
            <td class="p-3 text-center space-x-2">
              <button @click="startEdit(c)" class="text-indigo-500 hover:text-indigo-700 text-xs">Edit</button>
              <button @click="handleDelete(c.id)" class="text-red-500 hover:text-red-700 text-xs">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="store.contacts.length === 0" class="p-6 text-center text-gray-400">No contacts yet</p>
    </div>

    <!-- Add/Edit Modal -->
    <Modal v-if="showForm" :title="editing ? 'Edit Contact' : 'New Contact'" @close="closeForm">
      <input v-model="form.name" placeholder="Name *" class="w-full border rounded px-3 py-2 mb-2" />
      <input v-model="form.email" placeholder="Email" class="w-full border rounded px-3 py-2 mb-2" />
      <input v-model="form.phone" placeholder="Phone" class="w-full border rounded px-3 py-2 mb-2" />
      <input v-model="form.company" placeholder="Company" class="w-full border rounded px-3 py-2 mb-2" />
      <input v-model="form.tags" placeholder="Tags (comma-separated)" class="w-full border rounded px-3 py-2 mb-4" />
      <div class="flex gap-2">
        <button @click="save" class="flex-1 bg-indigo-600 text-white py-2 rounded hover:bg-indigo-500">Save</button>
        <button @click="closeForm" class="flex-1 bg-gray-200 py-2 rounded hover:bg-gray-300">Cancel</button>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import Modal from '../components/Modal.vue'
import { useContactsStore } from '../stores/contacts'

const store = useContactsStore()
const showForm = ref(false)
const editing = ref(null)
const form = reactive({ name: '', email: '', phone: '', company: '', tags: '' })

onMounted(() => store.fetchContacts())

function parseTags(tags) {
  return tags ? tags.split(',').map(t => t.trim()).filter(Boolean) : []
}

function startEdit(contact) {
  editing.value = contact.id
  Object.assign(form, { name: contact.name, email: contact.email, phone: contact.phone, company: contact.company, tags: contact.tags })
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editing.value = null
  Object.assign(form, { name: '', email: '', phone: '', company: '', tags: '' })
}

async function save() {
  if (editing.value) {
    await store.updateContact(editing.value, { ...form })
  } else {
    await store.createContact({ ...form })
  }
  closeForm()
  store.fetchContacts()
}

async function handleDelete(id) {
  if (confirm('Delete contact?')) {
    await store.deleteContact(id)
    store.fetchContacts()
  }
}
</script>
