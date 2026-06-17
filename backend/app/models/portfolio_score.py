"""
PortfolioScore ORM model.

Caches computed analytics scores (diversification, health) with their
sub-score breakdowns stored as JSONB. Keeps history for trend analysis.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PortfolioScore(Base):
    __tablename__ = "portfolio_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    score_type: Mapped[str] = mapped_column(String(50), nullable=False)
    overall_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    score_breakdown: Mapped[dict] = mapped_column(JSONB, default=dict)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # ── Constraints ───────────────────────────────────────────────────────
    __table_args__ = (
        UniqueConstraint(
            "user_id", "score_type", "calculated_at",
            name="uq_user_score_type_time"
        ),
    )

    # ── Relationships ─────────────────────────────────────────────────────
    user: Mapped["User"] = relationship(back_populates="scores")  # noqa: F821

    def __repr__(self) -> str:
        return f"<PortfolioScore {self.score_type}={self.overall_score}>"
