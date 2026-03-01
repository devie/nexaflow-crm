from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from nexaflow_crm.auth import get_current_user
from nexaflow_crm.database import get_db
from nexaflow_crm.models import CommunicationLog, Contact, Project, User
from nexaflow_crm.schemas import CommunicationLogCreate, CommunicationLogOut

router = APIRouter(tags=["Communication Log"])


@router.get("/api/contacts/{contact_id}/history", response_model=list[CommunicationLogOut])
def contact_history(
    contact_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return (
        db.query(CommunicationLog)
        .filter(CommunicationLog.contact_id == contact_id, CommunicationLog.user_id == user.id)
        .order_by(CommunicationLog.created_at.desc())
        .all()
    )


@router.get("/api/projects/{project_id}/history", response_model=list[CommunicationLogOut])
def project_history(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return (
        db.query(CommunicationLog)
        .filter(CommunicationLog.project_id == project_id, CommunicationLog.user_id == user.id)
        .order_by(CommunicationLog.created_at.desc())
        .all()
    )


@router.post("/api/communication-log", response_model=CommunicationLogOut, status_code=201)
def create_log(
    data: CommunicationLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    log = CommunicationLog(user_id=user.id, **data.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
