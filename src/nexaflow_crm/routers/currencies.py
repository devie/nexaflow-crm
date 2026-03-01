import json
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from nexaflow_crm.auth import get_current_user
from nexaflow_crm.database import get_db
from nexaflow_crm.models import ExchangeRateCache, User

router = APIRouter(prefix="/api/currencies", tags=["Currencies"])

CACHE_TTL_HOURS = 6

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
def get_rates(
    base: str = Query("USD", max_length=3),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    base = base.upper()
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=CACHE_TTL_HOURS)

    # Check cache
    cached = db.query(ExchangeRateCache).filter(ExchangeRateCache.base_currency == base).first()

    if cached and cached.fetched_at and cached.fetched_at.replace(tzinfo=timezone.utc) > cutoff:
        return {"base": base, "rates": json.loads(cached.rates_json), "cached": True}

    # Fetch fresh rates
    try:
        resp = httpx.get(f"https://api.frankfurter.app/latest?from={base}", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        rates = data.get("rates", {})
        rates_json = json.dumps(rates)

        if cached:
            cached.rates_json = rates_json
            cached.fetched_at = now
        else:
            cached = ExchangeRateCache(base_currency=base, rates_json=rates_json, fetched_at=now)
            db.add(cached)
        db.commit()
        return {"base": base, "rates": rates, "cached": False}

    except Exception:
        # Return stale cache if available
        if cached:
            return {"base": base, "rates": json.loads(cached.rates_json), "cached": True, "stale": True}
        return {"base": base, "rates": {}, "cached": False, "error": "Unable to fetch rates"}
