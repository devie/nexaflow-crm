from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from nexaflow_crm.auth import get_current_user
from nexaflow_crm.currency_service import get_rates
from nexaflow_crm.database import get_db
from nexaflow_crm.models import User

router = APIRouter(prefix="/api/currencies", tags=["Currencies"])

SUPPORTED_CURRENCIES = [
    "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "SEK", "NZD",
    "MXN", "SGD", "HKD", "NOK", "KRW", "TRY", "INR", "RUB", "BRL", "ZAR",
    "IDR", "MYR", "THB", "PHP", "PLN", "CZK", "HUF", "ILS", "DKK", "ISK",
    "BGN", "HRK", "RON",
]


@router.get("/supported")
def get_supported_currencies(user: User = Depends(get_current_user)):
    return {"currencies": SUPPORTED_CURRENCIES}


@router.get("/rates")
def get_exchange_rates(
    base: str = Query("USD", max_length=3),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    base = base.upper()
    rates = get_rates(base, db)
    return {"base": base, "rates": rates}
