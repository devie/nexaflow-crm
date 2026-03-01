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


def _fmt_number(n: float) -> str:
    """Format number with thousand separators."""
    return f"{n:,.2f}"


def _generate_invoice_html(invoice: Invoice, user: User, base_url: str = "", for_pdf: bool = False) -> str:
    line_items_html = ""
    subtotal = 0.0
    for item in invoice.line_items:
        line_items_html += f"""
        <tr>
            <td style="padding:8px;border-bottom:1px solid #dddddd;">{item.description}</td>
            <td style="padding:8px;border-bottom:1px solid #dddddd;text-align:center;">{item.quantity:g}</td>
            <td style="padding:8px;border-bottom:1px solid #dddddd;text-align:right;">{_fmt_number(item.unit_price)}</td>
            <td style="padding:8px;border-bottom:1px solid #dddddd;text-align:right;">{_fmt_number(item.total)}</td>
        </tr>"""
        subtotal += item.total

    total = subtotal if subtotal > 0 else invoice.amount
    inv_num = invoice.invoice_number or f"INV-{invoice.id}"
    created = invoice.created_at.strftime("%B %d, %Y") if invoice.created_at else "N/A"

    tracking = ""
    if not for_pdf and invoice.tracking_token and base_url:
        tracking = f'<img src="{base_url}/api/track/open/{invoice.tracking_token}" width="1" height="1" alt="" />'

    title_row = f'<tr><td style="padding:2px 0;color:#666666;">Title:</td><td style="padding:2px 0;padding-left:8px;"><b>{invoice.title}</b></td></tr>' if invoice.title else ''
    due_row = f'<tr><td style="padding:2px 0;color:#666666;">Due Date:</td><td style="padding:2px 0;padding-left:8px;"><b>{invoice.due_date}</b></td></tr>' if invoice.due_date else ''
    notes_html = f'<table style="width:100%;margin-bottom:20px;"><tr><td style="background-color:#f5f5f5;padding:10px;font-size:11px;color:#666666;">{invoice.notes}</td></tr></table>' if invoice.notes else ''

    # xhtml2pdf-compatible HTML (no border-radius, no shorthand, explicit closing tags)
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Invoice {inv_num}</title>
    <style type="text/css">
        body {{
            font-family: Helvetica, Arial, sans-serif;
            color: #333333;
            font-size: 12px;
            margin: 0;
            padding: 0;
        }}
        .container {{
            padding: 30px;
        }}
        .header-table {{
            width: 100%;
            margin-bottom: 25px;
        }}
        .invoice-title {{
            font-size: 26px;
            font-weight: bold;
            color: #4f46e5;
        }}
        .invoice-number {{
            font-size: 13px;
            color: #888888;
            margin-top: 4px;
        }}
        .from-name {{
            font-size: 13px;
            font-weight: bold;
        }}
        .from-email {{
            font-size: 11px;
            color: #888888;
        }}
        .meta-table {{
            width: 100%;
            margin-bottom: 20px;
        }}
        .amount-label {{
            font-size: 10px;
            color: #888888;
            text-align: right;
        }}
        .amount-value {{
            font-size: 22px;
            font-weight: bold;
            color: #4f46e5;
            text-align: right;
        }}
        .items-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .items-table th {{
            background-color: #f0f0f0;
            padding: 8px;
            text-align: left;
            font-weight: bold;
            font-size: 11px;
            border-bottom: 2px solid #cccccc;
        }}
        .items-table th.right {{
            text-align: right;
        }}
        .items-table th.center {{
            text-align: center;
        }}
        .totals-table {{
            width: 250px;
            margin-left: auto;
            margin-top: 15px;
        }}
        .totals-table td {{
            padding: 4px 8px;
            font-size: 12px;
        }}
        .totals-table .label {{
            color: #888888;
        }}
        .totals-table .total-row td {{
            padding-top: 10px;
            font-size: 15px;
            font-weight: bold;
            border-top: 2px solid #333333;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 15px;
            border-top: 1px solid #dddddd;
            text-align: center;
            font-size: 10px;
            color: #aaaaaa;
        }}
    </style>
</head>
<body>
<div class="container">
    <!-- Header -->
    <table class="header-table">
        <tr>
            <td style="vertical-align:top;width:60%;">
                <div class="invoice-title">INVOICE</div>
                <div class="invoice-number">{inv_num}</div>
            </td>
            <td style="vertical-align:top;text-align:right;width:40%;">
                <div class="from-name">{user.name}</div>
                <div class="from-email">{user.email}</div>
            </td>
        </tr>
    </table>

    <!-- Meta Info -->
    <table class="meta-table">
        <tr>
            <td style="vertical-align:top;width:50%;">
                <table>
                    {title_row}
                    <tr><td style="padding:2px 0;color:#666666;">Date:</td><td style="padding:2px 0;padding-left:8px;">{created}</td></tr>
                    {due_row}
                    <tr><td style="padding:2px 0;color:#666666;">Currency:</td><td style="padding:2px 0;padding-left:8px;">{invoice.currency}</td></tr>
                </table>
            </td>
            <td style="vertical-align:top;width:50%;">
                <div class="amount-label">AMOUNT DUE</div>
                <div class="amount-value">{invoice.currency} {_fmt_number(total)}</div>
            </td>
        </tr>
    </table>

    {notes_html}

    <!-- Line Items -->
    <table class="items-table">
        <thead>
            <tr>
                <th>Description</th>
                <th class="center" style="width:50px;">Qty</th>
                <th class="right" style="width:100px;">Unit Price</th>
                <th class="right" style="width:100px;">Total</th>
            </tr>
        </thead>
        <tbody>{line_items_html}</tbody>
    </table>

    <!-- Totals -->
    <table class="totals-table">
        <tr>
            <td class="label">Subtotal</td>
            <td style="text-align:right;">{invoice.currency} {_fmt_number(subtotal)}</td>
        </tr>
        <tr class="total-row">
            <td>Total</td>
            <td style="text-align:right;">{invoice.currency} {_fmt_number(total)}</td>
        </tr>
    </table>

    <!-- Footer -->
    <div class="footer">
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
    mode: str = Query("email_only", pattern="^(email_only|pdf_only|email_and_pdf)$"),
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
