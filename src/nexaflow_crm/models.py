from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from nexaflow_crm.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    preferred_currency = Column(String, default="USD")
    created_at = Column(DateTime, default=func.now())

    contacts = relationship("Contact", back_populates="owner")
    projects = relationship("Project", back_populates="owner")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, default="")
    phone = Column(String, default="")
    company = Column(String, default="")
    tags = Column(String, default="")  # comma-separated
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=func.now())

    owner = relationship("User", back_populates="contacts")
    projects = relationship("Project", back_populates="contact")
    project_contacts = relationship("ProjectContact", back_populates="contact")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    status = Column(String, default="active")  # active, completed, on_hold, cancelled
    value = Column(Float, default=0.0)
    budget = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    start_date = Column(String, default="")
    end_date = Column(String, default="")
    created_at = Column(DateTime, default=func.now())

    owner = relationship("User", back_populates="projects")
    contact = relationship("Contact", back_populates="projects")
    invoices = relationship("Invoice", back_populates="project", cascade="all, delete-orphan")
    project_contacts = relationship("ProjectContact", back_populates="project", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")


class ProjectContact(Base):
    __tablename__ = "project_contacts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, default="team_member")  # pm, team_member, stakeholder, billing_contact
    created_at = Column(DateTime, default=func.now())

    project = relationship("Project", back_populates="project_contacts")
    contact = relationship("Contact", back_populates="project_contacts")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="unpaid")  # paid, unpaid, overdue, cancelled
    due_date = Column(String, default="")
    currency = Column(String, default="USD")
    invoice_number = Column(String, unique=True, nullable=True)
    title = Column(String, default="")
    notes = Column(Text, default="")
    sent_at = Column(DateTime, nullable=True)
    sent_to_email = Column(String, default="")
    opened_at = Column(DateTime, nullable=True)
    tracking_token = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=func.now())

    project = relationship("Project", back_populates="invoices")
    line_items = relationship("InvoiceLineItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceLineItem(Base):
    __tablename__ = "invoice_line_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    description = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit_price = Column(Float, default=0.0)
    total = Column(Float, default=0.0)

    invoice = relationship("Invoice", back_populates="line_items")


class ExchangeRateCache(Base):
    __tablename__ = "exchange_rate_cache"

    id = Column(Integer, primary_key=True, index=True)
    base_currency = Column(String, unique=True, nullable=False)
    rates_json = Column(String, nullable=False)
    fetched_at = Column(DateTime, nullable=False)


class CommunicationLog(Base):
    __tablename__ = "communication_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    type = Column(String, nullable=False)  # invoice_sent, payment_received, note, call, email
    summary = Column(Text, default="")
    created_at = Column(DateTime, default=func.now())


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    due_date = Column(String, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    project = relationship("Project", back_populates="milestones")
