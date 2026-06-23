"""
Analytics API Routes.

Endpoints for diversification score, health score, sector allocation,
and the combined analytics summary.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    DiversificationBreakdown,
    DiversificationScoreResponse,
    HealthBreakdown,
    HealthScoreResponse,
    SectorAllocation,
    SectorAllocationResponse,
    PortfolioComparisonResponse,
)
from app.services.analytics_service import AnalyticsService
from app.broker.mock_broker import MockBroker

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])
settings = get_settings()


def _get_broker():
    """Broker factory — same as in portfolio routes."""
    return MockBroker()


# ── GET /api/v1/analytics/summary ─────────────────────────────────────────────

@router.get(
    "/summary",
    response_model=AnalyticsSummaryResponse,
    summary="Full analytics summary",
    description="Returns diversification score, health score, and sector "
                "allocation in a single response.",
)
async def get_analytics_summary(db: AsyncSession = Depends(get_db)):
    """Combined analytics — one API call for the full dashboard."""
    user_id = uuid.UUID(settings.demo_user_id)
    service = AnalyticsService(db, _get_broker())

    try:
        result = await service.get_full_summary(user_id)
        return AnalyticsSummaryResponse(
            diversification=_build_diversification_response(result["diversification"]),
            health=_build_health_response(result["health"]),
            sector_allocation=_build_sector_response(result["sector_allocation"]),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /api/v1/analytics/diversification ─────────────────────────────────────

@router.get(
    "/diversification",
    response_model=DiversificationScoreResponse,
    summary="Diversification score",
    description="Computes a 0-100 diversification score based on sector spread, "
                "stock concentration, market cap mix, and correlation risk.",
)
async def get_diversification_score(db: AsyncSession = Depends(get_db)):
    user_id = uuid.UUID(settings.demo_user_id)
    service = AnalyticsService(db, _get_broker())

    try:
        result = await service.get_diversification_score(user_id)
        return _build_diversification_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /api/v1/analytics/health ──────────────────────────────────────────────

@router.get(
    "/health",
    response_model=HealthScoreResponse,
    summary="Portfolio health score",
    description="Computes a 0-100 health score from diversification, volatility, "
                "drawdown risk, liquidity, and rebalancing need.",
)
async def get_health_score(db: AsyncSession = Depends(get_db)):
    user_id = uuid.UUID(settings.demo_user_id)
    service = AnalyticsService(db, _get_broker())

    try:
        result = await service.get_health_score(user_id)
        return _build_health_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /api/v1/analytics/sector-allocation ───────────────────────────────────

@router.get(
    "/sector-allocation",
    response_model=SectorAllocationResponse,
    summary="Sector allocation breakdown",
    description="Shows portfolio allocation across sectors with per-sector P&L.",
)
async def get_sector_allocation(db: AsyncSession = Depends(get_db)):
    user_id = uuid.UUID(settings.demo_user_id)
    service = AnalyticsService(db, _get_broker())

    try:
        result = await service.get_sector_allocation(user_id)
        return _build_sector_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/history/compare",
    response_model=PortfolioComparisonResponse,
    summary="Compare latest portfolio snapshot with previous snapshot",
)
async def compare_portfolio_history(db: AsyncSession = Depends(get_db)):
    user_id = uuid.UUID(settings.demo_user_id)
    service = AnalyticsService(db, _get_broker())

    try:
        return await service.get_portfolio_comparison(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))        


# ── Response Builders ─────────────────────────────────────────────────────────
# These map raw dicts from analytics engines to Pydantic response schemas.


def _build_diversification_response(data: dict) -> DiversificationScoreResponse:
    return DiversificationScoreResponse(
        overall_score=data["overall_score"],
        grade=data["grade"],
        breakdown=DiversificationBreakdown(**data["breakdown"]),
        recommendations=data["recommendations"],
    )


def _build_health_response(data: dict) -> HealthScoreResponse:
    return HealthScoreResponse(
        overall_score=data["overall_score"],
        grade=data["grade"],
        status=data["status"],
        breakdown=HealthBreakdown(**data["breakdown"]),
        recommendations=data["recommendations"],
    )


def _build_sector_response(data: dict) -> SectorAllocationResponse:
    return SectorAllocationResponse(
        sectors=[SectorAllocation(**s) for s in data["sectors"]],
        most_concentrated=data["most_concentrated"],
        least_concentrated=data["least_concentrated"],
    )
