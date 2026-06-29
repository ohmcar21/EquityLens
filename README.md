# 📈 EquityLens

### AI Portfolio Intelligence Platform

EquityLens is a full-stack AI-powered portfolio intelligence platform that helps investors understand the quality of their portfolio through advanced analytics, historical comparisons, sector analysis, and AI-generated insights.

Unlike traditional portfolio trackers that only display holdings and returns, EquityLens focuses on **portfolio intelligence** by converting raw investment data into meaningful, actionable insights.

> **Built with Next.js, FastAPI, PostgreSQL, Groq AI, SQLAlchemy, and TypeScript.**

---

## 📸 Dashboard Preview

> *Dashboard screenshots coming soon.*

---

# ✨ Features

* 📂 CSV Portfolio Upload
* 🤖 AI-Powered Portfolio Insights
* 📊 Portfolio Health Score
* 🎯 Diversification Analysis
* 🏢 Sector Allocation Analysis
* 📈 Historical Portfolio Comparison
* 💾 Automatic Historical Snapshot Tracking
* 🔌 Broker-Ready Architecture
* 📱 Responsive Dashboard
* ⚡ FastAPI + PostgreSQL Backend

---

# 🚀 Tech Stack

## Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS
* Recharts

## Backend

* FastAPI
* SQLAlchemy (Async)
* Pydantic
* PostgreSQL
* asyncpg

## AI

* Groq LLM

## Architecture

* Service-Oriented Architecture
* Broker Abstraction Layer
* Parent-Managed State Architecture
* Historical Snapshot Engine

---

# 🏗️ System Architecture

```text
                     CSV Upload
                          │
                          ▼
                 Portfolio Parser
                          │
                          ▼
             Portfolio Analytics Engine
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
 Historical Snapshot Engine        AI Insights Engine
          │                               │
          └───────────────┬───────────────┘
                          ▼
                  PostgreSQL Database
                          │
                          ▼
               Next.js Interactive Dashboard
```

---

# 📊 Core Features

| Feature                         | Status       |
| ------------------------------- | ------------ |
| CSV Portfolio Upload            | ✅            |
| Portfolio Analytics             | ✅            |
| AI Portfolio Insights           | ✅            |
| Portfolio Health Score          | ✅            |
| Diversification Analysis        | ✅            |
| Sector Allocation               | ✅            |
| Historical Portfolio Comparison | ✅            |
| Historical Snapshot Engine      | ✅            |
| Broker Abstraction Layer        | ✅            |
| Responsive Dashboard            | ✅            |
| Live Broker Integration         | 🚧 Version 2 |

---

# 📈 Portfolio Analytics

EquityLens evaluates portfolio quality using multiple analytical models:

* Portfolio Health Score
* Diversification Analysis
* Sector Allocation Analysis
* Stock Concentration Analysis
* Historical Portfolio Comparison
* AI-Generated Portfolio Insights

These metrics provide investors with a deeper understanding of portfolio quality beyond simple profit and loss.

---

# 📂 Project Structure

```text
EquityLens/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── services/
│   └── public/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── brokers/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── core/
│   │
│   ├── requirements.txt
│   └── .env
│
├── database/
│
└── README.md
```

---

# ⚙️ Getting Started

## Prerequisites

* Python 3.10+
* Node.js 18+
* PostgreSQL 15+

---

## Clone the Repository

```bash
git clone <repository-url>

cd EquityLens
```

---

## Backend Setup

```bash
cd backend

pip install -r requirements.txt
```

Create a `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/portfolio_intel

BROKER_MODE=mock
```

Initialize the database using the SQL schema:

```text
database/schema.sql
```

Run the backend:

```bash
uvicorn app.main:app --reload
```

Backend URLs:

```
Swagger UI
http://localhost:8000/docs

ReDoc
http://localhost:8000/redoc
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Open:

```
http://localhost:3000
```

---

# 📌 Workflow

```text
Upload Portfolio CSV
          │
          ▼
Backend Parses Holdings
          │
          ▼
Portfolio Analytics Engine
          │
          ▼
Historical Snapshot Storage
          │
          ▼
AI Insight Generation
          │
          ▼
Interactive Dashboard
```

---

# 🎯 Why EquityLens?

Most investment platforms show **what you own**.

EquityLens helps investors understand **how healthy their portfolio actually is** by combining portfolio analytics, historical tracking, diversification analysis, and AI-generated insights into a single intelligent dashboard.

---

# 🚀 Future Roadmap

* Live Broker Integration
* Multi-Broker Support
* User Authentication
* Cloud Deployment
* Advanced Portfolio Analytics
* Portfolio Timeline Visualization
* PDF Portfolio Reports

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

Feel free to fork the repository and submit a pull request.

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Built With

**Next.js • React • TypeScript • FastAPI • PostgreSQL • SQLAlchemy • Groq AI • Tailwind CSS**
