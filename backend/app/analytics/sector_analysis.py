"""
Sector Allocation Analysis — Pure computation module.

Aggregates holdings by sector and produces allocation breakdowns,
including per-sector P&L and concentration identification.
"""

from decimal import Decimal, ROUND_HALF_UP


def calculate_sector_allocation(holdings: list[dict]) -> dict:
    """
    Calculate sector-level allocation breakdown.

    Args:
        holdings: List of dicts with keys:
            - current_value, invested_value, sector

    Returns:
        Dict with sectors list, most_concentrated, least_concentrated.
    """
    if not holdings:
        return {
            "sectors": [],
            "most_concentrated": "N/A",
            "least_concentrated": "N/A",
        }

    total_value = sum(h["current_value"] for h in holdings)

    # Aggregate by sector
    sector_data: dict[str, dict] = {}
    for h in holdings:
        sector = h.get("sector", "Unknown")
        if sector not in sector_data:
            sector_data[sector] = {
                "value": 0.0,
                "invested": 0.0,
                "count": 0,
            }
        sector_data[sector]["value"] += h["current_value"]
        sector_data[sector]["invested"] += h["invested_value"]
        sector_data[sector]["count"] += 1

    # Build response
    sectors = []
    for sector_name, data in sorted(
        sector_data.items(), key=lambda x: x[1]["value"], reverse=True
    ):
        pnl = data["value"] - data["invested"]
        pnl_pct = (pnl / data["invested"] * 100) if data["invested"] > 0 else 0

        sectors.append({
            "sector": sector_name,
            "value": Decimal(str(round(data["value"], 2))),
            "percentage": Decimal(str(round(data["value"] / total_value * 100, 2))) if total_value > 0 else Decimal("0"),
            "holdings_count": data["count"],
            "pnl": Decimal(str(round(pnl, 2))),
            "pnl_pct": Decimal(str(round(pnl_pct, 2))),
        })

    most = sectors[0]["sector"] if sectors else "N/A"
    least = sectors[-1]["sector"] if sectors else "N/A"

    return {
        "sectors": sectors,
        "most_concentrated": most,
        "least_concentrated": least,
    }
