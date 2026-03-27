# API Specification — Agentic Hallucination Guardrail

| Field          | Value                                      |
|----------------|--------------------------------------------|
| **Sprint**     | 3 — Interface & Observability Layer        |
| **Type**       | Roadmap Only (no implementation)           |
| **Status**     | Draft                                      |
| **Base URL**   | `http://localhost:8000`                    |
| **Protocol**   | HTTP/1.1 + Server-Sent Events (SSE)       |
| **Auth**       | None (local-only deployment)               |
| **Version**    | 0.1.0                                      |

---

## Table of Contents

1. [Overview](#overview)
2. [Global Conventions](#global-conventions)
3. [Endpoints](#endpoints)
   - [3.5.1 POST /api/query](#351-post-apiquery)
   - [3.5.2 GET /api/stream/{trace_id}](#352-get-apistreamtrace_id)
   - [3.5.3 GET /api/health](#353-get-apihealth)
   - [3.5.4 GET /api/config](#354-get-apiconfig)
   - [3.5.5 GET /api/traces/{trace_id}](#355-get-apitracestrace_id)
4. [Error Format](#error-format)
5. [Cross-References](#cross-references)

---

## 1. Overview

This document defines the REST + SSE API surface for the Agentic Hallucination Guardrail system. All endpoints are served by a FastAPI application running inside the `guardrail-api` container. Query results are delivered asynchronously via Server-Sent Events so the UX Renderer can display agent activity in real time.

## 2. Global Conventions

**CORS.** In development the server allows origins matching `http://localhost:3000` with credentials support. No other origins are permitted.

**Rate Limiting.** 10 requests per second per client IP. Because the system targets local deployment this limit is intentionally lenient and exists only to prevent accidental tight loops.

**Authentication.** None. The API is designed for local-only access behind a Docker network. If the system is ever exposed publicly, an API-key middleware should be added.

**Content-Type.** All request and response bodies use `application/json` unless otherwise noted. SSE streams use `text/event-stream`.

---

## 3. Endpoints

### 3.5.1 POST /api/query

Submit a new natural-language query for processing by the agent pipeline.

**Request**

```json
{
  "query": "string (required — the user question)",
  "session_id": "string | null (optional — groups traces under one session)",
  "config_overrides": {
    "pass_threshold": "float | null (optional — override pass_threshold for this run)",
    "max_retries": "int | null   (optional — override max_retries for this run)",
    "temperature_init": "float | null (optional — override starting temperature)"
  }
}
```

**Response — 202 Accepted**

```json
{
  "trace_id": "string (UUID v4)",
  "status": "ACCEPTED"
}
```

The client should immediately open an SSE connection to `/api/stream/{trace_id}` to receive real-time agent updates. Results are never returned inline.

**Error — 400 / 503**

Returns the standard error envelope (see [Error Format](#error-format)).

---

### 3.5.2 GET /api/stream/{trace_id}

Opens a Server-Sent Events stream that emits one event per agent action.

**Headers**

| Header           | Purpose                                         |
|------------------|--------------------------------------------------|
| `Accept`         | Must be `text/event-stream`                      |
| `Last-Event-ID`  | Optional — server replays all events after this sequence number on reconnect |

**Event: agent_update**

Emitted each time an agent completes an action.

```
event: agent_update
data: {
  "seq": 1,
  "agent": "inference_agent",
  "action": "generate_response",
  "timestamp": "2026-03-26T12:00:00.000Z",
  "duration_ms": 340,
  "status": "complete",
  "payload": {}
}
```

**Terminal Event: complete**

Emitted once when the pipeline finishes successfully.

```
event: complete
data: {
  "trace_id": "uuid",
  "final_response": "string",
  "confidence_score": 0.92,
  "retry_count": 1
}
```

**Terminal Event: error**

Emitted if the pipeline fails irrecoverably.

```
event: error
data: {
  "trace_id": "uuid",
  "error": {
    "code": "BUDGET_EXCEEDED",
    "message": "Token ceiling reached before a passing response was produced."
  }
}
```

**Reconnection.** When a client sends `Last-Event-ID: <seq>`, the server replays every event with `seq > <Last-Event-ID>` before resuming the live stream. Events are retained in memory until the trace is finalized.

---

### 3.5.3 GET /api/health

Returns the operational status of the system and each agent.

> **Cross-ref:** Response fields align with the `HealthStatus` model defined in `agent-design.md`. The endpoint itself is declared in `containerization.md` as the Docker health-check target.

**Response — 200 OK**

```json
{
  "status": "healthy | degraded | unhealthy",
  "agents": {
    "mother_agent": "running | stopped | error",
    "inference": "running | stopped | error",
    "validator": "running | stopped | error",
    "corrector": "running | stopped | error",
    "critic": "running | stopped | error",
    "ux_renderer": "running | stopped | error"
  },
  "budget": {
    "ceiling": 4096,
    "consumed": 1520,
    "remaining": 2576
  },
  "uptime_ms": 84200,
  "version": "0.1.0",
  "ollama_status": "connected | disconnected",
  "model_loaded": true
}
```

---

### 3.5.4 GET /api/config

Returns the active system configuration values.

> **Cross-ref:** Every field maps 1-to-1 with the `config` object inside the State Schema defined in `architecture.md`.

**Response — 200 OK**

```json
{
  "pass_threshold": 0.7,
  "max_retries": 3,
  "temperature_init": 0.7,
  "temperature_decay": 0.15,
  "inference_timeout": 30,
  "critic_model": "llama3",
  "enable_toxicity": true,
  "token_ceiling": 4096
}
```

---

### 3.5.5 GET /api/traces/{trace_id}

Retrieves the full trace log for a completed (or failed) query.

**Response — 200 OK**

```json
{
  "trace_id": "string (UUID v4)",
  "session_id": "string | null",
  "query": "original user query",
  "status": "pass | fail | error",
  "created_at": "ISO-8601 timestamp",
  "completed_at": "ISO-8601 timestamp",
  "total_latency_ms": 1240.5,
  "retry_count": 1,
  "confidence_score": 0.92,
  "metric_breakdown": {
    "faithfulness": 0.95,
    "answer_relevancy": 0.88,
    "hallucination": 0.10,
    "toxicity": 0.01
  },
  "correction_history": [
    "Array of correction objects produced by the Corrector Agent on each retry"
  ],
  "trace_log": [
    {
      "seq": 1,
      "agent": "inference_agent",
      "action": "generate_response",
      "timestamp": "ISO-8601",
      "duration_ms": 340,
      "status": "complete",
      "payload": {}
    }
  ],
  "final_response": "The validated answer string returned to the user."
}
```

**Error — 404**

Returns `TRACE_NOT_FOUND` via the standard error envelope when the trace ID does not exist.

---

## 4. Error Format

All error responses share this envelope:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "trace_id": "string | null (present when error relates to an active trace)"
  }
}
```

**Standard Error Codes**

| Code                 | HTTP Status | Description                                      |
|----------------------|-------------|--------------------------------------------------|
| `INVALID_REQUEST`    | 400         | Malformed JSON or invalid field values            |
| `QUERY_EMPTY`        | 400         | The `query` field is missing or blank             |
| `TRACE_NOT_FOUND`    | 404         | No trace exists with the given `trace_id`         |
| `SERVICE_UNAVAILABLE`| 503         | Ollama is disconnected or a critical agent is down|
| `BUDGET_EXCEEDED`    | 429         | Token ceiling reached; retry with a new query     |

---

## 5. Cross-References

| Reference Target                              | Relationship                                                |
|-----------------------------------------------|-------------------------------------------------------------|
| `architecture.md` — State Schema / `config`   | Fields in `/api/config` response mirror the config object   |
| `agent-design.md` — `HealthStatus` model      | Fields in `/api/health` response mirror `HealthStatus`      |
| `containerization.md` — Health-check endpoint  | Docker HEALTHCHECK calls `GET /api/health`                  |
