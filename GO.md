# SmartInbox Agent — Full Project Guide

## What is this project?

An AI-powered customer support system for healthcare/insurance, built with a **Multi-Agent + RAG architecture**. It demonstrates all the skills from the JD.

---

## How it works (step by step)

1. **User submits a request** via dashboard or API (e.g. *"my MRI claim was denied"*)
2. **Triage Agent** classifies it as `claims`, `billing`, or `general`
3. **Routes to a specialist** — Claims Agent / Billing Agent / General Support
4. **RAG kicks in** — the specialist searches the `knowledge_base/` folder for relevant info (e.g. claims appeal process)
5. **LLM generates a response** using OpenAI GPT with the RAG context injected into the prompt
6. **Result stored** in PostgreSQL (or JSON file as fallback) and shown on the dashboard

---

## File-by-file breakdown

```
smart-inbox-agent/
├── agent_core/                        # All AI agent logic
│   ├── worker.py                      # Original single agent (UWM base)
│   ├── multi_agent.py                 # Multi-agent: triage + specialists + RAG
│   ├── rag.py                         # RAG engine: embeddings + similarity search
│   ├── memory.py                      # Session/conversation storage
│   └── auth.py                        # API key authentication middleware
│
├── api/                               # FastAPI backend
│   ├── main.py                        # App entry, middleware, routes
│   └── routes.py                      # ALL API endpoints
│
├── db/                                # Database layer
│   ├── schema.sql                     # PostgreSQL table definitions
│   └── database.py                    # DB operations (PG or JSON fallback)
│
├── knowledge_base/                    # Healthcare knowledge docs for RAG
│   ├── claims.txt                     # Claim filing, denials, appeals
│   ├── billing.txt                    # CPT codes, payment plans, refunds
│   └── general.txt                    # Portal guide, account mgmt
│
├── frontend/                          # Vanilla JS dashboard
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── frontend-react/                    # React dashboard (CDN, no build)
│   └── index.html
│
├── aws/deploy.md                      # AWS deployment guide
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── README.md
└── GO.md                              # This file
```

---

## Architecture Diagram

```
                    ┌──────────────┐
                    │  User Input  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  TriageAgent │ → classifies as claims/billing/general
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       ┌───────────┐ ┌──────────┐ ┌──────────┐
       │  Claims   │ │  Billing │ │ General  │
       │ Specialist│ │Specialist│ │ Support  │
       └─────┬─────┘ └────┬─────┘ └────┬─────┘
             │            │            │
             ▼            ▼            ▼
       ┌──────────────────────────────┐
       │  RAG: knowledge_base/*.txt   │
       │  (embeddings + similarity)   │
       └──────────────┬───────────────┘
                      │
                      ▼
       ┌──────────────────────────────┐
       │  OpenAI GPT generates resp.  │
       │  with RAG context in prompt  │
       └──────────────┬───────────────┘
                      │
                      ▼
       ┌──────────────────────────────┐
       │     Store in PostgreSQL      │
       │    Show on Dashboard (UI)    │
       └──────────────────────────────┘
```

---

## How RAG works

1. `knowledge_base/` has 3 text files with healthcare info
2. When a request comes in, `rag.py`:
   - Converts the query into an embedding (vector) using OpenAI
   - Converts each knowledge chunk into embeddings
   - Finds the most similar chunks via cosine similarity
   - Injects those chunks into the LLM's system prompt as context
3. The LLM answers using both its training + the provided context

---

## How to run

```bash
cd smart-inbox-agent
pip install -r requirements.txt
cp .env.example .env
# Edit .env — add your OPENAI_API_KEY

export OPENAI_API_KEY=$(grep OPENAI_API_KEY .env | cut -d= -f2-)
uvicorn api.main:app --reload
```

Then open in browser:
- **http://127.0.0.1:8000/** — Vanilla JS dashboard
- **http://127.0.0.1:8000/react** — React dashboard

---

## API Endpoints

| Method | Endpoint | What it does |
|--------|----------|-------------|
| POST | `/api/v1/agent/process` | **Main** — triage → specialist → RAG → response |
| GET | `/api/v1/tickets` | List all processed tickets |
| GET | `/api/v1/tickets?category=billing` | Filter tickets by category |
| GET | `/api/v1/tickets/{session_id}` | Get single ticket |
| GET | `/api/v1/stats` | Ticket count breakdown by category |
| GET | `/api/v1/workers` | List available agent workers |
| POST | `/api/v1/rag/search` | Directly search the knowledge base |
| GET | `/api/v1/rag/knowledge-base` | List KB categories & doc count |
| GET | `/api/v1/conversations` | List all conversation sessions |
| GET | `/api/v1/conversations/{id}` | Get conversation history |
| GET | `/api/v1/agent/memory/{id}` | Get session memory |
| GET | `/debug` | Check if API key is loaded |
| GET | `/health` | Health check |

---

## Key files explained

### `agent_core/multi_agent.py`
The heart of the project. Contains:
- **SpecialistAgent** — a domain expert (claims/billing/general) that calls the LLM with a custom system prompt + RAG context
- **MultiAgentOrchestrator** — creates 3 specialists, runs triage to classify requests, routes to the right specialist

### `agent_core/rag.py`
The RAG engine:
- Loads text files from `knowledge_base/`
- Chunks them into 500-word segments
- Creates embeddings using OpenAI
- Searches by cosine similarity
- Returns relevant context to be injected into prompts

### `api/routes.py`
All the REST endpoints. The main one is `POST /api/v1/agent/process` which calls `multi_orchestrator.process(task)`.

### `frontend/` and `frontend-react/`
Two dashboards doing the same thing — one with vanilla HTML/CSS/JS, one with React. Both call the same API endpoints.

---

## How to test

Submit requests like:
- *"My MRI claim was denied, what should I do?"* → Routes to **Claims Specialist** with RAG about appeals
- *"Can I set up a payment plan for my hospital bill?"* → Routes to **Billing Specialist** with RAG about payment plans
- *"How do I reset my portal password?"* → Routes to **General Support** with RAG about account management

---

## JD Skills Matrix

| JD Requirement | How it's covered |
|----------------|-----------------|
| UWM Architecture | `worker.py` + `multi_agent.py` (orchestrator pattern) |
| Python + APIs | FastAPI with modular packages in `api/` |
| REST APIs | 10+ endpoints in `routes.py` |
| PostgreSQL | `schema.sql` with indices + `database.py` with JSON fallback |
| LLM Integration | OpenAI GPT-4o for classification + response generation |
| Prompt Engineering | Different system prompts per specialist agent |
| Multi-Agent Patterns | Triage → Claims/Billing/General routing |
| RAG Architecture | Embeddings + cosine similarity on knowledge base |
| LangChain | Available in `requirements.txt` (can be used to extend) |
| HTML/CSS/JS | `frontend/` dashboard |
| React | `frontend-react/` dashboard |
| AWS | `aws/deploy.md` — full deployment guide (EC2, RDS, Lambda, S3, API Gateway) |
| Docker | `Dockerfile` + `docker-compose.yml` with PostgreSQL |
| API Auth | `auth.py` — configurable API key middleware |
| Healthcare Domain | `knowledge_base/` — claims, billing, general healthcare docs |
