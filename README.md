# Agentic Hallucination Guardrail

A production-grade LLMOps pipeline that **detects, validates, and corrects hallucinations** in LLM responses in real time. Built with a LangGraph state machine orchestrating multi-agent workflows, backed by local inference via Ollama for zero-cost, zero-latency operation.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.1.0-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-State%20Machine-1C3C3C?logo=langchain&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-000000)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Table of Contents

- [Why This Exists](#why-this-exists)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [License](#license)

---

## Why This Exists

LLM hallucinations are a critical barrier to deploying AI in production. Studies show **15-20% of LLM outputs contain fabricated information** that passes surface-level plausibility checks. Existing solutions rely on expensive cloud API calls and post-hoc evaluation.

This project takes a different approach:

- **Inline validation** -- responses are scored before delivery, not after
- **Adaptive correction** -- failed responses trigger temperature-decayed retries that converge toward deterministic outputs
- **Circuit breaker** -- after 3 retries, a safe fallback response is returned instead of an unreliable answer
- **Full observability** -- every pipeline execution is traced end-to-end with latency, retry count, confidence scores, and metric breakdowns

---

## Architecture

```
                    +-----------+
                    |  User     |
                    |  Query    |
                    +-----+-----+
                          |
                          v
                   +------+------+
                   | Mother Agent|  (Orchestrator + Token Budget)
                   +------+------+
                          |
              +-----------+-----------+
              |     LangGraph FSM     |
              |                       |
              |   +---------------+   |
              |   | Inference     |<--+---- Ollama (DeepSeek-R1)
              |   +-------+-------+   |
              |           |           |
              |   +-------v-------+   |
              |   | Validator     |   |     score >= 0.7?
              |   +-------+-------+   |
              |           |           |
              |     +-----+-----+     |
              |     |           |     |
              |   Pass        Fail    |
              |     |           |     |
              |     v           v     |
              |  +------+  +-------+  |
              |  |Respond|  |Correct|  |     retry < 3? loop back
              |  +---+---+  +---+---+  |     retry = 3? fallback
              |      |          |      |
              +------+----+----+------+
                          |
                    +-----v-----+
                    | SSE Stream|  (Real-time events to frontend)
                    +-----------+
```

**Key design decisions:**

| Decision                   | Rationale                                                         |
| -------------------------- | ----------------------------------------------------------------- |
| Local inference (Ollama)   | Zero cost, zero latency variance, full model control              |
| Temperature decay on retry | 0.7 → 0.55 → 0.4 → 0.25 converges toward deterministic outputs    |
| Per-query token budget     | 8192-token ceiling prevents runaway costs; fresh ledger per query |
| State hashing (SHA-256)    | Detects infinite loops by hashing mutable state fields            |
| SSE with sequence numbers  | Enables client-side reordering on reconnect                       |

---

## Tech Stack

### Backend

| Component              | Technology                   |
| ---------------------- | ---------------------------- |
| Framework              | FastAPI                      |
| LLM Inference          | Ollama (DeepSeek-R1)         |
| Pipeline Orchestration | LangGraph (StateGraph)       |
| Database               | SQLite (async via aiosqlite) |
| HTTP Client            | httpx (async)                |
| Real-time Streaming    | SSE (sse-starlette)          |
| Validation Models      | Pydantic                     |
| Linting/Formatting     | Ruff                         |
| Testing                | pytest + pytest-asyncio      |

### Frontend

| Component  | Technology       |
| ---------- | ---------------- |
| Framework  | Next.js 15       |
| UI Library | React 19         |
| Styling    | Tailwind CSS 4   |
| Animations | Framer Motion 11 |
| Charts     | Recharts 2       |
| Language   | TypeScript 5     |

### Infrastructure

| Component        | Technology                  |
| ---------------- | --------------------------- |
| Containerization | Docker Compose (3 services) |
| GPU Support      | NVIDIA Container Toolkit    |
| CI/CD            | GitHub Actions (planned)    |

---

## Getting Started

### Prerequisites

- **Python 3.9+**
- **Node.js 18+** and **pnpm**
- **Ollama** installed locally ([ollama.com](https://ollama.com))
- **Docker** and **Docker Compose** (optional, for containerized deployment)
- **NVIDIA GPU + drivers** (optional, for accelerated inference)

### Option 1: Docker Compose (Recommended)

One command spins up Ollama (with auto model pull), FastAPI, and Next.js:

```bash
make docker-up
```

This builds and starts all three services:

| Service | Port    | Description          |
| ------- | ------- | -------------------- |
| Ollama  | `11434` | LLM inference server |
| FastAPI | `8000`  | Backend API          |
| Next.js | `3000`  | Frontend dashboard   |

To stop:

```bash
make docker-down
```

### Option 2: Local Development

You need **three processes running simultaneously**, each in its own terminal: Ollama, the backend API, and the frontend dev server. Start them in order — each depends on the previous one.

1. **Clone the repository**

```bash
git clone https://github.com/<your-username>/agentic-hallucination-guardrail.git
cd agentic-hallucination-guardrail
```

2. **Set up environment variables**

```bash
cp .env.example .env
```

3. **Start Ollama and pull the model** *(Terminal 1)*

Ollama must be installed ([ollama.com](https://ollama.com)) and **running** before you start the backend. In a dedicated terminal:

```bash
ollama serve
```

Then, in any terminal, pull the model (this is a one-time ~4 GB download):

```bash
ollama pull deepseek-r1:latest
```

> **Important:** `ollama serve` must stay running. Do not close this terminal.

4. **Install backend dependencies and start the API** *(Terminal 2)*

The backend connects to Ollama on startup, so Ollama must be running first.

```bash
pip install -r src/backend/requirements.txt
python -m uvicorn src.backend.api:app --reload --port 8000
```

Verify it's working: `curl http://localhost:8000/api/health` should return `{"status": "healthy", ...}`.

5. **Install frontend dependencies and start the dashboard** *(Terminal 3)*

The frontend proxies `/api` requests to the backend at `localhost:8000`, so the backend must be running first.

```bash
cd src/frontend
pnpm install
pnpm dev
```

The API will be live at `http://localhost:8000` and the frontend at `http://localhost:3000`.

### Troubleshooting

If the dashboard header shows **"Offline"** badges, check the following:

| Badge | Shows "Offline" when | Fix |
|-------|---------------------|-----|
| **Ollama** | Ollama is not running | Run `ollama serve` in a terminal and keep it open |
| **DeepSeek-R1** | The model hasn't been pulled | Run `ollama pull deepseek-r1:latest` |
| **Pipeline** | The backend API is not running or cannot reach Ollama | Start the backend with `python -m uvicorn src.backend.api:app --reload --port 8000` and ensure Ollama is running |

If **all three** badges show "Offline", the frontend likely cannot reach the backend. Make sure the backend is running on port 8000 before starting the frontend.

---

## API Reference

| Method | Endpoint                 | Description                                        |
| ------ | ------------------------ | -------------------------------------------------- |
| `POST` | `/api/query`             | Submit a query for hallucination-guarded inference |
| `GET`  | `/api/stream/{trace_id}` | SSE stream of real-time pipeline events            |
| `GET`  | `/api/traces/{trace_id}` | Retrieve full trace data                           |
| `GET`  | `/api/health`            | System health + Ollama connectivity                |
| `GET`  | `/api/config`            | Active configuration and thresholds                |

### Submit a Query

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What causes hallucinations in large language models?"}'
```

**Response** (202 Accepted):

```json
{
  "trace_id": "a1b2c3d4-...",
  "status": "ACCEPTED"
}
```

### Stream Pipeline Events

```bash
curl -N http://localhost:8000/api/stream/a1b2c3d4-...
```

**SSE events:** `agent_update`, `complete`, `error`, `ping`

### Retrieve Trace

```bash
curl http://localhost:8000/api/traces/a1b2c3d4-...
```

**Response** includes: query, status, latency_ms, retry_count, confidence_score, metric_breakdown, correction_history, and final_response.

---

## Configuration

### Environment Variables

| Variable                | Default                    | Description                           |
| ----------------------- | -------------------------- | ------------------------------------- |
| `OLLAMA_HOST`           | `http://localhost:11434`   | Ollama server URL                     |
| `DATABASE_URL`          | `sqlite:///data/traces.db` | SQLite database path                  |
| `LOG_LEVEL`             | `info`                     | Logging verbosity                     |
| `STUB_VALIDATION_SCORE` | —                          | Override validation score for testing |

### Per-Query Overrides

Pass these in the `POST /api/query` request body:

```json
{
  "query": "...",
  "pass_threshold": 0.7,
  "max_retries": 3,
  "temperature_init": 0.7
}
```

### Validation Rules

Fine-grained control via `src/backend/config/validation_rules.json`:

- **Metric weights:** faithfulness (0.35), hallucination (0.30), answer relevancy (0.25), toxicity (0.10)
- **Confidence thresholds:** critic accept (0.85), evaluator pass (0.80)
- **Banned patterns:** "As an AI", "I cannot verify", etc.
- **Circuit breaker:** loop detection window of 5, half-open retry after 60s
- **Timeouts:** 30s per agent, 120s total pipeline

---

## Testing

```bash
# Run all tests
pytest src/backend/tests/ -v

# Run with coverage report
pytest src/backend/tests/ -v --cov=src/backend --cov-report=term-missing

# Lint
ruff check src/backend/

# Format
ruff format src/backend/
```

> **Note:** If you have `make` available (Linux/macOS), you can use `make test`, `make test-cov`, `make lint`, and `make format` as shortcuts.

**Test categories:**

- **Unit** -- Individual node logic (inference, validator, corrector, fallback)
- **Integration** -- Full graph traversal (happy path, retry path, circuit break)
- **Configuration** -- Stub score overrides, temperature decay verification

---

## Project Structure

```
agentic-hallucination-guardrail/
├── src/
│   ├── backend/
│   │   ├── api.py                       # FastAPI app (5 endpoints + SSE)
│   │   ├── orchestration/
│   │   │   ├── mother_agent.py          # Orchestrator + token budget
│   │   │   └── graph_engine.py          # LangGraph state machine (6 nodes)
│   │   ├── agents/
│   │   │   └── critic_agent.py          # Response critique agent
│   │   ├── evaluation/
│   │   │   └── evaluator.py             # Metric computation engine
│   │   ├── db/
│   │   │   └── database.py              # SQLite async persistence
│   │   ├── config/
│   │   │   └── validation_rules.json    # Thresholds, weights, timeouts
│   │   └── tests/
│   │       ├── conftest.py              # Shared fixtures
│   │       ├── test_graph_engine.py     # Pipeline path tests
│   │       ├── test_mother_agent.py     # Orchestrator tests
│   │       └── test_api_endpoints.py    # API integration tests
│   └── frontend/
│       ├── app/
│       │   ├── layout.tsx               # Root layout
│       │   └── page.tsx                 # Dashboard (in progress)
│       ├── package.json
│       └── tsconfig.json
├── data/                                # SQLite database (gitignored)
├── documentation/                       # Specs, sprint plans, audits
├── docker-compose.yml                   # 3-service stack (Ollama + API + UI)
├── Makefile                             # Dev, test, lint, docker commands
├── .env.example                         # Environment template
└── LICENSE
```

---

## Documentation

Detailed specifications live in `documentation/`, organized by sprint:

| Sprint   | Focus                                                            |
| -------- | ---------------------------------------------------------------- |
| Sprint 0 | Market research, hallucination taxonomy, model comparison        |
| Sprint 1 | System architecture, state machine design, technology stack      |
| Sprint 2 | Agent interaction protocols, conflict resolution, error handling |
| Sprint 3 | API specification, file manifest, CI/CD, containerization        |
| Sprint 4 | UX standards, accessibility, responsive design                   |
| Sprint 5 | Acceptance criteria, performance benchmarks, feature specs       |
| Sprint 6 | Testing strategy, QA audits, production readiness                |

---

## License

This project is licensed under the [MIT License](LICENSE).
