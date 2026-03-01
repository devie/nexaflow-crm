# Changelog

All notable changes to NexaFlow CRM are documented here.

---

## [Unreleased] — 2026-03-01

### Added — Phase 0: Vue 3 Frontend
- **Vue 3 + Vite SPA** replacing vanilla JS frontend
- Pinia stores for auth, contacts, projects, invoices, dashboard
- Vue Router with hash-based routing
- Tailwind CSS v4 with Vite plugin
- Reusable components: Modal, Badge, BudgetBar, ContactPicker, CommunicationTimeline, Navbar
- FastAPI serves Vue `dist/` with SPA fallback
- Dev mode with `http://localhost:5173` CORS support

### Added — Phase 1: Contact-Project M2M
- **ProjectContact** many-to-many model with roles (PM, team member, stakeholder, billing contact)
- `POST/GET/PUT/DELETE /api/projects/{id}/contacts` endpoints
- `GET /api/contacts/{id}/projects` — contact's project list
- ContactPicker component (searchable dropdown)
- Contact notes field
- Project budget, actual_cost, start_date, end_date fields
- Project edit modal with grouped sections (Basic Info, Financials, Schedule)

### Added — Phase 2: Multi-Currency
- **ExchangeRateCache** model with 6-hour TTL
- `GET /api/currencies/rates?base=USD` endpoint (Frankfurter.app)
- `GET /api/currencies/supported` — static currency list
- Per-user preferred currency setting
- Currency selector in navbar (persists via `PUT /api/auth/me`)
- Dashboard shows amounts in user's preferred currency
- `httpx` dependency added

### Added — Phase 3: Invoice Workflow
- **InvoiceLineItem** model (description, quantity, unit_price, total)
- **CommunicationLog** model (user, contact, project, invoice, type, summary)
- 3-step invoice wizard (project → line items → review)
- Auto-generated invoice numbers (INV-0001 format)
- Professional HTML invoice template (inline CSS, PDF-compatible)
- PDF generation via xhtml2pdf
- `GET /api/invoices/{id}/preview` — HTML preview
- `GET /api/invoices/{id}/pdf` — PDF download
- `POST /api/invoices/{id}/send` — 3-mode delivery (email_only, pdf_only, email_and_pdf)
- Email open tracking with 1x1 transparent GIF pixel
- `GET /api/track/open/{token}` — no-auth tracking endpoint
- Communication log auto-entry on invoice send
- `POST /api/communication-log` — manual log entry
- `GET /api/contacts/{id}/history` and `/api/projects/{id}/history` — timelines
- `xhtml2pdf` dependency added

### Added — Phase 4: Milestones + Dashboard
- **Milestone** model (project, title, description, due_date, completed_at)
- `CRUD /api/projects/{id}/milestones` endpoints
- `PATCH /api/projects/{id}/milestones/{mid}/complete` — toggle completion
- Dashboard expanded: overdue invoices, projects over budget, upcoming milestones, monthly revenue (6 months)
- Milestone checkboxes in project detail with overdue highlighting

### Added — Product Architecture Redesign
- **3-level Project Summary Card** via `GET /api/projects/{id}/summary`:
  - Level 1 (Executive): project value, budget, actual cost, net margin, margin %
  - Level 2 (Financial): variance, invoiced, received, outstanding, cash flow position
  - Level 3 (Operational): schedule, PM, team count, milestones completed/overdue
- Project detail slide-over with full summary data
- Status filter tabs on project and invoice lists
- Account management page (`PUT /api/auth/me`)
- User dropdown menu in navbar (Account Settings, Logout)

### Changed
- Frontend migrated from Vanilla JS + Tailwind CDN to Vue 3 + Vite + Tailwind v4
- BudgetBar now tracks actual_cost vs budget (previously tracked value vs budget)
- Invoice detail slide-over widened to max-w-2xl with better layout
- Project cards show actual_cost on budget bar instead of project value

---

## [1eb604c] — 2026-03-01

### Added
- `email-validator` dependency for Pydantic EmailStr support

---

## [3631d5a] — 2026-02-28

### Added
- JWT authentication with bcrypt password hashing
- Rate limiting with slowapi (60/min per user)
- CORS protection with configurable origins
- Input validation on all endpoints
- Pagination limits (max 100 per page)
- Security headers

---

## [e8bab1c] — 2026-02-28

### Added
- Initial release: FastAPI + SQLAlchemy + SQLite
- User registration and login with JWT tokens
- Contacts CRUD (name, email, phone, company, tags, search)
- Projects CRUD (title, description, status, value, contact link)
- Invoices CRUD (amount, status, due date, project link)
- Dashboard with summary cards
- Vanilla JS + Tailwind CSS frontend
