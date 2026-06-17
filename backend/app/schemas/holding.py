"""
Holding Pydantic schemas.

Includes computed fields (pnl, pnl_pct, invested_value, current_value)
that are calculated from the ORM model's properties.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, computed_field


class HoldingBase(BaseModel):
    symbol: str
    exchange: str = "NSE"
    quantity: int
    average_price: Decimal
    current_price: Decimal
    sector: str | None = None
    market_cap_category: str | None = None
    day_change_pct: Decimal = Decimal("0")


class HoldingCreate(HoldingBase):
    """Schema for creating a holding (used internally during sync)."""
    pass


class HoldingResponse(HoldingBase):
    """Schema returned in API responses — includes computed P&L fields."""
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    # ── Computed fields ───────────────────────────────────────────────────
    # These mirror the ORM model's @property methods so the API response
    # includes them without the frontend needing to compute them.
    @computed_field
    @property
    def invested_value(self) -> Decimal:
        return self.average_price * self.quantity

    @computed_field
    @property
    def current_value(self) -> Decimal:
        return self.current_price * self.quantity

    @computed_field
    @property
    def pnl(self) -> Decimal:
        return self.current_value - self.invested_value

    @computed_field
    @property
    def pnl_pct(self) -> Decimal:
        if self.invested_value == 0:
            return Decimal("0")
        return round((self.pnl / self.invested_value) * 100, 2)

    model_config = {"from_attributes": True}


class HoldingsSummary(BaseModel):
    """Aggregate summary of all holdings."""
    total_invested: Decimal
    total_current_value: Decimal
    total_pnl: Decimal
    total_pnl_pct: Decimal
    holdings_count: int
    holdings: list[HoldingResponse]
