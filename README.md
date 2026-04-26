# SQL Analyst Agent

A natural language interface to a PostgreSQL database, powered by
LangGraph, Groq, and FastAPI. Ask questions in plain English and
get structured answers, auto-generated charts, and full SQL transparency.

![Stack](https://img.shields.io/badge/LangGraph-agent-blue)
![Stack](https://img.shields.io/badge/FastAPI-backend-green)
![Stack](https://img.shields.io/badge/React-frontend-61dafb)
![Stack](https://img.shields.io/badge/PostgreSQL-database-336791)

---

## Demo

**Top 5 products by revenue**
> Côte de Blaye — $141,396.74 | Thüringer Rostbratwurst — $80,368.67
> Raclette Courdavault — $71,155.70 | Tarte au sucre — $47,234.97
> Camembert Pierrot — $46,825.48

**Country with most customers**
> USA with 13 customers

**Monthly revenue for 1997**
> Ranges from $36,362.80 (June) to $71,398.43 (December)

---

## How It Works

```
User Question
      │
      ▼
schema_context_node   → fetches table/column structure from PostgreSQL
      │
      ▼
sql_generate_node     → LLM writes SQL using schema as context
      │
      ▼
sql_execute_node      → runs SQL against PostgreSQL
      │                 on failure → retries with error feedback (max 3x)
      ▼
format_answer_node    → LLM formats raw results into natural language
      │
      ▼
chart_node            → detects if result is chartable (bar / line)
      │
      ▼
Response (answer + chart + SQL)
```

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

- Natural language → SQL translation with schema grounding
- Auto-retry on SQL errors (up to 3 attempts with error feedback)
- Bar and line chart auto-detection based on result shape
- Collapsible SQL viewer for full transparency
- Full LangSmith tracing for every agent run

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

## Setup

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

Open **http://localhost:5173**

---

## Observability

Every agent run is traced in LangSmith. Each node appears with
timing, inputs, and outputs — making it easy to catch silent
failures like wrong SQL that runs without errors.

See [postmortem.md](./postmortem.md) for a documented example of
a silent semantic failure caught using LangSmith traces.

---

## Known Limitations

- Ambiguous superlatives ("best", "worst", "top performing") are
  resolved by the LLM without clarification — see postmortem
- Schema is fetched on every request — can be cached for performance
- Chart type is heuristic-based (≤10 rows = bar, >10 = line)

---

## Part of

Built as Project 3 of the
[CampusX Agentic AI using LangGraph](https://github.com/campusx)
curriculum — Week 4: Database integration, observability & tools.