-- ============================================================================
-- AI Portfolio Intelligence Platform — PostgreSQL Schema (Week 1 MVP)
-- ============================================================================
-- Tables: users, holdings, portfolio_scores
-- Auth, transactions, and market_data_snapshots are deferred to later phases.
-- ============================================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USERS
-- ============================================================================
-- Minimal user table. Auth fields (password_hash, etc.) will be added later.
-- For now, this just gives us a user_id to associate holdings with.
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- HOLDINGS
-- ============================================================================
-- Represents current stock positions in a user's portfolio.
-- Each row = one stock position for one user.
--
-- Design decisions:
--   • average_price + current_price stored together so P&L can be computed
--     without joining to a separate market_data table.
--   • sector + market_cap_category are denormalized onto the holding for
--     fast analytics queries (no joins to a stocks master table).
--   • exchange is stored for future multi-exchange support (NSE/BSE).
-- ============================================================================
CREATE TABLE IF NOT EXISTS holdings (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol              VARCHAR(50) NOT NULL,       -- e.g., "RELIANCE", "TCS"
    exchange            VARCHAR(10) DEFAULT 'NSE',  -- NSE or BSE
    quantity            INTEGER NOT NULL CHECK (quantity > 0),
    average_price       DECIMAL(12, 2) NOT NULL,    -- weighted avg buy price
    current_price       DECIMAL(12, 2) NOT NULL,    -- latest market price
    sector              VARCHAR(100),               -- e.g., "Information Technology"
    market_cap_category VARCHAR(20),                -- "LARGE", "MID", "SMALL"
    day_change_pct      DECIMAL(6, 2) DEFAULT 0,    -- today's % change
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),

    -- A user can only hold one position per symbol per exchange
    CONSTRAINT uq_user_symbol_exchange UNIQUE (user_id, symbol, exchange)
);

CREATE INDEX idx_holdings_user_id ON holdings(user_id);
CREATE INDEX idx_holdings_sector ON holdings(sector);

-- ============================================================================
-- PORTFOLIO SCORES
-- ============================================================================
-- Caches computed analytics scores so we don't recalculate on every page load.
-- Each row = one score snapshot for a user at a point in time.
--
-- Design decisions:
--   • score_breakdown is JSONB — flexible enough to store the sub-scores
--     for both diversification (4 dimensions) and health (5 sub-scores)
--     without schema changes when we add new metrics.
--   • score_type distinguishes "diversification" vs "health" vs future types.
--   • We keep historical scores for trend analysis.
-- ============================================================================
CREATE TABLE IF NOT EXISTS portfolio_scores (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score_type      VARCHAR(50) NOT NULL,           -- "diversification" or "health"
    overall_score   DECIMAL(5, 2) NOT NULL,         -- 0.00 to 100.00
    score_breakdown JSONB NOT NULL DEFAULT '{}',    -- sub-score details
    calculated_at   TIMESTAMPTZ DEFAULT NOW(),

    -- For easy "latest score" queries
    CONSTRAINT uq_user_score_type_time UNIQUE (user_id, score_type, calculated_at)
);

CREATE INDEX idx_portfolio_scores_user_type ON portfolio_scores(user_id, score_type);
CREATE INDEX idx_portfolio_scores_calculated_at ON portfolio_scores(calculated_at DESC);

-- ============================================================================
-- SEED: Default demo user (for development)
-- ============================================================================
INSERT INTO users (id, email, full_name)
VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'demo@portfoliointel.dev',
    'Demo User'
) ON CONFLICT (id) DO NOTHING;
