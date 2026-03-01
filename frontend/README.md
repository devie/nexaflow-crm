# NexaFlow CRM — Frontend

Vue 3 SPA for NexaFlow CRM. Communicates with the FastAPI backend via REST API.

## Tech Stack

- Vue 3 with `<script setup>` SFCs
- Vite (build + dev server)
- Pinia (state management)
- Vue Router (hash-based routing)
- Tailwind CSS v4 (@tailwindcss/vite plugin)

## Development

```bash
npm install
npm run dev
```

Dev server runs at `http://localhost:5173` and proxies API calls to the backend at `http://localhost:6001`.

## Build

```bash
npm run build
```

Output goes to `dist/` which is served by FastAPI in production.

## Structure

```
src/
├── api/          # Fetch wrapper with JWT auth
├── components/   # Modal, Badge, BudgetBar, ContactPicker, Navbar, etc.
├── stores/       # Pinia: auth, contacts, projects, invoices, dashboard
├── utils/        # Currency conversion helpers
├── views/        # LoginView, DashboardView, ContactsView, ProjectsView, InvoicesView, AccountView
├── router/       # Hash-based routes
├── App.vue
└── main.js
```
