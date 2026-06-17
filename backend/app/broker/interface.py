"""
Broker Interface — Abstract base class (Strategy Pattern).

This defines the contract that ALL broker implementations must follow.
The service layer depends on this interface, never on a concrete broker.

When Zerodha credentials become available:
  1. Implement ZerodhaBroker(BrokerInterface)
  2. Change BROKER_MODE=zerodha in .env
  3. Zero changes needed in services, routes, or analytics.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class BrokerHolding:
    """
    Normalized holding data from any broker.

    This is the canonical data structure that flows through the system.
    Each broker implementation maps its native response format into this.
    """
    symbol: str
    exchange: str
    quantity: int
    average_price: Decimal
    current_price: Decimal
    sector: str
    market_cap_category: str    # "LARGE", "MID", "SMALL"
    day_change_pct: Decimal
    isin: str = ""              # International Securities ID (future use)


@dataclass
class BrokerQuote:
    """Normalized price quote from any broker."""
    symbol: str
    last_price: Decimal
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: int
    day_change_pct: Decimal


class BrokerInterface(ABC):
    """
    Abstract interface for broker integrations.

    Any broker (Zerodha, Groww, Upstox, etc.) must implement these methods.
    """

    @abstractmethod
    async def get_holdings(self) -> list[BrokerHolding]:
        """Fetch all current holdings from the broker."""
        ...

    @abstractmethod
    async def get_quote(self, symbol: str) -> BrokerQuote:
        """Fetch a real-time quote for a single symbol."""
        ...

    @abstractmethod
    async def get_bulk_quotes(self, symbols: list[str]) -> list[BrokerQuote]:
        """Fetch real-time quotes for multiple symbols."""
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """Check if the broker connection is active."""
        ...
