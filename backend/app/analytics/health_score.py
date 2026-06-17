"""
Portfolio Health Score Engine — Pure computation module.

Computes a 0–100 composite health score from 5 weighted sub-scores:
  1. Diversification (25%) — reuses the diversification score
  2. Volatility (20%) — portfolio-level std dev of daily returns
  3. Drawdown Risk (20%) — maximum simulated drawdown
  4. Liquidity (15%) — percentage in large-cap liquid stocks
  5. Rebalancing Need (20%) — drift from equal-weight target

Design decisions:
  - Pure functions, no DB dependency.
  - Volatility and drawdown use mock price history for now.
  - The "target allocation" for rebalancing is naive equal-weight
    (in production, this would be user-configurable).
"""

import math
from decimal import Decimal

from app.analytics.diversification import calculate_diversification_score


# ── Status Thresholds ─────────────────────────────────────────────────────────

def _score_to_grade(score: float) -> str:
    if score >= 80:
        return "A"
    elif score >= 65:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 35:
        return "D"
    else:
        return "F"


def _score_to_status(score: float) -> str:
    if score >= 70:
        return "Healthy"
    elif score >= 45:
        return "Needs Attention"
    else:
        return "At Risk"


# ── Sub-score 1: Diversification (delegates to diversification engine) ────────

def _get_diversification_subscore(holdings: list[dict]) -> float:
    """Reuse the diversification score as a health sub-score."""
    result = calculate_diversification_score(holdings)
    return float(result["overall_score"])


# ── Sub-score 2: Volatility ──────────────────────────────────────────────────

def _calculate_volatility_score(
    holdings: list[dict],
    price_histories: dict[str, list[float]],
) -> float:
    """
    Compute portfolio-level volatility from individual stock returns.

    Lower volatility → higher score.
    Uses simplified portfolio variance (ignores covariance for MVP).

    Scoring:
      - Annualized vol < 15% → score 90-100
      - Annualized vol 15-25% → score 60-90
      - Annualized vol 25-40% → score 30-60
      - Annualized vol > 40% → score 0-30
    """
    total_value = sum(h["current_value"] for h in holdings)
    if total_value == 0:
        return 50.0  # neutral default

    # Calculate portfolio-weighted daily returns
    portfolio_daily_returns = []
    max_days = 90

    for day in range(1, max_days):
        daily_return = 0.0
        for h in holdings:
            symbol = h["symbol"]
            weight = h["current_value"] / total_value

            if symbol in price_histories and len(price_histories[symbol]) > day:
                prices = price_histories[symbol]
                if prices[day - 1] > 0:
                    stock_return = (float(prices[day]) - float(prices[day - 1])) / float(
                        prices[day - 1]
                    )
                    daily_return += weight * stock_return

        portfolio_daily_returns.append(daily_return)

    if len(portfolio_daily_returns) < 2:
        return 50.0

    # Annualized volatility
    mean_return = sum(portfolio_daily_returns) / len(portfolio_daily_returns)
    variance = sum(
        (r - mean_return) ** 2 for r in portfolio_daily_returns
    ) / (len(portfolio_daily_returns) - 1)
    daily_vol = math.sqrt(variance)
    annualized_vol = daily_vol * math.sqrt(252) * 100  # as percentage

    # Map to score (lower vol = higher score)
    if annualized_vol <= 15:
        score = 90 + (15 - annualized_vol) * (10 / 15)
    elif annualized_vol <= 25:
        score = 60 + (25 - annualized_vol) * (30 / 10)
    elif annualized_vol <= 40:
        score = 30 + (40 - annualized_vol) * (30 / 15)
    else:
        score = max(0, 30 - (annualized_vol - 40) * 0.75)

    return round(min(100, max(0, score)), 2)


# ── Sub-score 3: Drawdown Risk ───────────────────────────────────────────────

