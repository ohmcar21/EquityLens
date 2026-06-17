"""
Portfolio & Holdings API Routes.

Thin controller layer — all business logic lives in PortfolioService.
Auth is skipped for Week 1; we use the demo user ID directly.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.schemas.holding import HoldingResponse, HoldingsSummary
from app.services.portfolio_service import PortfolioService
from app.broker.mock_broker import MockBroker

router = APIRouter(prefix="/api/v1/portfolio", tags=["Portfolio"])
settings = get_settings()


def _get_broker():
    """
    Factory for broker instance based on config.

    When BROKER_MODE=zerodha, this will return ZerodhaBroker instead.
    For now, always returns MockBroker.
    """
    # Future: if settings.broker_mode == "zerodha": return ZerodhaBroker(...)
    return MockBroker()


# ── GET /api/v1/portfolio/holdings ────────────────────────────────────────────

@router.get(
    "/holdings",
    response_model=HoldingsSummary,
    summary="Get all holdings with summary",
    description="Returns all holdings for the demo user with aggregate P&L summary. "
                "If no holdings exist, auto-syncs from the broker.",
)
async def get_holdings(db: AsyncSession = Depends(get_db)):
    """
    Fetch all holdings for the current user.
    Auth is skipped — uses demo user ID.
    """
    user_id = uuid.UUID(settings.demo_user_id)
    service = PortfolioService(db, _get_broker())

    try:
        summary = await service.get_holdings_summary(user_id)
        return HoldingsSummary(
            total_invested=summary["total_invested"],
            total_current_value=summary["total_current_value"],
            total_pnl=summary["total_pnl"],
            total_pnl_pct=summary["total_pnl_pct"],
            holdings_count=summary["holdings_count"],
            holdings=[
                HoldingResponse.model_validate(h)
                for h in summary["holdings"]
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── POST /api/v1/portfolio/sync ───────────────────────────────────────────────

@router.post(
    "/sync",
    response_model=list[HoldingResponse],
    summary="Sync holdings from broker",
    description="Pulls fresh holdings data from the broker (mock or Zerodha) "
                "and replaces the current holdings in the database.",
)
async def sync_holdings(db: AsyncSession = Depends(get_db)):
    """
    Force-sync holdings from broker into database.
    Deletes existing holdings, fetches fresh data from broker, inserts.
    """
    user_id = uuid.UUID(settings.demo_user_id)
    service = PortfolioService(db, _get_broker())

    try:
        holdings = await service.sync_holdings(user_id)
        return [HoldingResponse.model_validate(h) for h in holdings]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /api/v1/portfolio/holdings/{symbol} ───────────────────────────────────

@router.get(
    "/holdings/{symbol}",
    response_model=HoldingResponse,
    summary="Get a single holding by symbol",
)
async def get_holding_by_symbol(
    symbol: str,
    db: AsyncSession = Depends(get_db),
):
    """Fetch a specific holding by stock symbol."""
    user_id = uuid.UUID(settings.demo_user_id)
    service = PortfolioService(db, _get_broker())

    holdings = await service.get_holdings(user_id)
    holding = next(
        (h for h in holdings if h.symbol.upper() == symbol.upper()),
        None,
    )

    if holding is None:
        raise HTTPException(
            status_code=404,
            detail=f"Holding with symbol '{symbol}' not found",
        )

    return HoldingResponse.model_validate(holding)
