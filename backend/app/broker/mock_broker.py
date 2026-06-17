"""
MockBroker — Implements BrokerInterface using fake data.

This is the active broker during development. When Zerodha credentials
arrive, the app switches to ZerodhaBroker by changing BROKER_MODE in .env.

The mock data is intentionally imperfect (overweight IT, some losses)
so that analytics produce interesting, realistic results.
"""

from decimal import Decimal

from app.broker.interface import BrokerInterface, BrokerHolding, BrokerQuote
from app.mock_data.portfolio_data import MOCK_STOCKS, MOCK_HOLDINGS


class MockBroker(BrokerInterface):
    """Broker implementation backed by static mock data."""

    async def get_holdings(self) -> list[BrokerHolding]:
        """
        Return mock holdings as BrokerHolding dataclass instances.

        Maps the raw mock data dicts into the canonical BrokerHolding format
        by enriching with stock metadata (sector, market cap, ISIN).
        """
        holdings = []
        for h in MOCK_HOLDINGS:
            stock_info = MOCK_STOCKS[h["symbol"]]
            holdings.append(
                BrokerHolding(
                    symbol=h["symbol"],
                    exchange=stock_info["exchange"],
                    quantity=h["quantity"],
                    average_price=h["average_price"],
                    current_price=h["current_price"],
                    sector=stock_info["sector"],
                    market_cap_category=stock_info["market_cap_category"],
                    day_change_pct=h["day_change_pct"],
                    isin=stock_info["isin"],
                )
            )
        return holdings

    async def get_quote(self, symbol: str) -> BrokerQuote:
        """Return a mock quote for a single symbol."""
        # Find the holding data for this symbol
        holding_data = next(
            (h for h in MOCK_HOLDINGS if h["symbol"] == symbol), None
        )

        if holding_data is None:
            raise ValueError(f"Symbol '{symbol}' not found in mock data")

        price = holding_data["current_price"]
        return BrokerQuote(
            symbol=symbol,
            last_price=price,
            open_price=price * Decimal("0.995"),
            high_price=price * Decimal("1.012"),
            low_price=price * Decimal("0.988"),
            close_price=price,
            volume=1_250_000,
            day_change_pct=holding_data["day_change_pct"],
        )

    async def get_bulk_quotes(self, symbols: list[str]) -> list[BrokerQuote]:
        """Return mock quotes for multiple symbols."""
        quotes = []
        for symbol in symbols:
            try:
                quote = await self.get_quote(symbol)
                quotes.append(quote)
            except ValueError:
                continue  # Skip unknown symbols
        return quotes

    async def is_connected(self) -> bool:
        """Mock broker is always 'connected'."""
        return True