def _calculate_drawdown_score(
    holdings: list[dict],
    price_histories: dict[str, list[float]],
) -> float:
    """
    Compute maximum drawdown from peak and convert to a score.

    Max drawdown < 5% → score 90-100
    Max drawdown 5-15% → score 60-90
    Max drawdown 15-30% → score 30-60
    Max drawdown > 30% → score 0-30
    """
    total_value = sum(h["current_value"] for h in holdings)
    if total_value == 0:
        return 50.0

    # Reconstruct portfolio value over time
    max_days = 90
    portfolio_values = []

    for day in range(max_days + 1):
        day_value = 0.0
        valid = True
        for h in holdings:
            symbol = h["symbol"]
            if symbol in price_histories and len(price_histories[symbol]) > day:
                # Scale quantity by historical price / current price ratio
                price_ratio = float(price_histories[symbol][day]) / float(
                    h["current_price"]
                ) if h["current_price"] > 0 else 1.0
                day_value += h["current_value"] * price_ratio
            else:
                valid = False
                break
        if valid:
            portfolio_values.append(day_value)

    if len(portfolio_values) < 2:
        return 50.0

    # Calculate max drawdown
    peak = portfolio_values[0]
    max_drawdown = 0.0
    for value in portfolio_values:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak if peak > 0 else 0
        max_drawdown = max(max_drawdown, drawdown)

    max_dd_pct = max_drawdown * 100

    # Map to score
    if max_dd_pct <= 5:
        score = 90 + (5 - max_dd_pct) * 2
    elif max_dd_pct <= 15:
        score = 60 + (15 - max_dd_pct) * 3
    elif max_dd_pct <= 30:
        score = 30 + (30 - max_dd_pct) * 2
    else:
        score = max(0, 30 - (max_dd_pct - 30) * 1)

    return round(min(100, max(0, score)), 2)


# ── Sub-score 4: Liquidity ───────────────────────────────────────────────────

def _calculate_liquidity_score(holdings: list[dict]) -> float:
    """
    Score based on percentage of portfolio in liquid large-cap stocks.

    Large-cap stocks are assumed to be highly liquid on NSE.
    > 80% in large cap → score 90-100
    60-80% → score 70-90
    40-60% → score 50-70
    < 40% → score 30-50
    """
    total_value = sum(h["current_value"] for h in holdings)
    if total_value == 0:
        return 50.0

    large_cap_value = sum(
        h["current_value"]
        for h in holdings
        if h.get("market_cap_category", "").upper() == "LARGE"
    )

    large_cap_pct = (large_cap_value / total_value) * 100

    # All our mock data is large-cap, so this will score high.
    # In production with mid/small-cap holdings, this becomes meaningful.
    if large_cap_pct >= 80:
        score = 90 + (large_cap_pct - 80) * 0.5
    elif large_cap_pct >= 60:
        score = 70 + (large_cap_pct - 60)
    elif large_cap_pct >= 40:
        score = 50 + (large_cap_pct - 40)
    else:
        score = 30 + large_cap_pct * 0.5

    return round(min(100, max(0, score)), 2)


# ── Sub-score 5: Rebalancing Need ────────────────────────────────────────────

def _calculate_rebalancing_score(holdings: list[dict]) -> float:
    """
    Measures how far the portfolio has drifted from a target allocation.

    For MVP, the target is naive equal-weight across all positions.
    In production, this would be user-configurable.

    Low drift → high score.
    """
    n = len(holdings)
    if n == 0:
        return 0.0

    total_value = sum(h["current_value"] for h in holdings)
    if total_value == 0:
        return 0.0

    target_weight = 1.0 / n

    # Sum of absolute deviations from target weight
    total_deviation = sum(
        abs((h["current_value"] / total_value) - target_weight)
        for h in holdings
    )

    # Max possible deviation = 2 * (1 - 1/n) ≈ 2 for large n
    max_deviation = 2 * (1 - target_weight)

    # Normalize to 0-100
    normalized_deviation = total_deviation / max_deviation if max_deviation > 0 else 0
    score = (1 - normalized_deviation) * 100

    return round(max(0, min(100, score)), 2)


