# SQL Analyst Agent

Ever wished you could just *ask* your database a question instead of writing SQL? That's what this is.

Type a question in plain English — "which products made the most money last quarter?" — and the agent figures out the SQL, runs it, and hands you back a clean answer with a chart. No SQL knowledge required.

![Stack](https://img.shields.io/badge/LangGraph-agent-blue)
![Stack](https://img.shields.io/badge/FastAPI-backend-green)
![Stack](https://img.shields.io/badge/React-frontend-61dafb)
![Stack](https://img.shields.io/badge/PostgreSQL-database-336791)

---

## What it can do

Ask it anything about the Northwind trading database and it figures out the rest:

**"What are the top 5 products by total revenue?"**
> Côte de Blaye — $141,396.74 | Thüringer Rostbratwurst — $80,368.67
> Raclette Courdavault — $71,155.70 | Tarte au sucre — $47,234.97
> Camembert Pierrot — $46,825.48

**"Which country has the most customers?"**
> USA with 13 customers

**"Show me monthly revenue for 1997"**
> Ranges from $36,362.80 in June to $71,398.43 in December

Results come with auto-generated charts and a collapsible SQL viewer so you can see exactly what ran under the hood.

---

## How it works

The agent isn't just prompting an LLM and hoping for the best. It runs a proper pipeline:

```
Your question
      │
      ▼
Fetch schema        → pulls table/column structure from PostgreSQL
                      so the LLM knows what it's working with
      │
      ▼
Generate SQL        → LLM writes a query grounded in the real schema
      │
      ▼
Execute SQL         → runs it against PostgreSQL
                      if it fails → feeds the error back and retries (up to 3x)
      │
      ▼
Format answer       → LLM turns raw rows into a readable response
      │
      ▼
Detect chart        → checks if the data is worth visualizing (bar or line)
      │
      ▼
Response            → answer + chart + SQL
```

The schema fetch is the key step — without it, the LLM would guess column names and get them wrong. With it, every query is grounded in reality.

---

## Stack

| Layer | Technology |
|---|---|
| Agent | LangGraph (StateGraph) |
| LLM | Groq — llama-3.3-70b-versatile |
| Backend | FastAPI |
| Database | PostgreSQL + Northwind dataset |
| Observability | LangSmith |
| Frontend | React + Recharts |

---

## Features

- Plain English → SQL with full schema grounding
- Self-healing queries — retries with error feedback on failure
- Auto chart detection — bar for categories, line for trends
- SQL viewer — every answer shows the query that produced it
- Full LangSmith tracing — every node, every run, fully observable

---

## Project Structure

```
sql-analyst-agent/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── agent/
│   │   ├── graph.py         # LangGraph StateGraph
│   │   ├── tools.py         # SQL execution + chart detection
│   │   └── prompts.py       # System prompts
│   ├── db/
│   │   └── connection.py    # PostgreSQL connection + schema fetch
│   ├── .env
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── ChatBox.jsx
│           ├── ResultTable.jsx
│           └── Chart.jsx
├── postmortem.md
└── README.md
```

---

## Running it locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 16+

### 1. Database

```bash
psql postgres
CREATE DATABASE northwind;
\q

curl -O https://raw.githubusercontent.com/pthom/northwind_psql/master/northwind.sql
psql -d northwind -f northwind.sql
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql://your_user@localhost:5432/northwind
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=sql-analyst-agent
```

```bash
uvicorn main:app --reload
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** and start asking questions.

---

## Observability

Every agent run is fully traced in LangSmith — each node shows timing, inputs, and outputs. This makes it possible to catch failures that would otherwise be invisible: SQL that runs without errors but returns wrong answers.

This project includes a real example of exactly that. See [postmortem.md](./postmortem.md) — a documented silent semantic failure where the agent answered confidently but got it wrong, and why.

---

## Honest limitations

- Ambiguous questions ("who's the best employee?") get answered without clarification — the LLM picks the most likely interpretation silently. See the postmortem for why this matters.
- Schema is fetched on every request — fine for a demo, worth caching in production
- Chart type is a simple heuristic: ≤10 rows → bar, >10 rows → line

---

## Context

Built as Project 3 on Week 4: database integration, observability & tools.