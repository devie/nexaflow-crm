from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from nexaflow_crm.auth import get_current_user
from nexaflow_crm.database import get_db
from nexaflow_crm.models import Invoice, Project, User
from nexaflow_crm.schemas import InvoiceCreate, InvoiceOut, InvoiceUpdate

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])


@router.get("", response_model=list[InvoiceOut])
def list_invoices(
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = (
        db.query(Invoice)
        .join(Project)
        .filter(Project.user_id == user.id)
    )
    if status:
        q = q.filter(Invoice.status == status)
    return q.order_by(Invoice.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()


@router.post("", response_model=InvoiceOut, status_code=201)
def create_invoice(data: InvoiceCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == data.project_id, Project.user_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    invoice = Invoice(**data.model_dump())
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    invoice = (
        db.query(Invoice)
        .join(Project)
        .filter(Invoice.id == invoice_id, Project.user_id == user.id)
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.put("/{invoice_id}", response_model=InvoiceOut)
def update_invoice(invoice_id: int, data: InvoiceUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    invoice = (
        db.query(Invoice)
        .join(Project)
        .filter(Invoice.id == invoice_id, Project.user_id == user.id)
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(invoice, field, value)
    db.commit()
    db.refresh(invoice)
    return invoice


@router.delete("/{invoice_id}", status_code=204)
def delete_invoice(invoice_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    invoice = (
        db.query(Invoice)
        .join(Project)
        .filter(Invoice.id == invoice_id, Project.user_id == user.id)
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    db.delete(invoice)
    db.commit()
