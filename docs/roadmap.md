# Implementation Roadmap — Week 1 MVP

This roadmap details the day-by-day implementation tasks to set up, build, and verify the backend MVP for the AI Portfolio Intelligence Platform.

---

## Day 1: Project Setup & Database Initialization
- [x] Configure workspace directories.
- [x] Write `database/schema.sql` defining database tables: `users`, `holdings`, and `portfolio_scores`.
- [x] Setup `backend/requirements.txt` with FastAPI, SQLAlchemy, asyncpg, and other dependencies.
- [x] Create `.env.example` configurations.
- [x] Initialize database schema in local PostgreSQL instance.

## Day 2: Core Architecture & Data Models
- [x] Implement centralized configuration with `app/config.py`.
- [x] Create async connection engine and session dependency in `app/database.py`.
- [x] Write SQLAlchemy models mapping PostgreSQL tables:
  - `User` in `app/models/user.py`
  - `Holding` in `app/models/holding.py`
  - `PortfolioScore` in `app/models/portfolio_score.py`
- [x] Implement corresponding Pydantic request/response validation schemas.

## Day 3: Broker Abstraction & Mock Data Layer
- [x] Define abstract `BrokerInterface` in `app/broker/interface.py` to decouple from broker specifics.
- [x] Establish realistic mock data structures containing 15 Indian equities in `app/mock_data/portfolio_data.py`.
- [x] Write geometric Brownian motion price history generator for synthetic stock returns.
- [x] Implement concrete `MockBroker` complying with the `BrokerInterface`.

## Day 4: Core Analytics Engine
- [x] Create `app/analytics/diversification.py` implementing the 4-dimension scoring system:
  - Sector spread (Shannon entropy)
  - Stock concentration (HHI)
  - Market cap mix
  - Sector correlation penalty
- [x] Create `app/analytics/health_score.py` implementing the 5-subscore composite:
  - Diversification, Volatility, Drawdown risk, Liquidity, and Rebalancing drift.
- [x] Create `app/analytics/sector_analysis.py` for aggregating allocations.

## Day 5: Service Orchestration & API Routing
- [x] Implement `PortfolioService` to manage holdings retrieval and broker sync orchestration.
- [x] Implement `AnalyticsService` to perform portfolio-level computations and cache scores.
- [x] Mount FastAPI routes for portfolio holdings and sync (`/api/v1/portfolio/*`).
- [x] Mount FastAPI routes for analytics calculations (`/api/v1/analytics/*`).
- [x] Configure CORS policies and add healthcheck endpoints in `app/main.py`.

---

## Verification Checklist

To confirm the Week 1 MVP is fully operational, run the following verification steps:

1. **Schema Check**:
   Apply `database/schema.sql` to your PostgreSQL database. Ensure the `users`, `holdings`, and `portfolio_scores` tables are created, and the demo user row is present.

2. **Server Launch**:
   Run `uvicorn app.main:app --reload` from the `backend/` directory. Ensure the server starts with message `🚀 Starting Portfolio Intelligence API`.

3. **API Explorer**:
   Navigate to `http://localhost:8000/docs`. Verify the Swagger UI is fully rendered with sections for `Portfolio`, `Analytics`, and `Health`.

4. **Sync Execution**:
   Call `/api/v1/portfolio/sync` via POST. Ensure it populates the local database with the mock holdings data and returns a list of holdings.

5. **Analytics Calculation**:
   Call `/api/v1/analytics/summary` via GET. Verify that the response returns the diversification score breakdown, health score breakdown, and sector allocations, and saves the snapshot scores to the database.
