# NexaFlow CRM

Lightweight CRM for freelancers — manage clients, projects, invoices, and communications from a single dashboard.

**Live Demo:** [crm.zuhdi.id](https://crm.zuhdi.id)

## Features

### Contacts Management
- Full CRUD with name, email, phone, company, tags, notes
- Search and pagination
- Contact-project many-to-many relationships with roles (PM, team member, stakeholder, billing contact)
- Communication history timeline per contact

### Project Tracking
- Project cards with status (active / on hold / completed / cancelled)
- 3-level Project Summary Card:
  - **Executive** — project value, budget, actual cost, net margin %
  - **Financial** — budget variance, invoiced/received/outstanding, cash flow position
  - **Operational** — schedule, PM, team count, milestone progress, overdue alerts
- Budget tracking with visual progress bar (green/yellow/red)
- Start/end date scheduling
- Team assignment with role management
- Milestone tracking with due dates and completion toggle

### Invoice Workflow
- 3-step invoice wizard (project → line items → review)
- Auto-generated invoice numbers (INV-0001, INV-0002, ...)
- Line items with quantity, unit price, auto-calculated totals
- Professional HTML invoice preview
- PDF generation (xhtml2pdf)
- 3-mode delivery:
  - **Email Only** — sends HTML invoice via SMTP
  - **Download PDF** — generates PDF for print/download
  - **Email + PDF** — sends email with PDF attachment
- Email open tracking (1x1 transparent pixel)
- Multi-currency support

### Multi-Currency
- 10 supported currencies (USD, EUR, GBP, IDR, JPY, AUD, SGD, MYR, CNY, CAD)
- Exchange rates from Frankfurter.app (ECB data, cached 6 hours)
- Per-user preferred currency with navbar selector
- Currency conversion across dashboard

### Communication Log
- Timeline view per contact or project
- Log types: invoice sent, payment received, note, call, email
- Auto-logged on invoice send

### Dashboard
- Summary cards: total contacts, active/completed projects, total value
- Financial cards: unpaid/paid invoices, overdue count, over-budget projects
- Monthly revenue bar chart (last 6 months)
- Upcoming milestones widget

### Security
- JWT authentication with bcrypt password hashing
- Rate limiting (slowapi)
- CORS protection
- Input validation and pagination limits

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy |
| Database | SQLite |
| Auth | JWT (python-jose), bcrypt |
| Frontend | Vue 3, Vite, Pinia, Vue Router |
| Styling | Tailwind CSS v4 |
| PDF | xhtml2pdf |
| Currency | httpx + Frankfurter.app |
| Email | SMTP (smtplib) |
| Deploy | uv, Cloudflare Tunnel |

## Quick Start

```bash
# Install dependencies
uv sync

# Run migration (first time or after updates)
uv run python scripts/migrate.py

# Build frontend
cd frontend && npm install && npm run build && cd ..

# Start server
uv run nexaflow-crm
```

Server starts at `http://localhost:6001`

### Development (with hot reload)

```bash
# Terminal 1: Backend
uv run nexaflow-crm

# Terminal 2: Frontend dev server
cd frontend && npm run dev
```

Frontend dev server at `http://localhost:5173` proxies API calls to `:6001`.

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_PATH` | SQLite database file | `nexaflow.db` |
| `JWT_SECRET` | Secret key for JWT tokens | (auto-generated) |
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USER` | SMTP username/email | (required for email) |
| `SMTP_PASSWORD` | SMTP password/app password | (required for email) |
| `SMTP_FROM` | Sender email address | (defaults to SMTP_USER) |
| `BASE_URL` | Public URL for tracking pixels | `https://crm.zuhdi.id` |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Get JWT token |
| GET/PUT | `/api/auth/me` | View/update profile |
| GET | `/api/dashboard` | Dashboard stats |
| CRUD | `/api/contacts` | Manage contacts |
| CRUD | `/api/projects` | Manage projects |
| GET | `/api/projects/{id}/summary` | 3-level project summary |
| CRUD | `/api/projects/{id}/contacts` | Team assignment |
| CRUD | `/api/projects/{id}/milestones` | Milestone tracking |
| PATCH | `/api/projects/{id}/milestones/{mid}/complete` | Toggle milestone |
| CRUD | `/api/invoices` | Manage invoices |
| CRUD | `/api/invoices/{id}/line-items` | Invoice line items |
| GET | `/api/invoices/{id}/preview` | HTML invoice preview |
| GET | `/api/invoices/{id}/pdf` | Download invoice PDF |
| POST | `/api/invoices/{id}/send` | Send invoice (email/pdf/both) |
| GET | `/api/track/open/{token}` | Email open tracking |
| GET | `/api/currencies/rates` | Exchange rates |
| GET/POST | `/api/communication-log` | Communication history |
| GET | `/api/contacts/{id}/history` | Contact timeline |
| GET | `/api/projects/{id}/history` | Project timeline |

## Project Structure

```
nexaflow-crm/
├── src/nexaflow_crm/
│   ├── main.py              # FastAPI app, static mount, router registration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # JWT authentication
│   ├── database.py          # Database connection
│   └── routers/
│       ├── auth_router.py       # Auth endpoints
│       ├── contacts.py          # Contacts CRUD
│       ├── projects.py          # Projects CRUD + summary
│       ├── invoices.py          # Invoices CRUD
│       ├── invoice_workflow.py  # PDF, email, tracking
│       ├── project_contacts.py  # M2M team assignment
│       ├── milestones.py        # Milestone CRUD
│       ├── currencies.py        # Exchange rates
│       ├── communication_log.py # Timeline entries
│       └── dashboard.py         # Dashboard stats
├── frontend/                # Vue 3 SPA
│   ├── src/
│   │   ├── views/           # Page components
│   │   ├── components/      # Reusable UI components
│   │   ├── stores/          # Pinia state management
│   │   ├── api/             # API client with auth
│   │   └── utils/           # Currency helpers
│   └── dist/                # Built frontend (served by FastAPI)
├── scripts/
│   └── migrate.py           # Database migration script
└── pyproject.toml
```

## License

MIT
