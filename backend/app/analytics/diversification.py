"""
Diversification Score Engine — Pure computation module.

Computes a 0–100 diversification score from 4 weighted dimensions:
  1. Sector Spread (30%) — Shannon entropy of sector allocation
  2. Stock Concentration (30%) — Inverse Herfindahl-Hirschman Index
  3. Market Cap Mix (20%) — Balance across large/mid/small cap
  4. Correlation Risk (20%) — Penalty for correlated sector exposure

Design decisions:
  - All functions are pure (no DB, no side effects) → easy to test.
  - Takes a list of dicts as input, not ORM models → works with any data source.
  - Letter grades map to score ranges for human-readable output.
"""

import math
from decimal import Decimal, ROUND_HALF_UP


# ── Grade Boundaries ──────────────────────────────────────────────────────────

def _score_to_grade(score: float) -> str:
    """Map a 0–100 score to a letter grade."""
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


# ── Dimension 1: Sector Spread (Shannon Entropy) ─────────────────────────────

def _calculate_sector_spread(holdings: list[dict]) -> float:
    """
    Measures how evenly the portfolio is distributed across sectors.

    Uses normalized Shannon entropy:
      H = -Σ(p_i * ln(p_i)) / ln(n)

    where p_i = sector weight, n = number of sectors.
    Score 100 = perfectly even distribution across all sectors.
    Score 0 = entire portfolio in one sector.
    """
    total_value = sum(h["current_value"] for h in holdings)
    if total_value == 0:
        return 0.0

    # Aggregate by sector
    sector_values: dict[str, float] = {}
    for h in holdings:
        sector = h.get("sector", "Unknown")
        sector_values[sector] = sector_values.get(sector, 0.0) + h["current_value"]

    n_sectors = len(sector_values)
    if n_sectors <= 1:
        return 0.0

    # Compute Shannon entropy
    entropy = 0.0
    for value in sector_values.values():
        p = value / total_value
        if p > 0:
            entropy -= p * math.log(p)

    # Normalize: max entropy = ln(n)
    max_entropy = math.log(n_sectors)
    normalized = (entropy / max_entropy) * 100 if max_entropy > 0 else 0

    return round(normalized, 2)


# ── Dimension 2: Stock Concentration (Inverse HHI) ───────────────────────────

def _calculate_stock_concentration(holdings: list[dict]) -> float:
    """
    Measures how concentrated the portfolio is in individual positions.

    Uses the Herfindahl-Hirschman Index (HHI):
      HHI = Σ(s_i²)   where s_i = market share of stock i

    HHI ranges from 1/n (perfectly equal) to 1 (single stock).
    We invert it: score 100 = perfectly equal, score 0 = one stock.
    """
    total_value = sum(h["current_value"] for h in holdings)
    if total_value == 0 or len(holdings) == 0:
        return 0.0

    n = len(holdings)

    # Compute HHI
    hhi = sum((h["current_value"] / total_value) ** 2 for h in holdings)

    # Normalize HHI to 0-100 score
    # Min HHI = 1/n (equal weights), Max HHI = 1 (single stock)
    min_hhi = 1.0 / n
    if min_hhi >= 1.0:
        return 100.0  # Single stock edge case

    # Score: 100 when HHI = min_hhi, 0 when HHI = 1
    score = (1 - hhi) / (1 - min_hhi) * 100

    return round(max(0, min(100, score)), 2)


# ── Dimension 3: Market Cap Mix ───────────────────────────────────────────────

