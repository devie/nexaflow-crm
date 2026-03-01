from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from nexaflow_crm.auth import get_current_user
from nexaflow_crm.database import get_db
from nexaflow_crm.models import Contact, Invoice, Milestone, Project, User
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

    # Overdue invoices
    today_str = date.today().isoformat()
    overdue_invoices = (
        db.query(func.count(Invoice.id))
        .join(Project)
        .filter(
            Project.user_id == user.id,
            Invoice.status == "unpaid",
            Invoice.due_date != "",
            Invoice.due_date < today_str,
        )
        .scalar() or 0
    )

    # Projects over budget
    user_projects = db.query(Project).filter(Project.user_id == user.id, Project.budget > 0).all()
    projects_over_budget = sum(1 for p in user_projects if p.value > p.budget)

    # Upcoming milestones (next 5 with due_date, not completed)
    upcoming_milestones = (
        db.query(Milestone)
        .join(Project)
        .filter(
            Project.user_id == user.id,
            Milestone.completed_at.is_(None),
            Milestone.due_date.isnot(None),
            Milestone.due_date >= today_str,
        )
        .order_by(Milestone.due_date.asc())
        .limit(5)
        .all()
    )

    # Monthly revenue (last 6 months) — based on paid invoices created_at
    monthly_revenue = []
    today = date.today()
    for i in range(5, -1, -1):
        month = today.month - i
        year = today.year
        while month <= 0:
            month += 12
            year -= 1
        month_total = (
            db.query(func.sum(Invoice.amount))
            .join(Project)
            .filter(
                Project.user_id == user.id,
                Invoice.status == "paid",
                extract("year", Invoice.created_at) == year,
                extract("month", Invoice.created_at) == month,
            )
            .scalar() or 0.0
        )
        monthly_revenue.append({
            "month": f"{year}-{month:02d}",
            "revenue": round(float(month_total), 2),
        })

    return DashboardStats(
        total_contacts=total_contacts,
        active_projects=active_projects,
        completed_projects=completed_projects,
        total_project_value=round(total_value, 2),
        unpaid_total=round(unpaid, 2),
        paid_total=round(paid, 2),
        overdue_invoices=overdue_invoices,
        projects_over_budget=projects_over_budget,
        upcoming_milestones=upcoming_milestones,
        monthly_revenue=monthly_revenue,
    )
