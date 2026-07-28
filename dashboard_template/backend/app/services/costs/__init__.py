"""Costs services package."""

from datetime import datetime

from app.config import settings
from app.services.costs.generic import calculate_generic_costs


def calculate_costs(from_date: datetime, to_date: datetime) -> dict:
    """Calculate costs based on generic unit pricing configuration."""
    if settings.costs_unit_price > 0 and settings.costs_unit_name:
        return calculate_generic_costs(
            from_date=from_date,
            to_date=to_date,
            unit_price=settings.costs_unit_price,
            unit_name=settings.costs_unit_name,
            currency=settings.costs_currency,
        )

    return {
        "total_cost": 0,
        "cost_by_category": {},
        "unit_economics": {},
        "projections": [],
        "notes": [
            "Costs module not configured",
            "Set COSTS_UNIT_PRICE and COSTS_UNIT_NAME for generic pricing",
        ],
    }
