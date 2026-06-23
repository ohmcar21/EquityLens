"""
Analytics Service — Orchestrates all portfolio analytics computations.

Pulls holdings from the portfolio service, runs them through the
analytics engines, and optionally caches results in portfolio_scores.
"""

import uuid
from decimal import Decimal
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.portfolio_snapshot import PortfolioSnapshot

from app.analytics.diversification import calculate_diversification_score
from app.analytics.health_score import calculate_health_score
from app.analytics.sector_analysis import calculate_sector_allocation
from app.broker.interface import BrokerInterface
from app.mock_data.portfolio_data import MOCK_PRICE_HISTORIES
from app.models.portfolio_score import PortfolioScore
from app.services.portfolio_service import PortfolioService


class AnalyticsService:
    """Orchestrates analytics computations for a user's portfolio."""

    def __init__(self, db: AsyncSession, broker: BrokerInterface):
        self.db = db
        self.broker = broker
        self.portfolio_service = PortfolioService(db, broker)

    async def _get_holdings_as_dicts(self, user_id: uuid.UUID) -> list[dict]:
        """Fetch holdings and convert to analytics-compatible dicts."""
        holdings = await self.portfolio_service.get_holdings(user_id)
        return self.portfolio_service.holdings_to_analytics_format(holdings)

    async def get_portfolio_comparison(self, user_id: uuid.UUID) -> dict:
        result = await self.db.execute(
            select(PortfolioSnapshot.snapshot_id)
            .where(PortfolioSnapshot.user_id == user_id)
            .distinct()
            .order_by(desc(PortfolioSnapshot.snapshot_id))
        )

        snapshot_ids = result.scalars().all()

        if len(snapshot_ids) < 2:
            return {
                "added_holdings": [],
                "removed_holdings": [],
                "quantity_changes": [],
            }

        latest_snapshot_id = snapshot_ids[0]
        previous_snapshot_id = snapshot_ids[1]

        latest_result = await self.db.execute(
            select(PortfolioSnapshot)
            .where(
                PortfolioSnapshot.user_id == user_id,
                PortfolioSnapshot.snapshot_id ==latest_snapshot_id
            )
        )
        latest_holdings = latest_result.scalars().all()

        previous_result = await self.db.execute(
            select(PortfolioSnapshot)
            .where(
                PortfolioSnapshot.user_id == user_id,
                PortfolioSnapshot.snapshot_id == previous_snapshot_id,
            )
        )

        previous_holdings = previous_result.scalars().all()

        latest_map = {
            holding.symbol: holding.quantity
            for holding in latest_holdings
        }

        previous_map={
            holding.symbol: holding.quantity
            for holding in previous_holdings
        }
        added_holdings = [
            symbol
            for symbol in latest_map
            if symbol not in previous_map
        ]

        removed_holdings = [
            symbol
            for symbol in previous_map
            if symbol not in latest_map
        ]  

        quantity_changes = []
        for symbol in latest_map:
            if symbol in previous_map:
                if latest_map[symbol] != previous_map[symbol]:
                    quantity_changes.append({
                        "symbol": symbol,
                        "previous_quantity": previous_map[symbol],
                        "current_quantity": latest_map[symbol],
                        "change": latest_map[symbol] - previous_map[symbol],
                    })
        return {
            "added_holdings": added_holdings,
            "removed_holdings": removed_holdings,
            "quantity_changes": quantity_changes,
        }
            

    async def get_diversification_score(self, user_id: uuid.UUID) -> dict:
        """
        Compute diversification score and cache it.
        """
        holdings_dicts = await self._get_holdings_as_dicts(user_id)
        result = calculate_diversification_score(holdings_dicts)

        # Cache the score
        await self._cache_score(user_id, "diversification", result)

        return result

    async def get_health_score(self, user_id: uuid.UUID) -> dict:
        """
        Compute health score (includes volatility and drawdown from price history).
        """
        holdings_dicts = await self._get_holdings_as_dicts(user_id)

        # Use mock price histories for MVP
        # In production, fetch from market data provider
        result = calculate_health_score(
            holdings_dicts,
            price_histories=MOCK_PRICE_HISTORIES,
        )

        # Cache the score
        await self._cache_score(user_id, "health", result)

        return result

    async def get_sector_allocation(self, user_id: uuid.UUID) -> dict:
        """Compute sector allocation breakdown."""
        holdings_dicts = await self._get_holdings_as_dicts(user_id)
        return calculate_sector_allocation(holdings_dicts)

    async def get_full_summary(self, user_id: uuid.UUID) -> dict:
        """
        Compute all analytics in one call.
        Used by the /analytics/{user_id}/summary endpoint.
        """
        holdings_dicts = await self._get_holdings_as_dicts(user_id)

        diversification = calculate_diversification_score(holdings_dicts)
        health = calculate_health_score(
            holdings_dicts,
            price_histories=MOCK_PRICE_HISTORIES,
        )
        sector_allocation = calculate_sector_allocation(holdings_dicts)

        # Cache both scores
        await self._cache_score(user_id, "diversification", diversification)
        await self._cache_score(user_id, "health", health)

        return {
            "diversification": diversification,
            "health": health,
            "sector_allocation": sector_allocation,
        }

    async def _cache_score(
        self, user_id: uuid.UUID, score_type: str, result: dict
    ) -> None:
        """
        Persist a computed score to portfolio_scores for historical tracking.
        """
        score = PortfolioScore(
            user_id=user_id,
            score_type=score_type,
            overall_score=result["overall_score"],
            score_breakdown={
                k: str(v) for k, v in result.get("breakdown", {}).items()
            },
            calculated_at=datetime.now(timezone.utc),
        )
        self.db.add(score)
        await self.db.flush()
