"""
Mock Portfolio Data — 15 realistic Indian stocks across 6 sectors.

All prices, quantities, and P&L figures are realistic but fictional.
This data is designed to produce interesting analytics results:
  - Intentionally overweight in IT (to trigger diversification warnings)
  - Mix of large/mid cap (to test market cap scoring)
  - Varied P&L (some winners, some losers, for realistic analytics)

When Zerodha integration is live, this file becomes unused — the
MockBroker simply won't be instantiated.
"""

from decimal import Decimal


# ── Stock Master Data ─────────────────────────────────────────────────────────

MOCK_STOCKS = {
    # ── Information Technology (intentionally overweight) ──────────────────
    "TCS": {
        "name": "Tata Consultancy Services",
        "sector": "Information Technology",
        "market_cap_category": "LARGE",
        "exchange": "NSE",
        "isin": "INE467B01029",
    },
    "INFY": {
        "name": "Infosys Limited",
        "sector": "Information Technology",
        "market_cap_category": "LARGE",
        "exchange": "NSE",
        "isin": "INE009A01021",
    },
    "WIPRO": {
        "name": "Wipro Limited",
        "sector": "Information Technology",
        "market_cap_category": "LARGE",
        "exchange": "NSE",
        "isin": "INE075A01022",
    },

    # ── Banking ───────────────────────────────────────────────────────────
    "HDFCBANK": {
        "name": "HDFC Bank Limited",
        "sector": "Banking & Finance",
        "market_cap_category": "LARGE",
        "exchange": "NSE",
        "isin": "INE040A01034",
    },
    "ICICIBANK": {
        "name": "ICICI Bank Limited",
        "sector": "Banking & Finance",
        "market_cap_category": "LARGE",
        "exchange": "NSE",
        "isin": "INE090A01021",
    },
    "KOTAKBANK": {
        "name": "Kotak Mahindra Bank",
        "sector": "Banking & Finance",
        "market_cap_category": "LARGE",
        "exchange": "NSE",
        "isin": "INE237A01028",
    },

    # ── Pharmaceuticals ───────────────────────────────────────────────────
    "SUNPHARMA": {
        "name": "Sun Pharmaceutical Industries",
        "sector": "Pharmaceuticals",
        "market_cap_category": "LARGE",
        "exchange": "NSE",
        "isin": "INE044A01036",
    },
    "DRREDDY": {
        "name": "Dr. Reddy's Laboratories",
        "sector": "Pharmaceuticals",
        "market_cap_category": "LARGE",
        "exchange": "NSE",
        "isin": "INE089A01023",
    },
    "CIPLA": {
        "name": "Cipla Limited",
        "sector": "Pharmaceuticals",
        "market_cap_category": "LARGE",
        "exchange": "NSE",
        "isin": "INE059A01026",
    },

    # ── FMCG ──────────────────────────────────────────────────────────────
    "HINDUNILVR": {
        "name": "Hindustan Unilever Limited",
        "sector": "FMCG",
        "market_cap_category": "LARGE",
        "exchange": "NSE",
        "isin": "INE030A01027",
    },
    "ITC": {
        "name": "ITC Limited",
        "sector": "FMCG",
        "market_cap_category": "LARGE",
        "exchange": "NSE",
        "isin": "INE154A01025",
    },
    "NESTLEIND": {
        "name": "Nestlé India Limited",
        "sector": "FMCG",
        "market_cap_category": "LARGE",
        "exchange": "NSE",
        "isin": "INE239A01016",
    },

    # ── Automobile ────────────────────────────────────────────────────────
    "MARUTI": {
        "name": "Maruti Suzuki India",
        "sector": "Automobile",
        "market_cap_category": "LARGE",
        "exchange": "NSE",
        "isin": "INE585B01010",
    },
    "TATAMOTORS": {
        "name": "Tata Motors Limited",
        "sector": "Automobile",
        "market_cap_category": "LARGE",
        "exchange": "NSE",
        "isin": "INE155A01022",
    },

    # ── Energy ────────────────────────────────────────────────────────────
    "RELIANCE": {
        "name": "Reliance Industries Limited",
        "sector": "Energy & Petrochemicals",
        "market_cap_category": "LARGE",
        "exchange": "NSE",
        "isin": "INE002A01018",
    },
}


# ── Mock Holdings (Demo User's Portfolio) ─────────────────────────────────────
# Designed to be intentionally imperfect for interesting analytics:
#   - IT is ~35% of portfolio (overweight → lower diversification)
#   - Banking is ~25% (second largest)
#   - Some stocks have losses (realistic P&L mix)

