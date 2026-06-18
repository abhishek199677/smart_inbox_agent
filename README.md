# SmartInbox Agent

An AI-powered support ticket system using **multi-agent architecture** with **RAG (Retrieval-Augmented Generation)** and healthcare/insurance domain knowledge.

## Architecture

```
User Input
    │
    ▼
Triage Agent ──► Claims Specialist ──► RAG (knowledge_base/claims.txt)
    │               + LLM response
    ├──► Billing Specialist ──► RAG (knowledge_base/billing.txt)
    │       + LLM response
    └──► General Support ──► RAG (knowledge_base/general.txt)
            + LLM response
                │
                ▼
          Memory Store / PostgreSQL
                │
                ▼
          Dashboard UI (React + Vanilla)
```

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

uvicorn api.main:app --reload
```

## Frontends

| URL | Description |
|-----|-------------|
| `http://127.0.0.1:8000/` | Vanilla JS dashboard |
| `http://127.0.0.1:8000/static/react.html` | React dashboard |

## Project Structure

```
├── agent_core/
│   ├── worker.py          # Base UWM worker (original single agent)
│   ├── multi_agent.py     # Multi-agent: triage + 3 specialist agents
│   ├── rag.py             # RAG engine (embeddings + similarity search)
│   ├── memory.py          # Session & conversation memory
│   └── auth.py            # API key authentication middleware
├── api/
│   ├── main.py            # FastAPI app entry
│   └── routes.py          # All API endpoints
├── db/
│   ├── schema.sql         # PostgreSQL schema (tickets + knowledge docs)
│   └── database.py        # DB operations
├── knowledge_base/        # Healthcare domain documents for RAG
│   ├── claims.txt
│   ├── billing.txt
│   └── general.txt
├── frontend/              # Vanilla JS dashboard
├── frontend-react/        # React (CDN, no build step) dashboard
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/agent/process` | Multi-agent: triage + specialist + RAG |
| POST | `/api/v1/agent/legacy-process` | Original single-agent (backward compat) |
| GET | `/api/v1/workers` | List all registered agent workers |
| GET | `/api/v1/tickets` | List tickets (filter by ?category=) |
| GET | `/api/v1/stats` | Ticket statistics by category |
| POST | `/api/v1/rag/search` | Query the knowledge base directly |
| GET | `/api/v1/rag/knowledge-base` | List KB categories and doc count |
| GET | `/api/v1/conversations` | List all conversation sessions |
| GET | `/api/v1/agent/memory/{id}` | Get session memory |
| GET | `/debug` | Environment check (has_key, paths) |

## Skills Matrix

| JD Requirement | How It's Covered |
|----------------|-----------------|
| UWM Architecture | Base worker + multi-agent orchestrator |
| Python Backend | FastAPI with modular packages |
| REST APIs | 10+ documented endpoints |
| PostgreSQL | Schema with indices + JSON fallback |
| LLM Integration | OpenAI GPT-4o classification + response |
| Prompt Engineering | Domain-specific system prompts per agent |
| HTML/CSS/JS | Vanilla dashboard |
| React.js | CDN-based React dashboard |
| AWS Cloud | EC2 / Lambda / RDS / S3 / API Gateway |
| Docker | Dockerfile + docker-compose |
| Multi-Agent Patterns | Triage + specialists + orchestrator |
| RAG Architecture | Embeddings + cosine similarity retrieval |
| LangChain | Available (langchain + langchain-openai in reqs) |
| Healthcare Domain | Knowledge base with claims/billing/general docs |
| API Security | Configurable API key auth middleware |

## Docker

```bash
docker-compose up --build
```

## Running with Auth

Add `API_KEY=your-secret-key` to `.env`. Then include header on all requests:
```
Authorization: Bearer your-secret-key
```