def _calculate_market_cap_mix(holdings: list[dict]) -> float:
    """
    Measures balance across market cap categories.

    Ideal allocation (opinionated but reasonable):
      Large cap: 50-70% → stable core
      Mid cap:   20-35% → growth potential
      Small cap: 5-15%  → high growth / high risk

    Score is based on how close the actual allocation is to the ideal.
    All-large-cap portfolio scores ~60 (okay but not diversified by cap).
    """
    total_value = sum(h["current_value"] for h in holdings)
    if total_value == 0:
        return 0.0

    # Aggregate by market cap
    cap_values = {"LARGE": 0.0, "MID": 0.0, "SMALL": 0.0}
    for h in holdings:
        cap = h.get("market_cap_category", "LARGE").upper()
        if cap not in cap_values:
            cap = "LARGE"
        cap_values[cap] += h["current_value"]

    # Compute percentages
    cap_pcts = {k: (v / total_value) * 100 for k, v in cap_values.items()}

    # Ideal ranges (midpoints)
    ideal = {"LARGE": 60.0, "MID": 27.5, "SMALL": 12.5}

    # Score: penalize deviation from ideal
    total_deviation = sum(
        abs(cap_pcts[cap] - ideal[cap]) for cap in ideal
    )

    # Max possible deviation is ~175 (all in one cap, 0 in others)
    # Normalize so 0 deviation = 100 score
    score = max(0, 100 - (total_deviation * 0.8))

    return round(score, 2)


# ── Dimension 4: Correlation Risk ─────────────────────────────────────────────

# Simplified sector correlation matrix.
# In production, compute from actual returns. For MVP, use domain knowledge.
SECTOR_CORRELATIONS = {
    ("Information Technology", "Information Technology"): 1.0,
    ("Information Technology", "Banking & Finance"): 0.45,
    ("Information Technology", "Pharmaceuticals"): 0.20,
    ("Information Technology", "FMCG"): 0.15,
    ("Information Technology", "Automobile"): 0.35,
    ("Information Technology", "Energy & Petrochemicals"): 0.30,
    ("Banking & Finance", "Banking & Finance"): 1.0,
    ("Banking & Finance", "Pharmaceuticals"): 0.25,
    ("Banking & Finance", "FMCG"): 0.30,
    ("Banking & Finance", "Automobile"): 0.40,
    ("Banking & Finance", "Energy & Petrochemicals"): 0.50,
    ("Pharmaceuticals", "Pharmaceuticals"): 1.0,
    ("Pharmaceuticals", "FMCG"): 0.35,
    ("Pharmaceuticals", "Automobile"): 0.15,
    ("Pharmaceuticals", "Energy & Petrochemicals"): 0.20,
    ("FMCG", "FMCG"): 1.0,
    ("FMCG", "Automobile"): 0.25,
    ("FMCG", "Energy & Petrochemicals"): 0.20,
    ("Automobile", "Automobile"): 1.0,
    ("Automobile", "Energy & Petrochemicals"): 0.55,
    ("Energy & Petrochemicals", "Energy & Petrochemicals"): 1.0,
}


def _get_sector_correlation(sector_a: str, sector_b: str) -> float:
    """Look up pairwise sector correlation (symmetric)."""
    key = (sector_a, sector_b)
    if key in SECTOR_CORRELATIONS:
        return SECTOR_CORRELATIONS[key]
    key_reversed = (sector_b, sector_a)
    if key_reversed in SECTOR_CORRELATIONS:
        return SECTOR_CORRELATIONS[key_reversed]
    return 0.3  # default moderate correlation for unknown pairs


def _calculate_correlation_risk(holdings: list[dict]) -> float:
    """
    Penalizes portfolios where large sectors are highly correlated.

    Computes weighted average pairwise correlation across sectors.
    Score 100 = all sectors uncorrelated (impossible, but ideal).
    Score 0 = all capital in perfectly correlated sectors.
    """
    total_value = sum(h["current_value"] for h in holdings)
    if total_value == 0:
        return 0.0

    # Aggregate weights by sector
    sector_weights: dict[str, float] = {}
    for h in holdings:
        sector = h.get("sector", "Unknown")
        sector_weights[sector] = sector_weights.get(sector, 0.0) + (
            h["current_value"] / total_value
        )

    sectors = list(sector_weights.keys())
    if len(sectors) <= 1:
        return 0.0

    # Weighted average correlation
    weighted_corr = 0.0
    total_weight = 0.0
    for i, s1 in enumerate(sectors):
        for j, s2 in enumerate(sectors):
            if i >= j:
                continue  # skip diagonal and lower triangle
            w = sector_weights[s1] * sector_weights[s2]
            corr = _get_sector_correlation(s1, s2)
            weighted_corr += w * corr
            total_weight += w

    avg_corr = weighted_corr / total_weight if total_weight > 0 else 0.5

    # Convert: 0 correlation → 100 score, 1 correlation → 0 score
    score = (1 - avg_corr) * 100

    return round(max(0, min(100, score)), 2)