MOCK_HOLDINGS = [
    # ── IT (overweight: ~35% of portfolio) ────────────────────────────────
    {
        "symbol": "TCS",
        "quantity": 25,
        "average_price": Decimal("3450.00"),
        "current_price": Decimal("3892.50"),
        "day_change_pct": Decimal("1.24"),
    },
    {
        "symbol": "INFY",
        "quantity": 40,
        "average_price": Decimal("1520.00"),
        "current_price": Decimal("1678.35"),
        "day_change_pct": Decimal("0.87"),
    },
    {
        "symbol": "WIPRO",
        "quantity": 60,
        "average_price": Decimal("485.00"),
        "current_price": Decimal("452.10"),   # loss position
        "day_change_pct": Decimal("-0.45"),
    },

    # ── Banking (~25%) ────────────────────────────────────────────────────
    {
        "symbol": "HDFCBANK",
        "quantity": 30,
        "average_price": Decimal("1580.00"),
        "current_price": Decimal("1725.60"),
        "day_change_pct": Decimal("0.62"),
    },
    {
        "symbol": "ICICIBANK",
        "quantity": 45,
        "average_price": Decimal("940.00"),
        "current_price": Decimal("1085.20"),
        "day_change_pct": Decimal("1.15"),
    },
    {
        "symbol": "KOTAKBANK",
        "quantity": 20,
        "average_price": Decimal("1780.00"),
        "current_price": Decimal("1695.40"),   # loss position
        "day_change_pct": Decimal("-0.38"),
    },

    # ── Pharma (~12%) ─────────────────────────────────────────────────────
    {
        "symbol": "SUNPHARMA",
        "quantity": 35,
        "average_price": Decimal("1120.00"),
        "current_price": Decimal("1245.80"),
        "day_change_pct": Decimal("0.93"),
    },
    {
        "symbol": "DRREDDY",
        "quantity": 10,
        "average_price": Decimal("5480.00"),
        "current_price": Decimal("5320.15"),   # slight loss
        "day_change_pct": Decimal("-0.22"),
    },

    # ── FMCG (~13%) ──────────────────────────────────────────────────────
    {
        "symbol": "HINDUNILVR",
        "quantity": 15,
        "average_price": Decimal("2650.00"),
        "current_price": Decimal("2542.30"),   # loss position
        "day_change_pct": Decimal("-0.71"),
    },
    {
        "symbol": "ITC",
        "quantity": 100,
        "average_price": Decimal("410.00"),
        "current_price": Decimal("468.75"),
        "day_change_pct": Decimal("1.52"),
    },

    # ── Auto (~8%) ────────────────────────────────────────────────────────
    {
        "symbol": "MARUTI",
        "quantity": 5,
        "average_price": Decimal("10200.00"),
        "current_price": Decimal("11450.00"),
        "day_change_pct": Decimal("0.34"),
    },
    {
        "symbol": "TATAMOTORS",
        "quantity": 50,
        "average_price": Decimal("620.00"),
        "current_price": Decimal("745.30"),
        "day_change_pct": Decimal("2.18"),
    },

    # ── Energy (~7%) ──────────────────────────────────────────────────────
    {
        "symbol": "RELIANCE",
        "quantity": 15,
        "average_price": Decimal("2380.00"),
        "current_price": Decimal("2565.90"),
        "day_change_pct": Decimal("0.56"),
    },
]


# ── Mock Price History (90 days, for risk metrics) ────────────────────────────
# Simplified: daily returns as percentages for volatility calculation.
# In production, this would come from a market data provider.

import random
import math

random.seed(42)  # Reproducible randomness


def generate_mock_price_history(
    current_price: Decimal,
    days: int = 90,
    volatility: float = 0.02,
) -> list[Decimal]:
    """
    Generate a synthetic price history using geometric Brownian motion.

    Args:
        current_price: The current price (last element of the returned list).
        days: Number of historical days to generate.
        volatility: Daily volatility (std dev of daily returns).

    Returns:
        List of daily closing prices, oldest first, current price last.
    """
    prices = []
    price = float(current_price)

    # Generate forward from an estimated starting point, then reverse
    # so the last price matches current_price.
    daily_returns = [
        random.gauss(0.0003, volatility) for _ in range(days)
    ]

    # Work backwards from current price
    backward_prices = [price]
    for ret in reversed(daily_returns):
        price = price / math.exp(ret)
        backward_prices.append(price)

    backward_prices.reverse()
    return [Decimal(str(round(p, 2))) for p in backward_prices]


# Pre-generate price histories for all holdings
MOCK_PRICE_HISTORIES: dict[str, list[Decimal]] = {}
for holding in MOCK_HOLDINGS:
    symbol = holding["symbol"]
    # Different sectors have different volatility profiles
    stock_info = MOCK_STOCKS[symbol]
    sector_volatility = {
        "Information Technology": 0.018,
        "Banking & Finance": 0.020,
        "Pharmaceuticals": 0.022,
        "FMCG": 0.012,
        "Automobile": 0.025,
        "Energy & Petrochemicals": 0.019,
    }
    vol = sector_volatility.get(stock_info["sector"], 0.02)
    MOCK_PRICE_HISTORIES[symbol] = generate_mock_price_history(
        holding["current_price"], days=90, volatility=vol
    )
