import io
import os
import smtplib
import uuid
from datetime import datetime, timezone
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session
from xhtml2pdf import pisa

from nexaflow_crm.auth import get_current_user
from nexaflow_crm.database import get_db
from nexaflow_crm.models import (
    CommunicationLog,
    Invoice,
    InvoiceLineItem,
    Project,
    User,
)
from nexaflow_crm.schemas import LineItemCreate, LineItemOut

router = APIRouter(tags=["Invoice Workflow"])

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "")


def _get_user_invoice(invoice_id: int, db: Session, user: User) -> Invoice:
    invoice = (
        db.query(Invoice)
        .join(Project)
        .filter(Invoice.id == invoice_id, Project.user_id == user.id)
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


def _ensure_invoice_number(invoice: Invoice, db: Session, user: User) -> str:
    if not invoice.invoice_number:
        count = db.query(Invoice).join(Project).filter(Project.user_id == user.id).count()
        invoice.invoice_number = f"INV-{count:04d}"
        db.commit()
    return invoice.invoice_number


def _generate_invoice_html(invoice: Invoice, user: User, base_url: str = "", for_pdf: bool = False) -> str:
    line_items_html = ""
    subtotal = 0.0
    for item in invoice.line_items:
        line_items_html += f"""
        <tr>
            <td style="padding:10px 8px;border-bottom:1px solid #e5e7eb">{item.description}</td>
            <td style="padding:10px 8px;border-bottom:1px solid #e5e7eb;text-align:center">{item.quantity:g}</td>
            <td style="padding:10px 8px;border-bottom:1px solid #e5e7eb;text-align:right">{invoice.currency} {item.unit_price:,.2f}</td>
            <td style="padding:10px 8px;border-bottom:1px solid #e5e7eb;text-align:right">{invoice.currency} {item.total:,.2f}</td>
        </tr>"""
        subtotal += item.total

    total = subtotal if subtotal > 0 else invoice.amount
    inv_num = invoice.invoice_number or f"INV-{invoice.id}"
    created = invoice.created_at.strftime("%B %d, %Y") if invoice.created_at else "N/A"

    tracking = ""
    if not for_pdf and invoice.tracking_token and base_url:
        tracking = f'<img src="{base_url}/api/track/open/{invoice.tracking_token}" width="1" height="1" alt="" />'

    # PDF-friendly styles (no external CSS)
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/><title>Invoice {inv_num}</title></head>
<body style="font-family:Helvetica,Arial,sans-serif;color:#1f2937;margin:0;padding:0">
<div style="max-width:700px;margin:0 auto;padding:40px 30px">
    <!-- Header -->
    <table style="width:100%;margin-bottom:30px"><tr>
        <td style="vertical-align:top">
            <div style="font-size:28px;font-weight:bold;color:#4f46e5">INVOICE</div>
            <div style="font-size:14px;color:#6b7280;margin-top:4px">{inv_num}</div>
        </td>
        <td style="text-align:right;vertical-align:top">
            <div style="font-size:14px;font-weight:bold">{user.name}</div>
            <div style="font-size:13px;color:#6b7280">{user.email}</div>
        </td>
    </tr></table>

    <!-- Meta -->
    <table style="width:100%;margin-bottom:24px;font-size:13px">
    <tr>
        <td style="width:50%;vertical-align:top">
            {f'<div style="margin-bottom:4px"><span style="color:#6b7280">Title:</span> <strong>{invoice.title}</strong></div>' if invoice.title else ''}
            <div style="margin-bottom:4px"><span style="color:#6b7280">Date:</span> {created}</div>
            {f'<div style="margin-bottom:4px"><span style="color:#6b7280">Due:</span> {invoice.due_date}</div>' if invoice.due_date else ''}
        </td>
        <td style="width:50%;vertical-align:top;text-align:right">
            <div style="font-size:11px;color:#6b7280">AMOUNT DUE</div>
            <div style="font-size:24px;font-weight:bold;color:#4f46e5">{invoice.currency} {total:,.2f}</div>
        </td>
    </tr>
    </table>

    {f'<div style="background:#f9fafb;border-radius:6px;padding:12px;margin-bottom:24px;font-size:13px;color:#6b7280">{invoice.notes}</div>' if invoice.notes else ''}

    <!-- Line Items -->
    <table style="width:100%;border-collapse:collapse;font-size:13px">
        <thead>
            <tr style="background:#f3f4f6">
                <th style="padding:10px 8px;text-align:left;font-weight:600">Description</th>
                <th style="padding:10px 8px;text-align:center;font-weight:600;width:60px">Qty</th>
                <th style="padding:10px 8px;text-align:right;font-weight:600;width:120px">Unit Price</th>
                <th style="padding:10px 8px;text-align:right;font-weight:600;width:120px">Total</th>
            </tr>
        </thead>
        <tbody>{line_items_html}</tbody>
    </table>

    <!-- Total -->
    <table style="width:100%;margin-top:16px"><tr>
        <td></td>
        <td style="width:250px;text-align:right">
            <table style="width:100%;font-size:13px">
                <tr><td style="padding:4px 8px;color:#6b7280">Subtotal</td><td style="padding:4px 8px;text-align:right">{invoice.currency} {subtotal:,.2f}</td></tr>
                <tr style="font-size:16px;font-weight:bold;border-top:2px solid #1f2937">
                    <td style="padding:10px 8px">Total</td>
                    <td style="padding:10px 8px;text-align:right">{invoice.currency} {total:,.2f}</td>
                </tr>
            </table>
        </td>
    </tr></table>

    <!-- Footer -->
    <div style="margin-top:40px;padding-top:20px;border-top:1px solid #e5e7eb;font-size:11px;color:#9ca3af;text-align:center">
        Generated by NexaFlow CRM
    </div>
    {tracking}
</div>
</body>
</html>"""


def _html_to_pdf(html: str) -> bytes:
    buffer = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html), dest=buffer)
    return buffer.getvalue()


# --- Endpoints ---

@router.get("/api/invoices/{invoice_id}/preview", response_class=HTMLResponse)
def preview_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    invoice = _get_user_invoice(invoice_id, db, user)
    _ensure_invoice_number(invoice, db, user)
    return _generate_invoice_html(invoice, user)


@router.get("/api/invoices/{invoice_id}/pdf")
def download_pdf(
    invoice_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    invoice = _get_user_invoice(invoice_id, db, user)
    _ensure_invoice_number(invoice, db, user)
    html = _generate_invoice_html(invoice, user, for_pdf=True)
    pdf_bytes = _html_to_pdf(html)
    filename = f"{invoice.invoice_number or f'INV-{invoice.id}'}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.post("/api/invoices/{invoice_id}/send")
def send_invoice(
    invoice_id: int,
    to_email: str = Query(...),
    mode: str = Query("email_only", regex="^(email_only|pdf_only|email_and_pdf)$"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    invoice = _get_user_invoice(invoice_id, db, user)
    _ensure_invoice_number(invoice, db, user)

    # Generate tracking token
    if not invoice.tracking_token:
        invoice.tracking_token = str(uuid.uuid4())

    base_url = os.getenv("BASE_URL", "https://crm.zuhdi.id")
    html = _generate_invoice_html(invoice, user, base_url)
    pdf_bytes = _html_to_pdf(_generate_invoice_html(invoice, user, for_pdf=True))

    result = {"invoice_number": invoice.invoice_number}

    # PDF-only: just return the PDF bytes, no email
    if mode == "pdf_only":
        filename = f"{invoice.invoice_number}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'inline; filename="{filename}"'},
        )

    # Email modes
    if not SMTP_USER or not SMTP_PASSWORD:
        raise HTTPException(status_code=500, detail="SMTP not configured. Set SMTP_USER and SMTP_PASSWORD environment variables.")

    msg = MIMEMultipart("mixed")
    msg["Subject"] = f"Invoice {invoice.invoice_number}" + (f" — {invoice.title}" if invoice.title else "")
    msg["From"] = SMTP_FROM or SMTP_USER
    msg["To"] = to_email

    # HTML body
    msg.attach(MIMEText(html, "html"))

    # Attach PDF if mode is email_and_pdf
    if mode == "email_and_pdf":
        pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
        pdf_attachment.add_header("Content-Disposition", "attachment", filename=f"{invoice.invoice_number}.pdf")
        msg.attach(pdf_attachment)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    invoice.sent_at = datetime.now(timezone.utc)
    invoice.sent_to_email = to_email

    log = CommunicationLog(
        user_id=user.id,
        contact_id=None,
        project_id=invoice.project_id,
        invoice_id=invoice.id,
        type="invoice_sent",
        summary=f"Invoice {invoice.invoice_number} sent to {to_email}" + (" with PDF attached" if mode == "email_and_pdf" else ""),
    )
    db.add(log)
    db.commit()

    result["message"] = "Invoice sent" + (" with PDF" if mode == "email_and_pdf" else "")
    return result


@router.get("/api/track/open/{token}")
def track_open(token: str, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.tracking_token == token).first()
    if invoice and not invoice.opened_at:
        invoice.opened_at = datetime.now(timezone.utc)
        db.commit()
    gif = b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
    return Response(content=gif, media_type="image/gif")


# --- Line Items ---

@router.post("/api/invoices/{invoice_id}/line-items", response_model=LineItemOut, status_code=201)
def add_line_item(
    invoice_id: int,
    data: LineItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_user_invoice(invoice_id, db, user)
    total = round(data.quantity * data.unit_price, 2)
    item = InvoiceLineItem(
        invoice_id=invoice_id,
        description=data.description,
        quantity=data.quantity,
        unit_price=data.unit_price,
        total=total,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/api/invoices/{invoice_id}/line-items", response_model=list[LineItemOut])
def list_line_items(
    invoice_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_user_invoice(invoice_id, db, user)
    return db.query(InvoiceLineItem).filter(InvoiceLineItem.invoice_id == invoice_id).all()


@router.delete("/api/invoices/{invoice_id}/line-items/{item_id}", status_code=204)
def remove_line_item(
    invoice_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _get_user_invoice(invoice_id, db, user)
    item = db.query(InvoiceLineItem).filter(
        InvoiceLineItem.id == item_id,
        InvoiceLineItem.invoice_id == invoice_id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Line item not found")
    db.delete(item)
    db.commit()
