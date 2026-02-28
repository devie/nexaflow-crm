from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from nexaflow_crm.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
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
    created_at = Column(DateTime, default=func.now())

    owner = relationship("User", back_populates="contacts")
    projects = relationship("Project", back_populates="contact")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    status = Column(String, default="active")  # active, completed, on_hold
    value = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())

    owner = relationship("User", back_populates="projects")
    contact = relationship("Contact", back_populates="projects")
    invoices = relationship("Invoice", back_populates="project")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="unpaid")  # paid, unpaid
    due_date = Column(String, default="")
    created_at = Column(DateTime, default=func.now())

    project = relationship("Project", back_populates="invoices")
