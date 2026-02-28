from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from nexaflow_crm.auth import get_current_user
from nexaflow_crm.database import get_db
from nexaflow_crm.models import Contact, User
from nexaflow_crm.schemas import ContactCreate, ContactOut, ContactUpdate

router = APIRouter(prefix="/api/contacts", tags=["Contacts"])


@router.get("", response_model=list[ContactOut])
def list_contacts(
    search: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Contact).filter(Contact.user_id == user.id)
    if search:
        q = q.filter(Contact.name.ilike(f"%{search}%"))
    return q.order_by(Contact.created_at.desc()).all()


@router.post("", response_model=ContactOut, status_code=201)
def create_contact(data: ContactCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    contact = Contact(user_id=user.id, **data.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.get("/{contact_id}", response_model=ContactOut)
def get_contact(contact_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=ContactOut)
def update_contact(contact_id: int, data: ContactUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/{contact_id}", status_code=204)
def delete_contact(contact_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user.id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
