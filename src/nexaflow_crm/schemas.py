from datetime import datetime
from enum import Enum
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
    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


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


class ContactUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    tags: str | None = None


class ContactOut(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    company: str
    tags: str
    created_at: datetime | None = None
    model_config = {"from_attributes": True}


# Projects
class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(default="", max_length=5000)
    contact_id: int | None = None
    status: Literal["active", "completed", "on_hold", "cancelled"] = "active"
    value: float = Field(default=0.0, ge=0)


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    description: str | None = Field(default=None, max_length=5000)
    contact_id: int | None = None
    status: Literal["active", "completed", "on_hold", "cancelled"] | None = None
    value: float | None = Field(default=None, ge=0)


class ProjectOut(BaseModel):
    id: int
    title: str
    description: str
    contact_id: int | None
    status: str
    value: float
    created_at: datetime | None = None
    model_config = {"from_attributes": True}


# Invoices
class InvoiceCreate(BaseModel):
    project_id: int
    amount: float = Field(..., gt=0)
    status: Literal["unpaid", "paid", "overdue", "cancelled"] = "unpaid"
    due_date: str = ""


class InvoiceUpdate(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    status: Literal["unpaid", "paid", "overdue", "cancelled"] | None = None
    due_date: str | None = None


class InvoiceOut(BaseModel):
    id: int
    project_id: int
    amount: float
    status: str
    due_date: str
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
