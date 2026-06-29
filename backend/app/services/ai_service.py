"""AI service helper: build compact analytics payload and produce LLM prompt.

This module reuses the existing AnalyticsService to fetch the combined
analytics snapshot, composes a compact payload containing only the fields
required by the LLM (health, diversification, sector_summary, top_holdings,
recommendations), and returns both the payload and the prompt produced by
`app.ai.prompt_templates.build_prompt`.

This file does NOT call any LLM or perform network operations.
"""
from typing import Any, Dict, List
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.services.analytics_service import AnalyticsService
from app.broker.mock_broker import MockBroker
from app.ai.prompt_templates import build_prompt
from app.ai.groq_client import generate_text as groq_generate_text, GroqClientError


def _to_primitive(value: Any) -> Any:
    """Recursively convert Decimal and other non-JSON primitives to JSON-safe values."""
    # Import here to avoid top-level dependency if not needed elsewhere
    from decimal import Decimal

    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (int, float, str, bool)):
        return value
    if isinstance(value, dict):
        return {k: _to_primitive(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_primitive(v) for v in value]
    # Fallback: try to cast to float, else stringify
    try:
        return float(value)
    except Exception:
        return str(value)


async def build_payload_and_prompt(db: AsyncSession) -> Dict[str, Any]:
    """Fetch analytics, build compact payload, and produce the prompt.

    Returns:
      { "payload": {...}, "prompt": "..." }
    """
    settings = get_settings()
    user_id = uuid.UUID(settings.demo_user_id)

    service = AnalyticsService(db, MockBroker())

    # Fetch combined analytics snapshot using existing service
    full = await service.get_full_summary(user_id)

    health = full.get("health", {})
    diversification = full.get("diversification", {})
    sector_allocation = full.get("sector_allocation", {})

    # Build compact sector_summary (top N sectors)
    sectors_raw = sector_allocation.get("sectors", [])
    sector_summary: List[Dict[str, Any]] = []
    for s in sectors_raw[:5]:
        sector_summary.append({
            "sector": s.get("sector"),
            "percentage": _to_primitive(s.get("percentage")),
            "holdings_count": _to_primitive(s.get("holdings_count")),
            "pnl_pct": _to_primitive(s.get("pnl_pct")),
        })

    # Build top_holdings: derive from portfolio_service holdings summary
    holdings_summary = await service.portfolio_service.get_holdings_summary(user_id)
    holdings = holdings_summary.get("holdings") or []

    analytics_holdings = service.portfolio_service.holdings_to_analytics_format(holdings)

    total_value = 0.0
    try:
        total_value = float(holdings_summary.get("total_current_value", 0) or 0)
    except Exception:
        # fallback compute
        total_value = sum(h.get("current_value", 0) for h in analytics_holdings)

    sorted_holdings = sorted(analytics_holdings, key=lambda h: h.get("current_value", 0), reverse=True)
    top_holdings: List[Dict[str, Any]] = []
    for h in sorted_holdings[:3]:
        current = _to_primitive(h.get("current_value")) or 0
        weight = None
        try:
            weight = round((float(current) / total_value) * 100, 2) if total_value and float(current) else None
        except Exception:
            weight = None

        top_holdings.append({
            "symbol": h.get("symbol"),
            "current_value": _to_primitive(h.get("current_value")),
            "weight_pct": weight,
        })

    # Recommendations: prefer analytics-provided recommendations (health first, then diversification)
    recommendations = []
    if health.get("recommendations"):
        recommendations = health.get("recommendations")
    elif diversification.get("recommendations"):
        recommendations = diversification.get("recommendations")

    payload = {
        "health": _to_primitive(health),
        "diversification": _to_primitive(diversification),
        "sector_summary": sector_summary,
        "top_holdings": top_holdings,
        "recommendations": _to_primitive(recommendations),
    }

    # Build prompt using shared prompt template builder
    prompt = build_prompt(payload)

    return {"payload": payload, "prompt": prompt}

async def generate_report(db: AsyncSession) -> Dict[str, Any]:
    """
    Generate an AI report using Groq
    """

    payload_and_prompt = await build_payload_and_prompt(db)

    payload = payload_and_prompt["payload"]
    prompt = payload_and_prompt["prompt"]

    result = await groq_generate_text(prompt)

    if not result.get("text"):
        raise GroqClientError("Groq returned empty text")

    return {
        "report": result["text"],
        "payload": payload,
        "meta": {
            "model": result["model"],
            "prompt_chars": result["prompt_chars"],
        },
    }