# ── Main Entry Point ─────────────────────────────────────────────────────────

WEIGHTS = {
    "sector_spread": 0.30,
    "stock_concentration": 0.30,
    "market_cap_mix": 0.20,
    "correlation_risk": 0.20,
}


def calculate_diversification_score(holdings: list[dict]) -> dict:
    """
    Calculate the composite diversification score.

    Args:
        holdings: List of dicts, each with keys:
            - current_value (float): current market value of position
            - sector (str): sector name
            - market_cap_category (str): "LARGE", "MID", or "SMALL"

    Returns:
        Dict with overall_score, grade, breakdown, and recommendations.
    """
    if not holdings:
        return {
            "overall_score": Decimal("0"),
            "grade": "F",
            "breakdown": {
                "sector_spread": Decimal("0"),
                "stock_concentration": Decimal("0"),
                "market_cap_mix": Decimal("0"),
                "correlation_risk": Decimal("0"),
            },
            "recommendations": ["Add holdings to your portfolio to get a diversification score."],
        }

    # Calculate each dimension
    sector_spread = _calculate_sector_spread(holdings)
    stock_concentration = _calculate_stock_concentration(holdings)
    market_cap_mix = _calculate_market_cap_mix(holdings)
    correlation_risk = _calculate_correlation_risk(holdings)

    # Weighted composite
    overall = (
        sector_spread * WEIGHTS["sector_spread"]
        + stock_concentration * WEIGHTS["stock_concentration"]
        + market_cap_mix * WEIGHTS["market_cap_mix"]
        + correlation_risk * WEIGHTS["correlation_risk"]
    )

    grade = _score_to_grade(overall)

    # ── Generate recommendations ──────────────────────────────────────────
    recommendations = []

    if sector_spread < 60:
        # Find the dominant sector
        total_value = sum(h["current_value"] for h in holdings)
        sector_totals: dict[str, float] = {}
        for h in holdings:
            s = h.get("sector", "Unknown")
            sector_totals[s] = sector_totals.get(s, 0.0) + h["current_value"]
        top_sector = max(sector_totals, key=sector_totals.get)
        top_pct = round(sector_totals[top_sector] / total_value * 100, 1)
        recommendations.append(
            f"Portfolio is overweight in {top_sector} ({top_pct}%). "
            f"Consider diversifying into underrepresented sectors."
        )

    if stock_concentration < 60:
        recommendations.append(
            "Some positions are disproportionately large. "
            "Consider rebalancing to reduce single-stock risk."
        )

    if market_cap_mix < 50:
        recommendations.append(
            "Portfolio lacks market cap diversity. "
            "Consider adding mid-cap or small-cap stocks for growth potential."
        )

    if correlation_risk < 50:
        recommendations.append(
            "Sectors in your portfolio are highly correlated. "
            "Consider adding defensive sectors (pharma, FMCG) to reduce correlation risk."
        )

    if not recommendations:
        recommendations.append("Portfolio diversification looks healthy. Keep monitoring.")

    return {
        "overall_score": Decimal(str(round(overall, 2))),
        "grade": grade,
        "breakdown": {
            "sector_spread": Decimal(str(sector_spread)),
            "stock_concentration": Decimal(str(stock_concentration)),
            "market_cap_mix": Decimal(str(market_cap_mix)),
            "correlation_risk": Decimal(str(correlation_risk)),
        },
        "recommendations": recommendations,
    }
