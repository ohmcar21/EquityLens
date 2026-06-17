"""
Analytics Pydantic schemas.

Response schemas for diversification score, health score, sector allocation,
and the combined analytics summary endpoint.
"""

from decimal import Decimal

from pydantic import BaseModel


# ── Diversification Score ─────────────────────────────────────────────────────

class DiversificationBreakdown(BaseModel):
    """Sub-scores for the 4 diversification dimensions."""
    sector_spread: Decimal          # 0–100: entropy-based sector evenness
    stock_concentration: Decimal    # 0–100: inverse HHI of position sizes
    market_cap_mix: Decimal         # 0–100: balance across large/mid/small
    correlation_risk: Decimal       # 0–100: sector correlation penalty


class DiversificationScoreResponse(BaseModel):
    """Full diversification score response."""
    overall_score: Decimal          # 0–100 weighted composite
    grade: str                      # A/B/C/D/F letter grade
    breakdown: DiversificationBreakdown
    recommendations: list[str]      # actionable improvement suggestions


# ── Health Score ──────────────────────────────────────────────────────────────

class HealthBreakdown(BaseModel):
    """Sub-scores for the 5 health dimensions."""
    diversification: Decimal        # 0–100 (reuses diversification score)
    volatility: Decimal             # 0–100: lower volatility = higher score
    drawdown_risk: Decimal          # 0–100: lower max drawdown = higher score
    liquidity: Decimal              # 0–100: % in large-cap liquid stocks
    rebalancing_need: Decimal       # 0–100: lower drift = higher score


class HealthScoreResponse(BaseModel):
    """Full health score response."""
    overall_score: Decimal
    grade: str
    status: str                     # "Healthy", "Needs Attention", "At Risk"
    breakdown: HealthBreakdown
    recommendations: list[str]


# ── Sector Allocation ─────────────────────────────────────────────────────────

class SectorAllocation(BaseModel):
    """One sector's allocation details."""
    sector: str
    value: Decimal                  # total current value in this sector
    percentage: Decimal             # % of total portfolio
    holdings_count: int
    pnl: Decimal
    pnl_pct: Decimal


class SectorAllocationResponse(BaseModel):
    """Full sector allocation breakdown."""
    sectors: list[SectorAllocation]
    most_concentrated: str          # sector with highest weight
    least_concentrated: str         # sector with lowest weight


# ── Combined Analytics Summary ────────────────────────────────────────────────

class AnalyticsSummaryResponse(BaseModel):
    """Combined response for the /analytics/{user_id}/summary endpoint."""
    diversification: DiversificationScoreResponse
    health: HealthScoreResponse
    sector_allocation: SectorAllocationResponse
