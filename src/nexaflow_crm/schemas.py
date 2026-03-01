from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field


# Auth
class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=6, max_length=128)


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    preferred_currency: str = "USD"
    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)
    preferred_currency: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


# Contacts
class ContactCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: str = ""
    phone: str = ""
    company: str = ""
    tags: str = ""
    notes: str = ""


class ContactUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    tags: str | None = None
    notes: str | None = None


class ContactOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    company: str
    tags: str
    notes: str = ""
    created_at: datetime | None = None
    model_config = {"from_attributes": True}


# Projects
class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(default="", max_length=5000)
    contact_id: int | None = None
    status: Literal["active", "completed", "on_hold", "cancelled"] = "active"
    value: float = Field(default=0.0, ge=0)
    budget: float = Field(default=0.0, ge=0)
    actual_cost: float = Field(default=0.0, ge=0)
    currency: str = "USD"
    start_date: str = ""
    end_date: str = ""


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=5000)
    contact_id: int | None = None
    status: Literal["active", "completed", "on_hold", "cancelled"] | None = None
    value: float | None = Field(default=None, ge=0)
    budget: float | None = Field(default=None, ge=0)
    actual_cost: float | None = Field(default=None, ge=0)
    currency: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class ProjectOut(BaseModel):
    id: int
    title: str
    description: str
    contact_id: int | None
    status: str
    value: float
    budget: float = 0.0
    actual_cost: float = 0.0
    currency: str = "USD"
    start_date: str = ""
    end_date: str = ""
    created_at: datetime | None = None
    model_config = {"from_attributes": True}


# Project Summary — computed fields for detail view
class ProjectSummary(BaseModel):
    """All 3 levels of project summary in one response."""

    # --- Level 1: Executive ---
    id: int
    title: str
    status: str
    currency: str
    progress_pct: float          # milestones completed / total * 100
    project_value: float
    budget: float
    actual_cost: float
    net_margin: float            # value - actual_cost
    margin_pct: float            # net_margin / value * 100

    # --- Level 2: Financial ---
    variance: float              # budget - actual_cost
    invoiced_amount: float       # sum of all invoices
    received_payment: float      # sum of paid invoices
    outstanding_invoice: float   # invoiced - received
    cashflow_position: float     # received - actual_cost

    # --- Level 3: Operational ---
    start_date: str
    end_date: str
    pm_name: str                 # project manager name (from project_contacts role=pm)
    team_count: int
    milestones_completed: int
    milestones_total: int
    overdue_milestones: int

    # nested detail
    team_members: list[dict] = []
    milestones: list[dict] = []


# Project Contacts (M2M)
class ProjectContactCreate(BaseModel):
    contact_id: int
    role: Literal["pm", "team_member", "stakeholder", "billing_contact"] = "team_member"


class ProjectContactUpdate(BaseModel):
    role: Literal["pm", "team_member", "stakeholder", "billing_contact"]


class ProjectContactOut(BaseModel):
    id: int
    project_id: int
    contact_id: int
    role: str
    contact_name: str = ""
    contact_email: str = ""
    created_at: datetime | None = None
    model_config = {"from_attributes": True}


# Invoices
class InvoiceCreate(BaseModel):
    project_id: int
    amount: float = Field(..., gt=0)
    status: Literal["unpaid", "paid", "overdue", "cancelled"] = "unpaid"
    due_date: str = ""
    currency: str = "USD"
    title: str = ""
    notes: str = ""


class InvoiceUpdate(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    status: Literal["unpaid", "paid", "overdue", "cancelled"] | None = None
    due_date: str | None = None
    title: str | None = None
    notes: str | None = None


class InvoiceOut(BaseModel):
    id: int
    project_id: int
    amount: float
    status: str
    due_date: str
    currency: str = "USD"
    invoice_number: str | None = None
    title: str = ""
    notes: str = ""
    sent_at: datetime | None = None
    sent_to_email: str = ""
    opened_at: datetime | None = None
    created_at: datetime | None = None
    model_config = {"from_attributes": True}


# Invoice Line Items
class LineItemCreate(BaseModel):
    description: str = Field(..., min_length=1)
    quantity: float = Field(default=1.0, gt=0)
    unit_price: float = Field(default=0.0, ge=0)


class LineItemOut(BaseModel):
    id: int
    invoice_id: int
    description: str
    quantity: float
    unit_price: float
    total: float
    model_config = {"from_attributes": True}


# Communication Log
class CommunicationLogCreate(BaseModel):
    contact_id: int | None = None
    project_id: int | None = None
    invoice_id: int | None = None
    type: Literal["invoice_sent", "payment_received", "note", "call", "email"]
    summary: str = ""


class CommunicationLogOut(BaseModel):
    id: int
    user_id: int
    contact_id: int | None
    project_id: int | None
    invoice_id: int | None
    type: str
    summary: str
    created_at: datetime | None = None
    model_config = {"from_attributes": True}


# Milestones
class MilestoneCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: str = ""
    due_date: str | None = None


class MilestoneUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = None
    due_date: str | None = None


class MilestoneOut(BaseModel):
    id: int
    project_id: int
    title: str
    description: str
    due_date: str | None
    completed_at: datetime | None
    created_at: datetime | None = None
    model_config = {"from_attributes": True}


# Dashboard
class DashboardStats(BaseModel):
    total_contacts: int
    active_projects: int
    completed_projects: int
    total_project_value: float
    unpaid_total: float
    paid_total: float
    overdue_invoices: int = 0
    projects_over_budget: int = 0
    upcoming_milestones: list[MilestoneOut] = []
    monthly_revenue: list[dict] = []
