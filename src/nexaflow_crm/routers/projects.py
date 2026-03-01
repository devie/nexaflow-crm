from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from nexaflow_crm.auth import get_current_user
from nexaflow_crm.database import get_db
from nexaflow_crm.models import Invoice, Milestone, Project, ProjectContact, User
from nexaflow_crm.schemas import ProjectCreate, ProjectOut, ProjectSummary, ProjectUpdate

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectOut])
def list_projects(
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Project).filter(Project.user_id == user.id)
    if status:
        q = q.filter(Project.status == status)
    return q.order_by(Project.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = Project(user_id=user.id, **data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/{project_id}/summary", response_model=ProjectSummary)
def get_project_summary(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Financial computations from invoices
    invoiced_amount = (
        db.query(func.sum(Invoice.amount))
        .filter(Invoice.project_id == project_id, Invoice.status != "cancelled")
        .scalar() or 0.0
    )
    received_payment = (
        db.query(func.sum(Invoice.amount))
        .filter(Invoice.project_id == project_id, Invoice.status == "paid")
        .scalar() or 0.0
    )

    val = project.value or 0.0
    cost = project.actual_cost or 0.0
    bgt = project.budget or 0.0
    net_margin = val - cost
    margin_pct = round((net_margin / val) * 100, 1) if val > 0 else 0.0

    # Milestones
    all_milestones = db.query(Milestone).filter(Milestone.project_id == project_id).all()
    ms_total = len(all_milestones)
    ms_completed = sum(1 for m in all_milestones if m.completed_at)
    today_str = date.today().isoformat()
    ms_overdue = sum(1 for m in all_milestones if not m.completed_at and m.due_date and m.due_date < today_str)
    progress_pct = round((ms_completed / ms_total) * 100, 1) if ms_total > 0 else 0.0

    # Team
    pcs = db.query(ProjectContact).filter(ProjectContact.project_id == project_id).all()
    pm_name = ""
    team_members = []
    for pc in pcs:
        name = pc.contact.name if pc.contact else "Unknown"
        email = pc.contact.email if pc.contact else ""
        if pc.role == "pm" and not pm_name:
            pm_name = name
        team_members.append({"name": name, "email": email, "role": pc.role})

    milestones_list = [
        {
            "id": m.id,
            "title": m.title,
            "due_date": m.due_date,
            "completed": m.completed_at is not None,
            "overdue": not m.completed_at and bool(m.due_date) and m.due_date < today_str,
        }
        for m in all_milestones
    ]

    return ProjectSummary(
        id=project.id,
        title=project.title,
        status=project.status,
        currency=project.currency or "USD",
        progress_pct=progress_pct,
        project_value=round(val, 2),
        budget=round(bgt, 2),
        actual_cost=round(cost, 2),
        net_margin=round(net_margin, 2),
        margin_pct=margin_pct,
        variance=round(bgt - cost, 2),
        invoiced_amount=round(invoiced_amount, 2),
        received_payment=round(received_payment, 2),
        outstanding_invoice=round(invoiced_amount - received_payment, 2),
        cashflow_position=round(received_payment - cost, 2),
        start_date=project.start_date or "",
        end_date=project.end_date or "",
        pm_name=pm_name,
        team_count=len(pcs),
        milestones_completed=ms_completed,
        milestones_total=ms_total,
        overdue_milestones=ms_overdue,
        team_members=team_members,
        milestones=milestones_list,
    )


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
