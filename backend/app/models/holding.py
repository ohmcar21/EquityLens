"""
Holding ORM model.

Represents a single stock position in a user's portfolio.
Sector and market_cap_category are denormalized here for fast analytics
queries — avoids joining to a separate stocks master table.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Holding(Base):
    __tablename__ = "holdings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    exchange: Mapped[str] = mapped_column(String(10), default="NSE")
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    average_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    current_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True)
    market_cap_category: Mapped[str | None] = mapped_column(String(20), nullable=True)
    day_change_pct: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("0"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Constraints ───────────────────────────────────────────────────────
    __table_args__ = (
        UniqueConstraint("user_id", "symbol", "exchange", name="uq_user_symbol_exchange"),
    )

    # ── Relationships ─────────────────────────────────────────────────────
    user: Mapped["User"] = relationship(back_populates="holdings")  # noqa: F821

    # ── Computed Properties ───────────────────────────────────────────────
    @property
    def invested_value(self) -> Decimal:
        """Total capital invested in this position."""
        return self.average_price * self.quantity

    @property
    def current_value(self) -> Decimal:
        """Current market value of this position."""
        return self.current_price * self.quantity

    @property
    def pnl(self) -> Decimal:
        """Absolute profit/loss."""
        return self.current_value - self.invested_value

    @property
    def pnl_pct(self) -> Decimal:
        """Percentage profit/loss."""
        if self.invested_value == 0:
            return Decimal("0")
        return (self.pnl / self.invested_value) * 100

    def __repr__(self) -> str:
        return f"<Holding {self.symbol} qty={self.quantity}>"
