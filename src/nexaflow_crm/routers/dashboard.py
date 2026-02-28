from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from nexaflow_crm.auth import get_current_user
from nexaflow_crm.database import get_db
from nexaflow_crm.models import Contact, Invoice, Project, User
from nexaflow_crm.schemas import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardStats)
def get_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    total_contacts = db.query(func.count(Contact.id)).filter(Contact.user_id == user.id).scalar() or 0
    active_projects = db.query(func.count(Project.id)).filter(Project.user_id == user.id, Project.status == "active").scalar() or 0
    completed_projects = db.query(func.count(Project.id)).filter(Project.user_id == user.id, Project.status == "completed").scalar() or 0
    total_value = db.query(func.sum(Project.value)).filter(Project.user_id == user.id).scalar() or 0.0

    unpaid = (
        db.query(func.sum(Invoice.amount))
        .join(Project)
        .filter(Project.user_id == user.id, Invoice.status == "unpaid")
        .scalar() or 0.0
    )
    paid = (
        db.query(func.sum(Invoice.amount))
        .join(Project)
        .filter(Project.user_id == user.id, Invoice.status == "paid")
        .scalar() or 0.0
    )

    return DashboardStats(
        total_contacts=total_contacts,
        active_projects=active_projects,
        completed_projects=completed_projects,
        total_project_value=round(total_value, 2),
        unpaid_total=round(unpaid, 2),
        paid_total=round(paid, 2),
    )
