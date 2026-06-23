"""
Portfolio Service — Business logic for holdings management.

Orchestrates between the broker abstraction, database models, and the
API layer. Routes delegate to this service; this service owns the logic.
"""

import uuid
from decimal import Decimal

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.broker.interface import BrokerInterface
from app.models.holding import Holding
from app.models.portfolio_snapshot import PortfolioSnapshot


class PortfolioService:
    """Handles portfolio and holdings business logic."""

    def __init__(self, db: AsyncSession, broker: BrokerInterface):
        self.db = db
        self.broker = broker

    async def sync_holdings(self, user_id: uuid.UUID) -> list[Holding]:
        """
        Sync holdings from broker into the database.

        Strategy: Full replace (delete all existing → insert fresh from broker).
        This is correct for a portfolio snapshot model. If we needed incremental
        updates (e.g., tracking partial sells), we'd diff instead.

        When switching from MockBroker to ZerodhaBroker, this method's behavior
        is identical — only the broker.get_holdings() implementation changes.
        """
        # 1. Fetch fresh holdings from broker
        broker_holdings = await self.broker.get_holdings()

        # 2. Delete existing holdings for this user
        await self.db.execute(
            delete(Holding).where(Holding.user_id == user_id)
        )

        # 3. Insert fresh holdings
        db_holdings = []
        for bh in broker_holdings:
            holding = Holding(
                user_id=user_id,
                symbol=bh.symbol,
                exchange=bh.exchange,
                quantity=bh.quantity,
                average_price=bh.average_price,
                current_price=bh.current_price,
                sector=bh.sector,
                market_cap_category=bh.market_cap_category,
                day_change_pct=bh.day_change_pct,
            )
            self.db.add(holding)
            db_holdings.append(holding)

        await self.db.flush()  # assigns IDs without committing
        return db_holdings
    
    async def upload_holdings(
            self,
            user_id: uuid.UUID,
            records: list[dict],
        ) -> list[Holding]:

            # 1. Query max snapshot_id and calculate next_snapshot_id
            result = await self.db.execute(
                select(func.max(PortfolioSnapshot.snapshot_id))
                .where(PortfolioSnapshot.user_id == user_id)
            )
            max_snapshot_id = result.scalar()
            next_snapshot_id = 1 if max_snapshot_id is None else max_snapshot_id + 1

            # 2. Create PortfolioSnapshot rows from records
            for record in records:
                snapshot = PortfolioSnapshot(
                    user_id=user_id,
                    snapshot_id=next_snapshot_id,
                    symbol=record["symbol"],
                    exchange="NSE",
                    quantity=record["quantity"],
                    average_price=record["avg_price"],
                    current_price=record["current_price"],
                    sector="Unknown",
                    market_cap_category="LARGE",
                    day_change_pct=0,
                )
                self.db.add(snapshot)

            await self.db.execute(
            delete(Holding).where(Holding.user_id == user_id)
            )

            db_holdings = []

            for record in records:
                holding = Holding(
                    user_id=user_id,
                    symbol=record["symbol"],
                    exchange="NSE",
                    quantity=record["quantity"],
                    average_price=record["avg_price"],
                    current_price=record["current_price"],
                    sector="Unknown",
                    market_cap_category="LARGE",
                    day_change_pct=0,
                )

                self.db.add(holding)
                db_holdings.append(holding)

            await self.db.flush()
            return db_holdings

            

    async def get_holdings(self, user_id: uuid.UUID) -> list[Holding]:
        """
        Get all holdings for a user from the database.

        If no holdings exist yet, triggers a sync first.
        """
        result = await self.db.execute(
            select(Holding).where(Holding.user_id == user_id)
        )
        holdings = list(result.scalars().all())

        # Auto-sync if empty (first visit or cleared DB)
        if not holdings:
            holdings = await self.sync_holdings(user_id)

        return holdings

    async def get_holdings_summary(self, user_id: uuid.UUID) -> dict:
        """
        Get holdings with aggregate summary (total invested, P&L, etc.).
        """
        holdings = await self.get_holdings(user_id)

        total_invested = sum(h.invested_value for h in holdings)
        total_current = sum(h.current_value for h in holdings)
        total_pnl = total_current - total_invested
        total_pnl_pct = (
            (total_pnl / total_invested * 100) if total_invested > 0 else Decimal("0")
        )

        return {
            "total_invested": total_invested,
            "total_current_value": total_current,
            "total_pnl": total_pnl,
            "total_pnl_pct": round(total_pnl_pct, 2),
            "holdings_count": len(holdings),
            "holdings": holdings,
        }

    def holdings_to_analytics_format(self, holdings: list[Holding]) -> list[dict]:
        """
        Convert ORM Holding objects to plain dicts for analytics engines.

        Analytics modules are pure functions that take dicts, not ORM models.
        This keeps analytics testable without SQLAlchemy.
        """
        return [
            {
                "symbol": h.symbol,
                "sector": h.sector or "Unknown",
                "market_cap_category": h.market_cap_category or "LARGE",
                "current_value": float(h.current_value),
                "invested_value": float(h.invested_value),
                "current_price": float(h.current_price),
                "average_price": float(h.average_price),
                "quantity": h.quantity,
            }
            for h in holdings
        ]
