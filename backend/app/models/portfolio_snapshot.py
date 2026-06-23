"""
PortfolioSnapshot ORM model.

Represents a historical snapshot of a user's holdings at a specific point in time.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    snapshot_id: Mapped[int] = mapped_column(Integer, nullable=False)
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

    # ── Constraints ───────────────────────────────────────────────────────
    __table_args__ = (
        UniqueConstraint(
            "snapshot_id", "user_id", "symbol", "exchange",
            name="uq_snapshot_user_symbol_exchange"
        ),
    )

    # ── Relationships ─────────────────────────────────────────────────────
    user: Mapped["User"] = relationship(back_populates="snapshots")  # noqa: F821

    def __repr__(self) -> str:
        return f"<PortfolioSnapshot {self.snapshot_id} symbol={self.symbol} qty={self.quantity}>"
