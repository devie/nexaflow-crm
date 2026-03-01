"""Shared currency conversion service used by dashboard and other modules."""

import json
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.orm import Session

from nexaflow_crm.models import ExchangeRateCache

CACHE_TTL_HOURS = 6


def get_rates(base: str, db: Session) -> dict:
    """Get exchange rates for a base currency. Returns {currency: rate} dict."""
    base = base.upper()
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=CACHE_TTL_HOURS)

    cached = db.query(ExchangeRateCache).filter(ExchangeRateCache.base_currency == base).first()

    if cached and cached.fetched_at and cached.fetched_at.replace(tzinfo=timezone.utc) > cutoff:
        return json.loads(cached.rates_json)

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
        return rates

    except Exception:
        if cached:
            return json.loads(cached.rates_json)
        return {}


def convert_amount(amount: float, from_currency: str, to_currency: str, db: Session) -> float:
    """Convert amount from one currency to another."""
    if not amount or from_currency == to_currency:
        return amount

    rates = get_rates(from_currency, db)
    if to_currency in rates:
        return amount * rates[to_currency]

    # Fallback: try reverse
    reverse_rates = get_rates(to_currency, db)
    if from_currency in reverse_rates and reverse_rates[from_currency] > 0:
        return amount / reverse_rates[from_currency]

    return amount
