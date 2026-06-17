"""
Application configuration using Pydantic Settings.

Reads from environment variables / .env file. The BROKER_MODE flag controls
whether the app uses MockBroker or ZerodhaBroker — this is the single switch
you flip when real credentials become available.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio_intel"

    # ── Application ───────────────────────────────────────────────────────
    app_env: str = "development"
    debug: bool = True
    app_title: str = "Portfolio Intelligence API"
    app_version: str = "0.1.0"

    # ── Broker ────────────────────────────────────────────────────────────
    broker_mode: str = "mock"  # "mock" or "zerodha"
    kite_api_key: str = ""
    kite_api_secret: str = ""
    kite_access_token: str = ""

    # ── Demo User ─────────────────────────────────────────────────────────
    # Fixed UUID for the demo user seeded in schema.sql
    demo_user_id: str = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance — created once, reused everywhere."""
    return Settings()
