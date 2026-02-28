# NexaFlow CRM

Lightweight CRM for freelancers — manage clients, projects, and invoices.

## Features

- **User Authentication** — Register/login with JWT tokens
- **Contacts Management** — Name, email, phone, company, tags with search
- **Project Tracking** — Link to contacts, status (active/on hold/completed), value
- **Invoice Management** — Link to projects, paid/unpaid status, due dates
- **Dashboard** — Summary cards: total clients, active projects, unpaid invoices
- **Responsive UI** — Clean, modern interface with Tailwind CSS

## Tech Stack

- FastAPI + SQLAlchemy + SQLite
- JWT authentication (python-jose + passlib/bcrypt)
- Vanilla JS + Tailwind CSS (CDN)
- uv for dependency management

## Quick Start

```bash
uv sync
uv run nexaflow-crm
```

Server starts at `http://localhost:6001`

1. Register a new account
2. Add contacts, create projects, generate invoices
3. Track everything from the dashboard

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Get JWT token |
| GET | `/api/dashboard` | Dashboard stats |
| CRUD | `/api/contacts` | Manage contacts |
| CRUD | `/api/projects` | Manage projects |
| CRUD | `/api/invoices` | Manage invoices |

## Live Demo

[crm.zuhdi.id](https://crm.zuhdi.id)
