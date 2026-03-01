from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from nexaflow_crm.auth import get_current_user
from nexaflow_crm.database import get_db
from nexaflow_crm.models import Contact, Project, ProjectContact, User
from nexaflow_crm.schemas import ProjectContactCreate, ProjectContactOut, ProjectContactUpdate

router = APIRouter(tags=["Project Contacts"])


def _get_user_project(project_id: int, db: Session, user: User) -> Project:
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/api/projects/{project_id}/contacts", response_model=ProjectContactOut, status_code=201)
def assign_contact(
    project_id: int,
    data: ProjectContactCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_user_project(project_id, db, user)
    contact = db.query(Contact).filter(Contact.id == data.contact_id, Contact.user_id == user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    existing = db.query(ProjectContact).filter(
        ProjectContact.project_id == project_id,
        ProjectContact.contact_id == data.contact_id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Contact already assigned to this project")

    pc = ProjectContact(project_id=project_id, contact_id=data.contact_id, role=data.role)
    db.add(pc)
    db.commit()
    db.refresh(pc)
    return _enrich_pc(pc)


@router.get("/api/projects/{project_id}/contacts", response_model=list[ProjectContactOut])
def list_project_contacts(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_user_project(project_id, db, user)
    pcs = db.query(ProjectContact).filter(ProjectContact.project_id == project_id).all()
    return [_enrich_pc(pc) for pc in pcs]


@router.put("/api/projects/{project_id}/contacts/{contact_id}", response_model=ProjectContactOut)
def update_project_contact(
    project_id: int,
    contact_id: int,
    data: ProjectContactUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_user_project(project_id, db, user)
    pc = db.query(ProjectContact).filter(
        ProjectContact.project_id == project_id,
        ProjectContact.contact_id == contact_id,
    ).first()
    if not pc:
        raise HTTPException(status_code=404, detail="Contact assignment not found")
    pc.role = data.role
    db.commit()
    db.refresh(pc)
    return _enrich_pc(pc)


@router.delete("/api/projects/{project_id}/contacts/{contact_id}", status_code=204)
def remove_project_contact(
    project_id: int,
    contact_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_user_project(project_id, db, user)
    pc = db.query(ProjectContact).filter(
        ProjectContact.project_id == project_id,
        ProjectContact.contact_id == contact_id,
    ).first()
    if not pc:
        raise HTTPException(status_code=404, detail="Contact assignment not found")
    db.delete(pc)
    db.commit()


@router.get("/api/contacts/{contact_id}/projects", response_model=list[ProjectContactOut])
def list_contact_projects(
    contact_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    pcs = db.query(ProjectContact).filter(ProjectContact.contact_id == contact_id).all()
    return [_enrich_pc(pc) for pc in pcs]


def _enrich_pc(pc: ProjectContact) -> dict:
    return {
        "id": pc.id,
        "project_id": pc.project_id,
        "contact_id": pc.contact_id,
        "role": pc.role,
        "contact_name": pc.contact.name if pc.contact else "",
        "contact_email": pc.contact.email if pc.contact else "",
        "created_at": pc.created_at,
    }
