from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import extract
from sqlalchemy.orm import Session

from nexaflow_crm.auth import get_current_user
from nexaflow_crm.currency_service import convert_amount
from nexaflow_crm.database import get_db
from nexaflow_crm.models import Contact, Invoice, Milestone, Project, User
from nexaflow_crm.schemas import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardStats)
def get_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    target_currency = user.preferred_currency or "USD"

    total_contacts = db.query(Contact).filter(Contact.user_id == user.id).count()

    # Projects
    user_projects = db.query(Project).filter(Project.user_id == user.id).all()
    active_projects = sum(1 for p in user_projects if p.status == "active")
    completed_projects = sum(1 for p in user_projects if p.status == "completed")

    # Convert each project value from its own currency to target
    total_value = 0.0
    projects_over_budget = 0
    for p in user_projects:
        p_currency = p.currency or "USD"
        converted_value = convert_amount(p.value or 0, p_currency, target_currency, db)
        total_value += converted_value
        if p.budget and p.budget > 0:
            converted_cost = convert_amount(p.actual_cost or 0, p_currency, target_currency, db)
            converted_budget = convert_amount(p.budget, p_currency, target_currency, db)
            if converted_cost > converted_budget:
                projects_over_budget += 1

    # Invoices — convert each from its own currency
    user_invoices = (
        db.query(Invoice)
        .join(Project)
        .filter(Project.user_id == user.id)
        .all()
    )

    unpaid = 0.0
    paid = 0.0
    overdue_invoices = 0
    today_str = date.today().isoformat()

    for inv in user_invoices:
        inv_currency = inv.currency or "USD"
        converted = convert_amount(inv.amount or 0, inv_currency, target_currency, db)
        if inv.status == "unpaid":
            unpaid += converted
            if inv.due_date and inv.due_date < today_str:
                overdue_invoices += 1
        elif inv.status == "paid":
            paid += converted

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

    # Monthly revenue (last 6 months) — paid invoices, converted
    monthly_revenue = []
    today = date.today()
    for i in range(5, -1, -1):
        month = today.month - i
        year = today.year
        while month <= 0:
            month += 12
            year -= 1

        month_total = 0.0
        for inv in user_invoices:
            if inv.status != "paid" or not inv.created_at:
                continue
            if inv.created_at.year == year and inv.created_at.month == month:
                inv_currency = inv.currency or "USD"
                month_total += convert_amount(inv.amount or 0, inv_currency, target_currency, db)

        monthly_revenue.append({
            "month": f"{year}-{month:02d}",
            "revenue": round(month_total, 2),
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
