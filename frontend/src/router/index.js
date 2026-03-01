import { createRouter, createWebHashHistory } from 'vue-router'
import { getToken } from '../api'

import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import ContactsView from '../views/ContactsView.vue'
import ProjectsView from '../views/ProjectsView.vue'
import InvoicesView from '../views/InvoicesView.vue'
import AccountView from '../views/AccountView.vue'

const routes = [
  { path: '/login', name: 'login', component: LoginView, meta: { guest: true } },
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'dashboard', component: DashboardView },
  { path: '/contacts', name: 'contacts', component: ContactsView },
  { path: '/projects', name: 'projects', component: ProjectsView },
  { path: '/invoices', name: 'invoices', component: InvoicesView },
  { path: '/account', name: 'account', component: AccountView },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = getToken()
  if (!to.meta.guest && !token) return { name: 'login' }
  if (to.meta.guest && token) return { name: 'dashboard' }
})

export default router
