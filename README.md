# AI Portfolio Intelligence Platform — Backend (Week 1 MVP)

This is the backend for the AI Portfolio Intelligence Platform, built using **FastAPI**, **SQLAlchemy (Async)**, and **PostgreSQL**.

The architecture uses the **Strategy Pattern** to abstract broker integrations, allowing the platform to run completely off realistic mock data (15 Indian stocks across 6 sectors) without requiring active Zerodha Kite Connect credentials.

---

## Technical Stack
- **Framework**: FastAPI (Asynchronous)
- **Database ORM**: SQLAlchemy 2.0 (Async) + asyncpg
- **Database**: PostgreSQL 15+
- **Settings Management**: Pydantic Settings v2

---

## Getting Started

### 1. Prerequisites
- Python 3.10 or higher installed
- PostgreSQL database running locally

### 2. Setup Environment
1. Copy the example environment file:
   ```bash
   cp backend/.env.example backend/.env
   ```
2. Modify `backend/.env` with your database credentials. For example:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio_intel
   BROKER_MODE=mock
   ```

### 3. Database Schema Setup
Initialize the database using the schema DDL script. Run the SQL script located at:
- [database/schema.sql](file:///c:/Users/ohmcar/Desktop/project%20w%20aneesh/Banking/database/schema.sql)

This script:
1. Creates the `users`, `holdings`, and `portfolio_scores` tables.
2. Seeds a demo user with UUID `a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11`.

### 4. Installation
Install python dependencies in your environment:
```bash
pip install -r backend/requirements.txt
```

### 5. Running the API Server
Start the development server using uvicorn:
```bash
cd backend
uvicorn app.main:app --reload
```

The API docs will be available at:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Core Analytics Features

### 1. Diversification Score (0–100)
Calculated as a weighted average of four dimensions:
- **Sector Spread (30%)**: Normalized Shannon Entropy showing how evenly distributed holdings are across sectors.
- **Stock Concentration (30%)**: Inverse Herfindahl-Hirschman Index (HHI) reflecting single-stock concentration risk.
- **Market Cap Mix (20%)**: Balance against ideal allocations of Large (60%), Mid (27.5%), and Small cap (12.5%).
- **Correlation Risk (20%)**: Inter-sector correlation penalty based on domain-mapped sector relationships.

### 2. Portfolio Health Score (0–100)
Composite score summarizing overall portfolio robustness:
- **Diversification (25%)**: Incorporates the Diversification Score.
- **Volatility (20%)**: Annualized portfolio volatility based on historical returns (90-day mock returns).
- **Drawdown Risk (20%)**: Maximum portfolio-level drawdown simulated over the past 90 days.
- **Liquidity (15%)**: Weight in large-cap NSE liquid stocks.
- **Rebalancing Need (20%)**: Degree of drift from an equal-weighted target allocation.
