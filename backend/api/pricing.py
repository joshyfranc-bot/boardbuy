"""Booking price calculation — single source of truth."""
from datetime import date
from decimal import Decimal

from django.conf import settings


def compute_media_price(unit, start: date, end: date) -> Decimal:
    """Best-rate pricing: fill months, then weeks, then days."""
    days = (end - start).days + 1
    if days <= 0:
        raise ValueError("end must be after start")
    months, rem = divmod(days, 28)
    weeks, day_r = divmod(rem, 7)
    price = (
        months * unit.price_monthly
        + weeks * unit.price_weekly
        + day_r * unit.price_daily
    )
    # never charge more than pure monthly pro-rata
    cap = unit.price_monthly * Decimal(days) / Decimal(28)
    return min(price, cap.quantize(Decimal("0.01")))


def commission_pct_for(unit) -> Decimal:
    override = unit.owner.commission_pct
    return override if override is not None else Decimal(str(settings.PLATFORM_COMMISSION_PCT))


def vat_pct() -> Decimal:
    return Decimal(str(settings.VAT_PCT))