# ── Main Entry Point ─────────────────────────────────────────────────────────

HEALTH_WEIGHTS = {
    "diversification": 0.25,
    "volatility": 0.20,
    "drawdown_risk": 0.20,
    "liquidity": 0.15,
    "rebalancing_need": 0.20,
}


def calculate_health_score(
    holdings: list[dict],
    price_histories: dict[str, list] | None = None,
) -> dict:
    """
    Calculate the composite portfolio health score.

    Args:
        holdings: List of dicts with keys:
            - symbol, current_value, current_price, sector,
              market_cap_category, average_price, quantity
        price_histories: Dict of symbol → list of historical prices.
            If None, volatility and drawdown use default scores.

    Returns:
        Dict with overall_score, grade, status, breakdown, recommendations.
    """
    if not holdings:
        return {
            "overall_score": Decimal("0"),
            "grade": "F",
            "status": "At Risk",
            "breakdown": {
                "diversification": Decimal("0"),
                "volatility": Decimal("0"),
                "drawdown_risk": Decimal("0"),
                "liquidity": Decimal("0"),
                "rebalancing_need": Decimal("0"),
            },
            "recommendations": ["Add holdings to your portfolio to get a health score."],
        }

    # Convert price histories to float for calculations
    float_histories: dict[str, list[float]] = {}
    if price_histories:
        for sym, prices in price_histories.items():
            float_histories[sym] = [float(p) for p in prices]

    # Calculate each sub-score
    div_score = _get_diversification_subscore(holdings)
    vol_score = _calculate_volatility_score(holdings, float_histories)
    dd_score = _calculate_drawdown_score(holdings, float_histories)
    liq_score = _calculate_liquidity_score(holdings)
    reb_score = _calculate_rebalancing_score(holdings)

    # Weighted composite
    overall = (
        div_score * HEALTH_WEIGHTS["diversification"]
        + vol_score * HEALTH_WEIGHTS["volatility"]
        + dd_score * HEALTH_WEIGHTS["drawdown_risk"]
        + liq_score * HEALTH_WEIGHTS["liquidity"]
        + reb_score * HEALTH_WEIGHTS["rebalancing_need"]
    )

    grade = _score_to_grade(overall)
    status = _score_to_status(overall)

    # ── Generate recommendations ──────────────────────────────────────────
    recommendations = []

    if vol_score < 50:
        recommendations.append(
            "Portfolio volatility is elevated. "
            "Consider adding low-beta, defensive stocks (FMCG, utilities)."
        )

    if dd_score < 50:
        recommendations.append(
            "Maximum drawdown risk is concerning. "
            "Review high-beta positions and consider stop-loss strategies."
        )

    if liq_score < 60:
        recommendations.append(
            "Significant portion of portfolio is in less liquid stocks. "
            "Ensure adequate large-cap allocation for easier exit during volatility."
        )

    if reb_score < 50:
        recommendations.append(
            "Portfolio has drifted significantly from balanced allocation. "
            "Consider rebalancing to manage concentration risk."
        )

    if div_score < 50:
        recommendations.append(
            "Diversification is weak. See diversification score for specific guidance."
        )

    if not recommendations:
        recommendations.append(
            "Portfolio health looks good. Continue monitoring for changes."
        )

    return {
        "overall_score": Decimal(str(round(overall, 2))),
        "grade": grade,
        "status": status,
        "breakdown": {
            "diversification": Decimal(str(div_score)),
            "volatility": Decimal(str(vol_score)),
            "drawdown_risk": Decimal(str(dd_score)),
            "liquidity": Decimal(str(liq_score)),
            "rebalancing_need": Decimal(str(reb_score)),
        },
        "recommendations": recommendations,
    }
