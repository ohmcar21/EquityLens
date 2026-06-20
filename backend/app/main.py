"""
FastAPI Application Entry Point.

Mounts all route modules, configures CORS, and sets up the API metadata.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes import portfolio, analytics, ai_reports

settings = get_settings()


# ── Lifespan (startup/shutdown) ───────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Startup: Log configuration, verify DB connection (future).
    Shutdown: Clean up connections (future).
    """
    print(f"🚀 Starting {settings.app_title} v{settings.app_version}")
    print(f"📊 Broker mode: {settings.broker_mode}")
    print(f"🗄️  Database: {settings.database_url.split('@')[-1] if '@' in settings.database_url else 'configured'}")
    yield
    print("👋 Shutting down...")


# ── FastAPI App ───────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description=(
        "AI-powered portfolio intelligence platform. "
        "Provides portfolio analytics, diversification scoring, "
        "and health scoring for Indian equity portfolios."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── CORS ──────────────────────────────────────────────────────────────────────
# Allow Next.js frontend (localhost:3000) to call the API.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Next.js dev server
        "http://127.0.0.1:3000",
        "http://localhost:5173",    # Vite dev server (if used)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Mount Routers ─────────────────────────────────────────────────────────────

app.include_router(portfolio.router)
app.include_router(analytics.router)
app.include_router(ai_reports.router)

# ── Root Health Check ─────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_title,
        "version": settings.app_version,
        "broker_mode": settings.broker_mode,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "configured",
        "broker_mode": settings.broker_mode,
        "environment": settings.app_env,
    }
