from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from nexaflow_crm.auth import get_current_user
from nexaflow_crm.database import get_db
from nexaflow_crm.models import Milestone, Project, User
from nexaflow_crm.schemas import MilestoneCreate, MilestoneOut, MilestoneUpdate

router = APIRouter(tags=["Milestones"])


def _get_user_project(project_id: int, db: Session, user: User) -> Project:
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/api/projects/{project_id}/milestones", response_model=list[MilestoneOut])
def list_milestones(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_user_project(project_id, db, user)
    return db.query(Milestone).filter(Milestone.project_id == project_id).order_by(Milestone.due_date.asc()).all()


@router.post("/api/projects/{project_id}/milestones", response_model=MilestoneOut, status_code=201)
def create_milestone(
    project_id: int,
    data: MilestoneCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_user_project(project_id, db, user)
    milestone = Milestone(project_id=project_id, **data.model_dump())
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


@router.put("/api/projects/{project_id}/milestones/{milestone_id}", response_model=MilestoneOut)
def update_milestone(
    project_id: int,
    milestone_id: int,
    data: MilestoneUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_user_project(project_id, db, user)
    milestone = db.query(Milestone).filter(
        Milestone.id == milestone_id, Milestone.project_id == project_id
    ).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(milestone, field, value)
    db.commit()
    db.refresh(milestone)
    return milestone


@router.delete("/api/projects/{project_id}/milestones/{milestone_id}", status_code=204)
def delete_milestone(
    project_id: int,
    milestone_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_user_project(project_id, db, user)
    milestone = db.query(Milestone).filter(
        Milestone.id == milestone_id, Milestone.project_id == project_id
    ).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    db.delete(milestone)
    db.commit()


@router.patch("/api/projects/{project_id}/milestones/{milestone_id}/complete", response_model=MilestoneOut)
def complete_milestone(
    project_id: int,
    milestone_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_user_project(project_id, db, user)
    milestone = db.query(Milestone).filter(
        Milestone.id == milestone_id, Milestone.project_id == project_id
    ).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    if milestone.completed_at:
        milestone.completed_at = None  # toggle uncomplete
    else:
        milestone.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(milestone)
    return milestone
