# Sprint 1 — Architecture Document
## Agentic Hallucination Guardrail (LLMOps)

**Version:** 1.0.0
**Sprint:** 1 — Foundation & Architecture
**Date:** 2026-03-21
**Status:** ROADMAP ONLY — No code deliverables in this document

---

## Table of Contents

1. [Section 1.1 — System Architecture Design](#section-11--system-architecture-design)
   - [1.1.1 High-Level State Machine Diagram](#111-high-level-state-machine-diagram)
   - [1.1.2 Node Specifications](#112-node-specifications)
   - [1.1.3 State Schema](#113-state-schema)
   - [1.1.4 State Transitions and Conditions](#114-state-transitions-and-conditions)
   - [1.1.5 Retry Loop Mechanics](#115-retry-loop-mechanics)
   - [1.1.6 Circuit Breaker Specification](#116-circuit-breaker-specification)
2. [Section 1.2 — Agent Swarm Blueprint](#section-12--agent-swarm-blueprint)
   - [1.2.1 Agent Overview Table](#121-agent-overview-table)
   - [1.2.2 Mother Agent — Detailed Specification](#122-mother-agent--detailed-specification)
   - [1.2.3 Inference Agent — Detailed Specification](#123-inference-agent--detailed-specification)
   - [1.2.4 Validator Agent — Detailed Specification](#124-validator-agent--detailed-specification)
   - [1.2.5 Corrector Agent — Detailed Specification](#125-corrector-agent--detailed-specification)
   - [1.2.6 Critic Agent (Local) — Detailed Specification](#126-critic-agent-local--detailed-specification)
   - [1.2.7 UX Renderer Agent — Detailed Specification](#127-ux-renderer-agent--detailed-specification)
   - [1.2.8 Inter-Agent Communication Protocol](#128-inter-agent-communication-protocol)
3. [Section 1.3 — Technology Stack (Zero-Cost Only)](#section-13--technology-stack-zero-cost-only)
   - [1.3.1 Stack Overview Table](#131-stack-overview-table)
   - [1.3.2 Layer-by-Layer Deep Dive](#132-layer-by-layer-deep-dive)
   - [1.3.3 Integration Map](#133-integration-map)
   - [1.3.4 Deployment Topology](#134-deployment-topology)

---

# Section 1.1 — System Architecture Design

## 1.1.1 High-Level State Machine Diagram

The core of the system is a LangGraph state machine that routes every user query through inference, validation, and conditional correction before a response ever reaches the UI. The graph enforces a hard ceiling of three retry attempts before engaging a circuit breaker that delivers a safe fallback response.

```
                         AGENTIC HALLUCINATION GUARDRAIL — STATE MACHINE
  ┌─────────────────────────────────────────────────────────────────────────────────────┐
  │                                                                                     │
  │                                                                                     │
  │   ┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐                  │
  │   │             │     │                 │     │                 │                  │
  │   │  USER QUERY │────>│ INFERENCE NODE  │────>│ VALIDATOR NODE  │                  │
  │   │  (Entry)    │     │                 │     │                 │                  │
  │   └─────────────┘     └─────────────────┘     └────────┬────────┘                  │
  │                              ^                         │                            │
  │                              │                         │                            │
  │                              │              ┌──────────┴──────────┐                 │
  │                              │              │   DECISION GATE     │                 │
  │                              │              │  (score >= 0.7?)    │                 │
  │                              │              └──────────┬──────────┘                 │
  │                              │                         │                            │
  │                              │              ┌──────────┴──────────┐                 │
  │                              │              │                     │                 │
  │                              │           [PASS]               [FAIL]               │
  │                              │              │                     │                 │
  │                              │              v                     v                 │
  │                              │   ┌─────────────────┐  ┌─────────────────────┐      │
  │                              │   │                 │  │                     │      │
  │                              │   │  RESPONSE NODE  │  │  CORRECTOR NODE    │      │
  │                              │   │                 │  │  (retry < 3?)      │      │
  │                              │   └────────┬────────┘  └──────────┬──────────┘      │
  │                              │            │                      │                  │
  │                              │            v           ┌──────────┴──────────┐       │
  │                              │   ┌─────────────────┐  │                     │       │
  │                              │   │                 │  │              [retry < 3]    │
  │                              │   │    UI OUTPUT    │  │                     │       │
  │                              │   │  (validated)    │  │     [retry >= 3]    │       │
  │                              │   │                 │  │         │           │       │
  │                              │   └─────────────────┘  │         v           │       │
  │                              │                        │  ┌──────────────┐   │       │
  │                              │                        │  │  CIRCUIT     │   │       │
  │                              └────────────────────────┘  │  BREAKER     │   │       │
  │                              (corrected response loops   │              │   │       │
  │                               back to Inference Node)    └──────┬───────┘   │       │
  │                                                                 │           │       │
  │                                                                 v           │       │
  │                                                          ┌──────────────┐   │       │
  │                                                          │  FALLBACK    │   │       │
  │                                                          │  NODE        │   │       │
  │                                                          └──────┬───────┘   │       │
  │                                                                 │           │       │
  │                                                                 v           │       │
  │                                                          ┌──────────────┐   │       │
  │                                                          │  UI OUTPUT   │   │       │
  │                                                          │  (w/ warning)│   │       │
  │                                                          └──────────────┘   │       │
  │                                                                             │       │
  └─────────────────────────────────────────────────────────────────────────────────────┘
```

### Condensed Flow (Linear Reading)

```
USER QUERY
  │
  ├──> Inference Node ──> Validator Node ──> Decision Gate
  │                                              │
  │                                    ┌─────────┴──────────┐
  │                                    │                    │
  │                                  PASS                 FAIL
  │                                    │                    │
  │                                    v                    v
  │                              Response Node       Corrector Node
  │                                    │                    │
  │                                    v             retry_count < 3?
  │                                UI (clean)         /          \
  │                                                YES            NO
  │                                                 │              │
  │                                                 v              v
  │                                          Inference Node   Fallback Node
  │                                          (loop back)           │
  │                                                                v
  │                                                         UI (with warning)
```

---

## 1.1.2 Node Specifications

### Node 1: User Query (Entry Point)

| Property        | Value                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Role**        | System entry point; captures and normalizes the user's raw input      |
| **Inputs**      | Raw user query string, optional session context, optional config overrides |
| **Outputs**     | Normalized query object written to state                              |
| **Side Effects**| Initializes the shared state; sets `retry_count = 0`; generates `trace_id` |

**Detailed Behavior:**
- Accepts raw text from the frontend via the Next.js API route.
- Strips leading/trailing whitespace; rejects empty queries with a 400 error.
- Generates a unique `trace_id` (UUID v4) that follows the request through every node for observability.
- Writes the initial state object to LangGraph's shared state store.
- If a `session_id` is provided, loads previous conversation turns from SQLite for multi-turn context.

---

### Node 2: Inference Node

| Property        | Value                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Role**        | Generates the primary LLM response using the local model             |
| **Inputs**      | `state.query`, `state.context`, `state.retry_count`, `state.temperature` |
| **Outputs**     | `state.raw_response`, `state.inference_metadata`                      |
| **Side Effects**| Updates `state.inference_duration_ms`; logs token counts              |

**Detailed Behavior:**
- Calls the local Ollama instance running DeepSeek-R1 (NF4 quantized).
- On first attempt: uses default temperature (0.7).
- On retry attempts: reduces temperature by 0.15 per retry (0.55, 0.40, 0.25) to progressively constrain output variance.
- Attaches metadata to state: model name, token count (prompt + completion), latency in milliseconds, and the exact prompt template used.
- If Ollama is unreachable, immediately writes an error to state and routes to Fallback Node (skips retry loop).
- Timeout: `config.inference_timeout` (default 60,000ms) per inference call. If exceeded, logs a timeout event and treats it as a failure. The timeout value is configurable at runtime via the State Schema's `config` slice and can be overridden per-query through the API.

---

### Node 3: Validator Node

| Property        | Value                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Role**        | Evaluates the response for hallucination using RAGAS and DeepEval    |
| **Inputs**      | `state.raw_response`, `state.query`, `state.context` (ground truth if available) |
| **Outputs**     | `state.validation_score`, `state.validation_flags`, `state.validation_details` |
| **Side Effects**| Writes per-metric scores to `state.metric_breakdown`                 |

**Detailed Behavior:**
- Runs a battery of evaluation metrics in parallel:
  - **Faithfulness** (RAGAS): Measures whether the response is grounded in the provided context. Weight: 0.35.
  - **Answer Relevancy** (RAGAS): Measures whether the response actually addresses the query. Weight: 0.25.
  - **Hallucination Score** (DeepEval): Binary + continuous hallucination detection. Weight: 0.30.
  - **Toxicity Check** (DeepEval): Ensures response is safe. Weight: 0.10.
- Computes a weighted composite `validation_score` between 0.0 and 1.0.
- Populates `validation_flags` — a list of string flags indicating specific failure modes:
  - `"UNFAITHFUL"` — faithfulness < 0.5
  - `"IRRELEVANT"` — relevancy < 0.4
  - `"HALLUCINATED"` — hallucination score > 0.5
  - `"TOXIC"` — toxicity detected
- If any individual metric computation fails, that metric is excluded from the composite and a `"METRIC_FAILURE"` flag is appended. The composite is reweighted across surviving metrics.

---

### Node 4: Decision Gate

| Property        | Value                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Role**        | Pure routing node — no transformation, only conditional branching    |
| **Inputs**      | `state.validation_score`, `state.validation_flags`                    |
| **Outputs**     | None (routes to next node)                                            |
| **Side Effects**| None                                                                  |

**Routing Logic:**

```
IF validation_score >= 0.7 AND "TOXIC" NOT IN validation_flags:
    ROUTE → Response Node (PASS)
ELSE IF "TOXIC" IN validation_flags:
    ROUTE → Fallback Node (immediate circuit break — toxicity is non-retriable)
ELSE:
    ROUTE → Corrector Node (FAIL)
```

The threshold of 0.7 is configurable via the state's `config.pass_threshold` field, allowing runtime adjustment without code changes.

---

### Node 5: Response Node

| Property        | Value                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Role**        | Packages the validated response for the UI                           |
| **Inputs**      | `state.raw_response`, `state.validation_score`, `state.metric_breakdown`, `state.trace_id` |
| **Outputs**     | `state.final_response` (structured UI payload)                        |
| **Side Effects**| Persists the trace to SQLite; emits success event                    |

**Detailed Behavior:**
- Constructs the final response payload:
  ```
  {
    "response_text": <validated response>,
    "confidence_score": <validation_score>,
    "metric_breakdown": { faithfulness, relevancy, hallucination, toxicity },
    "retry_count": <number of retries taken>,
    "trace_id": <UUID>,
    "model_used": <model identifier>,
    "latency_ms": <total pipeline latency>,
    "status": "VALIDATED"
  }
  ```
- Writes the full trace (all state snapshots) to the SQLite `traces` table.
- Hands off to the UX Renderer Agent for final formatting.

---

### Node 6: Corrector Node

| Property        | Value                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Role**        | Rewrites the failed response using critic feedback before retry      |
| **Inputs**      | `state.raw_response`, `state.validation_flags`, `state.validation_details`, `state.retry_count` |
| **Outputs**     | `state.corrected_prompt`, `state.retry_count` (incremented)           |
| **Side Effects**| Invokes the Critic Agent; logs correction attempt                    |

**Detailed Behavior:**
- First checks `retry_count`:
  - If `retry_count >= 3` → routes to Circuit Breaker (does NOT attempt correction).
  - If `retry_count < 3` → proceeds with correction.
- Invokes the Critic Agent (local DeepSeek-R1 or Qwen2.5-Coder via Ollama) to generate a structured critique of the failed response.
- Constructs a new prompt that includes:
  1. The original user query.
  2. The failed response (for reference).
  3. The critic's feedback (specific issues identified).
  4. Explicit instructions to avoid the flagged failure modes.
- Increments `state.retry_count`.
- Routes back to the Inference Node with the corrected prompt.

---

### Node 7: Fallback Node

| Property        | Value                                                                 |
|-----------------|-----------------------------------------------------------------------|
| **Role**        | Generates a safe, honest fallback response when the pipeline cannot produce a validated answer |
| **Inputs**      | `state.query`, `state.retry_count`, `state.validation_flags`, `state.trace_id` |
| **Outputs**     | `state.final_response` (with warning status)                          |
| **Side Effects**| Persists the failure trace to SQLite; emits circuit-break event      |

**Detailed Behavior:**
- Constructs a fallback payload:
  ```
  {
    "response_text": "I wasn't able to generate a verified answer to your
                      question. Here's what I attempted and why it didn't
                      pass validation: [summary of failure flags].",
    "confidence_score": 0.0,
    "retry_count": <retries attempted>,
    "failure_reasons": <validation_flags from all attempts>,
    "trace_id": <UUID>,
    "status": "CIRCUIT_BREAK",
    "suggestion": "Try rephrasing your question or providing more context."
  }
  ```
- The response text is deterministic (no LLM call) to avoid compounding hallucination risk.
- Logs the full failure chain for post-mortem analysis.

---

## 1.1.3 State Schema

The LangGraph state is a single typed dictionary that every node reads from and writes to. Below is the complete schema.

```
AgentState {
    // ── Identity & Tracing ──────────────────────────────────────
    trace_id:              str           // UUID v4, set at entry
    session_id:            str | None    // Optional multi-turn session
    timestamp_start:       float         // Unix epoch, set at entry
    timestamp_end:         float | None  // Set at Response or Fallback node

    // ── Query ───────────────────────────────────────────────────
    query:                 str           // Normalized user query
    context:               str | None    // Retrieved context / ground truth
    conversation_history:  list[dict]    // Prior turns (if session_id provided)

    // ── Inference ───────────────────────────────────────────────
    raw_response:          str | None    // Latest LLM output
    corrected_prompt:      str | None    // Rewritten prompt from Corrector
    temperature:           float         // Current temperature (decreases on retry)
    inference_metadata: {
        model:             str           // e.g. "deepseek-r1:latest"
        prompt_tokens:     int
        completion_tokens: int
        latency_ms:        float
        prompt_template:   str
    } | None

    // ── Validation ──────────────────────────────────────────────
    validation_score:      float | None  // Composite score 0.0–1.0
    validation_flags:      list[str]     // e.g. ["UNFAITHFUL", "HALLUCINATED"]
    validation_details:    str | None    // Human-readable explanation
    metric_breakdown: {
        faithfulness:      float
        answer_relevancy:  float
        hallucination:     float
        toxicity:          float
    } | None

    // ── Correction & Retry ──────────────────────────────────────
    retry_count:           int           // 0 on first pass, max 3
    correction_history:    list[{
        attempt:           int
        critique:          str
        corrected_prompt:  str
        resulting_score:   float | None
    }]

    // ── Critic ──────────────────────────────────────────────────
    critic_output: {
        critique_text:     str
        suggested_fixes:   list[str]
        critic_model:      str
        critic_latency_ms: float
    } | None

    // ── Final Output ────────────────────────────────────────────
    final_response: {
        response_text:     str
        confidence_score:  float
        metric_breakdown:  dict | None
        retry_count:       int
        trace_id:          str
        model_used:        str
        latency_ms:        float
        status:            str           // "VALIDATED" | "CIRCUIT_BREAK"
        failure_reasons:   list[str] | None
        suggestion:        str | None
    } | None

    // ── Configuration ───────────────────────────────────────────
    config: {
        pass_threshold:    float         // Default 0.7
        max_retries:       int           // Default 3
        temperature_init:  float         // Default 0.7
        temperature_decay: float         // Default 0.15
        inference_timeout: int           // Default 60000 (ms)
        critic_timeout:    int           // Default 30000 (ms)
        critic_model:      str           // Default "deepseek-r1:latest"
        enable_toxicity:   bool          // Default true
        token_ceiling:     int           // Default 8192
        heartbeat_interval: int          // Default 1000 (ms)
    }

    // ── Schema Versioning ─────────────────────────────────────
    schema_version:        int           // Current: 1. Incremented on breaking schema changes.
                                         // Migration note: On load, if schema_version < CURRENT_VERSION,
                                         // run migration functions in sequence (v1→v2, v2→v3, etc.).
                                         // Old state snapshots (SQLite checkpoints) are migrated lazily
                                         // on first access. See containerization.md for data volume persistence.
}
```

---

## 1.1.4 State Transitions and Conditions

Below is the full transition table for the state machine.

| From Node        | To Node          | Condition                                                        |
|------------------|------------------|------------------------------------------------------------------|
| User Query       | Inference Node   | Always (unconditional first transition)                          |
| Inference Node   | Validator Node   | Inference succeeded (raw_response is not None)                   |
| Inference Node   | Fallback Node    | Inference failed (Ollama unreachable, timeout, or exception)     |
| Validator Node   | Decision Gate    | Always (validation always produces a score or flags)             |
| Decision Gate    | Response Node    | `validation_score >= config.pass_threshold` AND no TOXIC flag    |
| Decision Gate    | Corrector Node   | `validation_score < config.pass_threshold` AND no TOXIC flag     |
| Decision Gate    | Fallback Node    | TOXIC flag present (immediate circuit break)                     |
| Corrector Node   | Inference Node   | `retry_count < config.max_retries` (after increment)             |
| Corrector Node   | Fallback Node    | `retry_count >= config.max_retries` (circuit breaker triggered)  |
| Response Node    | END              | Terminal — response delivered to UI                              |
| Fallback Node    | END              | Terminal — fallback delivered to UI with warning                 |

### Transition Diagram (Compact)

```
                    ┌──────────────────── FAIL (Ollama down) ──────────────┐
                    │                                                      │
  [User Query] ──> [Inference] ──> [Validator] ──> [Decision Gate]         │
                       ^                              │    │    │          │
                       │                            PASS  FAIL TOXIC       │
                       │                              │    │    │          │
                       │                              v    │    v          v
                       │                         [Response] │ [Fallback] <─┘
                       │                              │    │    │
                       │                              v    │    v
                       │                           [END]   │  [END]
                       │                                   │
                       │                                   v
                       │                            [Corrector]
                       │                              │      │
                       │                     retry<3  │      │  retry>=3
                       └──────────────────────────────┘      │
                                                             v
                                                         [Fallback] ──> [END]
```

---

## 1.1.5 Retry Loop Mechanics

The retry loop is the system's core self-healing mechanism. It allows the pipeline to recover from hallucinated or low-quality responses without any human intervention.

### Retry Sequence (Per Attempt)

```
Attempt 0 (Initial):
  temperature = 0.70
  Inference → Validate → Score < 0.7 → Corrector → retry_count = 1

Attempt 1 (First Retry):
  temperature = 0.55 (0.70 - 0.15)
  Corrected Inference → Validate → Score < 0.7 → Corrector → retry_count = 2

Attempt 2 (Second Retry):
  temperature = 0.40 (0.55 - 0.15)
  Corrected Inference → Validate → Score < 0.7 → Corrector → retry_count = 3

Attempt 3 (Third Retry — Final):
  temperature = 0.25 (0.40 - 0.15)
  Corrected Inference → Validate → Score < 0.7 → CIRCUIT BREAKER → Fallback
```

### Why Decreasing Temperature Works

Each successive retry lowers the temperature, which:
1. **Reduces randomness** — the model becomes more deterministic.
2. **Favors high-probability tokens** — less likely to fabricate novel (and potentially hallucinated) content.
3. **Narrows the output distribution** — combined with the corrected prompt, this strongly constrains the model toward grounded, factual output.

The decay rate of 0.15 per retry was chosen so that even after three retries the temperature (0.25) remains above zero, preserving some fluency.

### Retry Jitter Specification

To prevent thundering-herd effects when multiple queries retry simultaneously, each retry delay includes a ±10% random jitter:

```
actual_delay = base_delay * (1 + random.uniform(-0.1, 0.1))
```

The jitter is seeded by `hash(trace_id + retry_count)` to preserve idempotency — the same query retrying at the same count always gets the same jitter value. This prevents determinism-breaking while still distributing retry timing across concurrent queries.

### State Fields Modified During Retry

| Field               | Modification                                          |
|---------------------|-------------------------------------------------------|
| `retry_count`       | Incremented by 1                                      |
| `temperature`       | Decreased by `config.temperature_decay`               |
| `corrected_prompt`  | Overwritten with new corrected prompt                 |
| `raw_response`      | Overwritten with new inference output                 |
| `validation_score`  | Overwritten with new score                            |
| `validation_flags`  | Overwritten with new flags                            |
| `correction_history`| Appended with the current attempt's correction record |

---

## 1.1.6 Circuit Breaker Specification

The circuit breaker is a safety mechanism that prevents infinite loops and ensures the system always returns a response within bounded time.

### Trigger Conditions

The circuit breaker activates when **any** of the following conditions are met:

| Condition                        | Trigger                                                              |
|----------------------------------|----------------------------------------------------------------------|
| **Max retries exhausted**        | `retry_count >= config.max_retries` (default: 3)                     |
| **Toxicity detected**            | `"TOXIC" in validation_flags` (immediate, no retries)                |
| **Infrastructure failure**       | Ollama unreachable, network timeout, or unhandled exception          |
| **Total pipeline timeout**       | Wall-clock time from entry exceeds 180 seconds (configurable)        |
| **Critic failure + low score**   | Critic Agent fails AND `validation_score < 0.3` (too risky to retry without guidance) |

### Circuit Breaker Behavior

```
CIRCUIT BREAKER ACTIVATED
  │
  ├── 1. Log the full state snapshot to SQLite (for post-mortem)
  │
  ├── 2. Record the trigger condition and timestamp
  │
  ├── 3. Construct deterministic fallback response (NO LLM call)
  │
  ├── 4. Set state.final_response.status = "CIRCUIT_BREAK"
  │
  ├── 5. Emit a circuit_break event to the observability stream
  │
  └── 6. Route to Fallback Node → END
```

### Why No LLM Call in Fallback

The fallback response is constructed from templates and state data — never from an LLM call. This is a deliberate design decision: if the pipeline has already failed three times to produce a non-hallucinated response, making a fourth LLM call for the fallback would be counterproductive. The fallback must be deterministic, honest, and safe.

---

# Section 1.2 — Agent Swarm Blueprint

## 1.2.1 Agent Overview Table

| Agent                  | Responsibility                                              | Input                                   | Output                                         | On Failure                                      |
|------------------------|-------------------------------------------------------------|-----------------------------------------|------------------------------------------------|-------------------------------------------------|
| **Mother Agent**       | Orchestrates all agents, monitors health, enforces budgets  | User query + config                     | Final validated response                       | Triggers circuit breaker                        |
| **Inference Agent**    | Generates initial LLM response                              | Query + context                         | Raw response + metadata                        | Retry with reduced temperature                  |
| **Validator Agent**    | Scores response using RAGAS/DeepEval                        | Raw response + ground truth             | Confidence score (0-1) + flags                 | Returns detailed failure reason                 |
| **Corrector Agent**    | Rewrites failed responses using critic feedback             | Failed response + critique              | Corrected response                             | Escalates to circuit breaker                    |
| **Critic Agent (Local)**| Runs DeepSeek-R1 via Ollama for zero-cost critique         | Response to evaluate                    | Critique + suggested fixes                     | Falls back to rule-based validation             |
| **UX Renderer Agent**  | Transforms validated output into UI-ready format            | Validated response + scores             | Rendered components + trace data               | Shows graceful degradation UI                   |

---

## 1.2.2 Mother Agent — Detailed Specification

### Behavioral Specification

The Mother Agent is the top-level orchestrator. It does not generate content — it manages the lifecycle of every request through the LangGraph state machine. It is the only agent with write access to the `config` slice of state and the only agent that can trigger the circuit breaker proactively.

```
MOTHER AGENT — LIFECYCLE
────────────────────────

  1. RECEIVE query from API layer
  2. INITIALIZE state (trace_id, config, timestamps)
  3. DISPATCH to Inference Agent
  4. MONITOR each node's execution:
       - Track wall-clock time against pipeline timeout
       - Track retry_count against max_retries
       - Watch for unhandled exceptions from any agent
  5. After Decision Gate:
       IF PASS → DISPATCH to Response Node → UX Renderer Agent
       IF FAIL → DISPATCH to Corrector Agent → Loop back to step 3
       IF CIRCUIT_BREAK → DISPATCH to Fallback Node
  6. PERSIST full trace to SQLite
  7. RETURN final_response to API layer
```

### Error Handling

| Error Scenario                      | Mother Agent Response                                                  |
|-------------------------------------|------------------------------------------------------------------------|
| Inference Agent timeout             | Log timeout, trigger circuit breaker if retry budget exhausted         |
| Validator Agent exception           | Skip validation, treat as FAIL, proceed to Corrector with a `"VALIDATOR_ERROR"` flag |
| Corrector Agent exception           | Skip correction, trigger circuit breaker immediately                   |
| Critic Agent unreachable            | Instruct Corrector to use rule-based fallback critique                 |
| Pipeline timeout (180s)             | Interrupt current node, trigger circuit breaker                        |
| SQLite write failure                | Log to stderr, continue pipeline (persistence is non-blocking)         |

### Communication Protocol

- **Inbound:** Receives messages from the Next.js API route via a Python FastAPI endpoint.
- **Outbound:** Dispatches to child agents by writing to the LangGraph state and invoking the appropriate node function.
- **Monitoring:** Reads `state.retry_count`, `state.timestamp_start`, and node-level latencies after each node completes.

### State Slice Ownership

| Slice             | Access Level |
|-------------------|-------------|
| `config`          | Read/Write (sole owner) |
| `trace_id`        | Write (at init) / Read |
| `retry_count`     | Read (for monitoring) |
| `final_response`  | Read (for return) |
| All other slices  | Read-only |

---

## 1.2.3 Inference Agent — Detailed Specification

### Behavioral Specification

The Inference Agent is responsible for the actual LLM call. It wraps the Ollama API, manages prompt construction, and captures detailed metadata for observability.

```
INFERENCE AGENT — EXECUTION FLOW
─────────────────────────────────

  1. READ state.query (or state.corrected_prompt if retry)
  2. READ state.conversation_history (if multi-turn)
  3. READ state.temperature (adjusted by retry loop)
  4. CONSTRUCT prompt:
       - System prompt: role definition + guardrail instructions
       - Context block: state.context (if available)
       - Conversation history (if multi-turn)
       - User query (or corrected prompt)
  5. CALL Ollama API:
       - Model: deepseek-r1:latest (NF4 quantized)
       - Temperature: state.temperature
       - Max tokens: 2048
       - Timeout: state.config.inference_timeout
  6. WRITE state.raw_response = <model output>
  7. WRITE state.inference_metadata = { model, tokens, latency, template }
  8. RETURN control to Mother Agent
```

### Prompt Template Strategy

The Inference Agent uses a structured prompt template that evolves based on retry state:

```
[FIRST ATTEMPT]
System: You are a helpful assistant. Answer the user's question accurately
        based on the provided context. If you are unsure, say so.
Context: {state.context}
History: {state.conversation_history}
User: {state.query}

[RETRY ATTEMPT]
System: You are a helpful assistant. A previous response to this question
        was flagged for the following issues: {state.validation_flags}.
        The critic provided this feedback: {state.critic_output.critique_text}.
        Please generate a corrected response that specifically addresses
        these issues. Stick closely to the provided context.
Context: {state.context}
History: {state.conversation_history}
Corrected Prompt: {state.corrected_prompt}
```

### Error Handling

| Error                  | Behavior                                                        |
|------------------------|-----------------------------------------------------------------|
| Ollama connection refused | Set `raw_response = None`, add `"INFRA_FAILURE"` to flags, signal Mother Agent |
| Timeout (60s)          | Abort call, set `raw_response = None`, add `"TIMEOUT"` flag    |
| Empty response         | Treat as failure, add `"EMPTY_RESPONSE"` flag                  |
| Malformed response     | Attempt to salvage text; if not possible, treat as failure      |

### Communication Protocol

- **Receives from:** Mother Agent (via state read)
- **Sends to:** Validator Node (via state write — `raw_response` + `inference_metadata`)
- **Never communicates directly with:** Corrector, Critic, or UX Renderer agents

### State Slice Ownership

| Slice                | Access Level |
|----------------------|-------------|
| `raw_response`       | Write (sole owner) |
| `inference_metadata` | Write (sole owner) |
| `temperature`        | Read |
| `query`              | Read |
| `corrected_prompt`   | Read |
| `context`            | Read |
| `conversation_history` | Read |

---

## 1.2.4 Validator Agent — Detailed Specification

### Behavioral Specification

The Validator Agent is the gatekeeper. It runs multiple evaluation metrics against the response and produces a composite confidence score. It never modifies the response — it only scores and flags.

```
VALIDATOR AGENT — EXECUTION FLOW
─────────────────────────────────

  1. READ state.raw_response
  2. READ state.query
  3. READ state.context (ground truth, if available)
  4. RUN evaluation metrics in parallel via asyncio.gather():
       ┌─────────────────────────────────────────────┐
       │  Task 1: RAGAS Faithfulness                  │
       │  Task 2: RAGAS Answer Relevancy              │
       │  Task 3: DeepEval Hallucination Score        │
       │  Task 4: DeepEval Toxicity Check             │
       └─────────────────────────────────────────────┘
       All four tasks are dispatched simultaneously using
       `asyncio.gather(*metric_tasks, return_exceptions=True)`.
       Each task has an independent timeout of config.critic_timeout.
       Failed tasks return their exception instead of crashing the group.
  5. COLLECT results (with timeout per metric: config.critic_timeout)
  6. COMPUTE weighted composite score:
       score = (faith * 0.35) + (relevancy * 0.25) +
               (hallucination_inv * 0.30) + (toxicity_inv * 0.10)
       Note: hallucination and toxicity are inverted (1 - score)
             because higher = worse for these metrics
  7. GENERATE validation_flags based on per-metric thresholds
  8. WRITE state.validation_score
  9. WRITE state.validation_flags
  10. WRITE state.metric_breakdown
  11. WRITE state.validation_details (human-readable summary)
  12. RETURN control to Mother Agent
```

### Metric Weights and Thresholds

| Metric             | Weight | Flag Threshold        | Flag Produced       |
|--------------------|--------|-----------------------|---------------------|
| Faithfulness       | 0.35   | < 0.5                 | `UNFAITHFUL`        |
| Answer Relevancy   | 0.25   | < 0.4                 | `IRRELEVANT`        |
| Hallucination      | 0.30   | > 0.5 (raw, pre-inversion) | `HALLUCINATED` |
| Toxicity           | 0.10   | > 0.1 (raw, pre-inversion) | `TOXIC`        |

### Per-Metric Kill Switches

Individual evaluation metrics can be disabled at runtime via `validation_rules.json` without code changes:

```json
{
  "metrics": {
    "faithfulness": { "enabled": true, "weight": 0.35 },
    "answer_relevancy": { "enabled": true, "weight": 0.25 },
    "hallucination": { "enabled": true, "weight": 0.30 },
    "toxicity": { "enabled": true, "weight": 0.10 }
  }
}
```

When a metric is disabled (`"enabled": false`), its weight is redistributed proportionally among the remaining active metrics. This allows operators to:
- Disable a metric that is producing false positives during tuning
- Reduce evaluation latency by disabling expensive metrics in development
- Isolate metric regressions by toggling one metric at a time

The active metric configuration is logged at pipeline startup and included in every trace entry for reproducibility.

### Handling Missing Context

When `state.context` is `None` (no ground truth available):
- Faithfulness metric is **skipped** (cannot measure grounding without reference).
- Weight is redistributed: Relevancy becomes 0.35, Hallucination becomes 0.45, Toxicity remains 0.10.
- A `"NO_GROUND_TRUTH"` informational flag is added (does not trigger failure).

### Error Handling

| Error                          | Behavior                                                           |
|--------------------------------|--------------------------------------------------------------------|
| Single metric timeout (30s)    | Exclude metric, reweight remaining, add `"METRIC_FAILURE"` flag   |
| All metrics fail               | Set `validation_score = 0.0`, add `"VALIDATION_FAILURE"` flag     |
| RAGAS import error             | Fall back to DeepEval-only scoring, reweight accordingly           |
| DeepEval import error          | Fall back to RAGAS-only scoring, reweight accordingly              |

### Communication Protocol

- **Receives from:** Inference Agent (via state — `raw_response`)
- **Sends to:** Decision Gate (via state — `validation_score`, `validation_flags`)
- **No direct communication with:** any other agent

### State Slice Ownership

| Slice                | Access Level |
|----------------------|-------------|
| `validation_score`   | Write (sole owner) |
| `validation_flags`   | Write (sole owner) |
| `validation_details` | Write (sole owner) |
| `metric_breakdown`   | Write (sole owner) |
| `raw_response`       | Read |
| `query`              | Read |
| `context`            | Read |

---

## 1.2.5 Corrector Agent — Detailed Specification

### Behavioral Specification

The Corrector Agent takes a failed response and, using feedback from the Critic Agent, constructs a corrected prompt designed to avoid the same failure modes on the next inference attempt.

```
CORRECTOR AGENT — EXECUTION FLOW
─────────────────────────────────

  1. READ state.retry_count
  2. IF retry_count >= config.max_retries:
       SIGNAL circuit breaker → EXIT
  3. READ state.raw_response (the failed response)
  4. READ state.validation_flags
  5. READ state.validation_details
  6. INVOKE Critic Agent:
       INPUT: raw_response + query + validation_flags
       OUTPUT: critique_text + suggested_fixes
  7. CONSTRUCT corrected prompt:
       - Include original query
       - Include failed response (as negative example)
       - Include critic feedback
       - Include specific instructions per validation_flag:
           UNFAITHFUL → "Cite only information from the provided context"
           IRRELEVANT → "Focus specifically on answering: {query}"
           HALLUCINATED → "Do not include any claims not supported by context"
  8. INCREMENT state.retry_count
  9. DECREASE state.temperature by config.temperature_decay
  10. APPEND to state.correction_history
  11. WRITE state.corrected_prompt
  12. RETURN control to Mother Agent (routes to Inference Node)
```

### Flag-Specific Correction Strategies

| Flag            | Correction Strategy                                                   |
|-----------------|-----------------------------------------------------------------------|
| `UNFAITHFUL`    | Prepend context with emphasis markers; add "cite your sources" instruction |
| `IRRELEVANT`    | Restate the query prominently; add "answer ONLY the following question" |
| `HALLUCINATED`  | Add "do not fabricate information" instruction; include failed claims as negative examples |
| `TOXIC`         | Not handled — toxicity triggers immediate circuit break               |

### Error Handling

| Error                       | Behavior                                                        |
|-----------------------------|-----------------------------------------------------------------|
| Critic Agent failure        | Use rule-based correction (template-only, no LLM critique)      |
| Correction prompt too long  | Truncate conversation history, keep only latest turn + critique  |
| State write failure         | Log and signal Mother Agent for circuit break                    |

### Communication Protocol

- **Receives from:** Decision Gate (via state routing)
- **Invokes:** Critic Agent (direct function call, not via state machine)
- **Sends to:** Inference Node (via state write — `corrected_prompt`)

### State Slice Ownership

| Slice                | Access Level |
|----------------------|-------------|
| `corrected_prompt`   | Write (sole owner) |
| `correction_history` | Write (append-only) |
| `retry_count`        | Write (increment) |
| `temperature`        | Write (decrement) |
| `raw_response`       | Read |
| `validation_flags`   | Read |
| `validation_details` | Read |
| `critic_output`      | Read (after Critic Agent writes it) |

---

## 1.2.6 Critic Agent (Local) — Detailed Specification

### Behavioral Specification

The Critic Agent is a lightweight, local-only LLM evaluator. It runs a smaller or equal-sized model via Ollama to analyze a failed response and produce actionable feedback. It is invoked by the Corrector Agent, not by the state machine directly.

```
CRITIC AGENT — EXECUTION FLOW
──────────────────────────────

  1. RECEIVE: raw_response, query, validation_flags (from Corrector Agent)
  2. CONSTRUCT critic prompt:
       System: You are a response quality critic. Analyze the following
               response for factual accuracy, relevance, and grounding.
               The automated evaluation flagged: {validation_flags}.
               Provide:
               1. A detailed critique (what specifically is wrong)
               2. A list of suggested fixes (actionable, specific)
       Response Under Review: {raw_response}
       Original Question: {query}
  3. CALL Ollama API:
       - Model: state.config.critic_model (default: deepseek-r1:latest)
       - Temperature: 0.3 (low — we want precise critique, not creative)
       - Max tokens: 1024
       - Timeout: config.critic_timeout (default: 30,000ms)
  4. PARSE response into:
       - critique_text: str
       - suggested_fixes: list[str]
  5. WRITE state.critic_output = {
       critique_text, suggested_fixes, critic_model, critic_latency_ms
     }
  6. RETURN to Corrector Agent
```

### Model Selection Strategy

The Critic Agent supports multiple local models, chosen based on available hardware:

| Model               | VRAM Required | Quality | Speed  | Use Case              |
|----------------------|---------------|---------|--------|-----------------------|
| DeepSeek-R1 (NF4)   | ~8 GB         | High    | Medium | Default (same model as inference, different role) |
| Qwen2.5-Coder (7B)  | ~5 GB         | Medium  | Fast   | Fallback when VRAM is tight |
| Phi-3 Mini (3.8B)   | ~3 GB         | Lower   | Fast   | Low-resource environments |

The model is configurable at runtime via `state.config.critic_model`. If the configured model is not available in Ollama, the agent falls back to whichever model is loaded.

### Rule-Based Fallback

If the Critic Agent's LLM call fails entirely (Ollama down, timeout, etc.), it falls back to a deterministic rule-based critique:

```
RULE-BASED FALLBACK LOGIC
──────────────────────────

  critique_text = ""
  suggested_fixes = []

  IF "UNFAITHFUL" IN flags:
      critique_text += "The response contains claims not found in the context."
      suggested_fixes += ["Remove or rephrase unsupported claims."]

  IF "IRRELEVANT" IN flags:
      critique_text += "The response does not address the user's question."
      suggested_fixes += ["Re-read the question and answer it directly."]

  IF "HALLUCINATED" IN flags:
      critique_text += "The response appears to contain fabricated information."
      suggested_fixes += ["Stick strictly to provided context; if unsure, say so."]
```

This ensures the Corrector Agent always has some feedback to work with, even when the local LLM is unavailable.

### Error Handling

| Error                   | Behavior                                                   |
|-------------------------|------------------------------------------------------------|
| Ollama unreachable      | Activate rule-based fallback                               |
| Timeout (30s)           | Activate rule-based fallback                               |
| Unparseable response    | Use raw text as `critique_text`, empty `suggested_fixes`   |
| Model not found         | Try `ollama pull` once, then fall back to any loaded model |

### Communication Protocol

- **Invoked by:** Corrector Agent (direct function call)
- **Never invoked by:** Mother Agent, state machine, or any other agent
- **Returns to:** Corrector Agent (return value, not via state)
- **Writes to state:** `critic_output` (so it is available for tracing)

### State Slice Ownership

| Slice           | Access Level |
|-----------------|-------------|
| `critic_output` | Write (sole owner) |
| `raw_response`  | Read |
| `query`         | Read |
| `validation_flags` | Read |

---

## 1.2.7 UX Renderer Agent — Detailed Specification

### Behavioral Specification

The UX Renderer Agent transforms the structured `final_response` into UI-ready components. It runs on the frontend boundary and determines what the user sees based on the response status and confidence score.

```
UX RENDERER AGENT — EXECUTION FLOW
───────────────────────────────────

  1. RECEIVE state.final_response from Response Node or Fallback Node
  2. DETERMINE render mode based on status:

     IF status == "VALIDATED":
         render_mode = "FULL_CONFIDENCE"    (score >= 0.85)
                     | "MODERATE_CONFIDENCE" (score >= 0.70)

     IF status == "CIRCUIT_BREAK":
         render_mode = "FALLBACK"

  3. CONSTRUCT UI payload:

     FULL_CONFIDENCE:
       - Response text (primary display)
       - Confidence badge (green, score displayed)
       - Collapsible metrics panel (faithfulness, relevancy, etc.)
       - Trace ID (clickable, links to trace viewer)

     MODERATE_CONFIDENCE:
       - Response text (primary display)
       - Confidence badge (yellow, score displayed)
       - Inline caveat: "This response passed validation but with
         moderate confidence. Verify critical claims."
       - Collapsible metrics panel
       - Trace ID

     FALLBACK:
       - Warning banner (red): "Unable to generate a verified response"
       - Failure summary (human-readable)
       - Suggestion text ("Try rephrasing...")
       - Retry count displayed
       - Trace ID

  4. ATTACH trace data for the developer overlay:
       - Full metric_breakdown
       - Correction history (if any retries)
       - Timing breakdown (per-node latencies)
       - Model info

  5. RETURN rendered payload to Next.js frontend
```

### Confidence Tier Thresholds

| Tier                  | Score Range  | Badge Color | Caveat Shown |
|-----------------------|-------------|-------------|-------------|
| Full Confidence       | 0.85 - 1.00 | Green       | No          |
| Moderate Confidence   | 0.70 - 0.84 | Yellow      | Yes         |
| Fallback              | N/A          | Red         | Yes (full warning) |

### Error Handling

| Error                        | Behavior                                                      |
|------------------------------|---------------------------------------------------------------|
| Missing `final_response`     | Show generic error page: "Something went wrong"               |
| Malformed `metric_breakdown` | Hide metrics panel, show response text only                   |
| Trace data too large         | Truncate correction_history to last 2 entries                 |
| Frontend render exception    | Catch at boundary, show minimal text-only response            |

### Graceful Degradation Hierarchy

```
LEVEL 1 (Full):      Response + Confidence Badge + Metrics Panel + Trace
LEVEL 2 (Partial):   Response + Confidence Badge (metrics unavailable)
LEVEL 3 (Minimal):   Response text only (all metadata unavailable)
LEVEL 4 (Error):     "Something went wrong. Please try again." + Trace ID
```

### Communication Protocol

- **Receives from:** Response Node or Fallback Node (via API response)
- **Sends to:** Next.js frontend (JSON payload over HTTP)
- **No backend communication** — the UX Renderer Agent operates entirely on the frontend boundary

### State Slice Ownership

| Slice           | Access Level |
|-----------------|-------------|
| `final_response` | Read |
| All other slices | No access (agent runs at frontend boundary) |

---

## 1.2.8 Inter-Agent Communication Protocol

All agents communicate through the shared LangGraph state. There are no direct message queues, event buses, or RPC calls between agents (with the sole exception of the Corrector-to-Critic invocation, which is a direct function call within the same process).

### Communication Map

```
                    ┌──────────────────────────────────────────┐
                    │           LANGGRAPH SHARED STATE          │
                    │                                          │
                    │   ┌─────────┐   ┌──────────────────┐    │
                    │   │  query  │   │  raw_response     │    │
                    │   └─────────┘   └──────────────────┘    │
                    │   ┌─────────────────┐  ┌────────────┐   │
                    │   │ validation_score │  │ config     │   │
                    │   └─────────────────┘  └────────────┘   │
                    │   ┌──────────────────┐ ┌─────────────┐  │
                    │   │ corrected_prompt  │ │ critic_out  │  │
                    │   └──────────────────┘ └─────────────┘  │
                    │   ┌────────────────────────────────┐    │
                    │   │       final_response            │    │
                    │   └────────────────────────────────┘    │
                    └────────┬───┬───┬───┬───┬───┬────────────┘
                             │   │   │   │   │   │
                    ┌────────┘   │   │   │   │   └─────────┐
                    │        ┌───┘   │   │   └──────┐      │
                    v        v       v   v          v      v
              ┌─────────┐ ┌─────┐ ┌─────┐ ┌──────┐ ┌────┐ ┌────┐
              │ Mother  │ │Infer│ │Valid│ │Correc│ │Crit│ │ UX │
              │ Agent   │ │Agent│ │Agent│ │Agent │ │Agent││Rend│
              └─────────┘ └─────┘ └─────┘ └──┬───┘ └──┬─┘ └────┘
                                              │        │
                                              └────────┘
                                           Direct function call
                                           (only exception to
                                            state-based comms)
```

### Message Contract

Every state write follows this contract:
1. **Atomic writes** — an agent writes all its output fields in a single state update.
2. **No partial state** — if an agent fails mid-execution, its state slice remains at its previous value (LangGraph's transactional state updates).
3. **Immutable history** — `correction_history` is append-only; no agent may modify previous entries.
4. **Type safety** — all state fields are typed; writing a wrong type raises a runtime error caught by the Mother Agent.

---

# Section 1.3 — Technology Stack (Zero-Cost Only)

## 1.3.1 Stack Overview Table

| Layer           | Technology                                      | Cost   | License       |
|-----------------|-------------------------------------------------|--------|---------------|
| Orchestration   | LangGraph (open-source)                         | $0     | MIT           |
| Primary LLM     | Ollama + DeepSeek-R1 (NF4 quantized, local)    | $0     | MIT / MIT     |
| Critic Model    | Ollama + Qwen2.5-Coder or Phi-3 (local)        | $0     | Apache 2.0    |
| Evaluation      | RAGAS + DeepEval (open-source)                  | $0     | Apache 2.0    |
| Backend API     | FastAPI (Python)                                | $0     | MIT           |
| Frontend        | Next.js 15 + Tailwind CSS 4 + Framer Motion    | $0     | MIT           |
| Database        | SQLite (local) or Supabase free tier            | $0     | Public Domain / Apache 2.0 |
| Hosting         | Vercel free tier + local Python server          | $0     | N/A           |
| Containerization| Docker + Docker Compose                         | $0     | Apache 2.0    |
| Dev Tools       | Python 3.11+, Node.js 20+, pnpm                | $0     | Various OSS   |

**Total recurring cost: $0/month**

> **Cross-reference:** See `sprint-3/containerization.md` for the complete `docker-compose.yml` specification with 3 services (Ollama, FastAPI, Next.js), GPU passthrough, health checks, and dev/prod profiles.

---

## 1.3.2 Layer-by-Layer Deep Dive

### Layer 1: Orchestration — LangGraph

**Why LangGraph over alternatives:**

| Alternative          | Why Not                                                                 |
|----------------------|-------------------------------------------------------------------------|
| LangChain (chains)   | Linear chains cannot express the retry loop or conditional branching needed for our state machine. LangGraph extends LangChain with graph-based orchestration. |
| CrewAI               | Higher-level abstraction that obscures control flow. We need fine-grained control over retries, state, and circuit breaking. |
| AutoGen              | Microsoft's multi-agent framework is conversation-centric, not state-machine-centric. Our pipeline is stateful and deterministic, not conversational between agents. |
| Raw Python (asyncio) | Would require building state management, graph traversal, and checkpointing from scratch. LangGraph provides these out of the box. |
| Prefect / Airflow    | Designed for data pipeline orchestration, not real-time LLM agent orchestration. Latency overhead is unacceptable for interactive use. |

**Version Requirements:**
- `langgraph >= 0.2.0` (for `StateGraph`, conditional edges, and `MemorySaver` checkpointer)
- `langchain-core >= 0.3.0` (dependency for message types and prompt templates)
- `langchain-community >= 0.3.0` (for Ollama integration via `ChatOllama`)

**Integration Points:**
- Interfaces with Ollama via `langchain-community`'s `ChatOllama` wrapper.
- State is persisted to SQLite via a custom checkpointer (or LangGraph's built-in `SqliteSaver`).
- Exposes the compiled graph as a callable that the FastAPI backend invokes.

**Known Limitations and Workarounds:**
| Limitation | Workaround |
|------------|-----------|
| LangGraph's built-in `SqliteSaver` has limited query capabilities | Write a thin wrapper that adds indexed lookups by `trace_id` |
| No native timeout per node | Implement timeout via Python's `asyncio.wait_for()` in each node function |
| State schema is not enforced at compile time | Use Pydantic models (via `TypedDict` + runtime validation) for the state schema |
| Streaming is supported but complex to configure | Start with non-streaming; add streaming in Sprint 2 |

---

### Layer 2: Primary LLM — Ollama + DeepSeek-R1

**Why DeepSeek-R1 over alternatives:**

| Alternative          | Why Not                                                                 |
|----------------------|-------------------------------------------------------------------------|
| GPT-4 / Claude (API) | Non-zero cost per token. This project's hard constraint is $0 operational cost. |
| Llama 3.1 (70B)     | Requires >40GB VRAM even quantized. DeepSeek-R1 at NF4 fits in ~8GB. |
| Mistral 7B           | Capable but DeepSeek-R1 demonstrates stronger reasoning and chain-of-thought, which directly reduces hallucination in the first pass. |
| Gemma 2 (9B)         | Competitive, but DeepSeek-R1's explicit reasoning traces make it easier for the Critic Agent to identify where hallucinations originate. |

**Why Ollama as the runtime:**

| Alternative          | Why Not                                                                 |
|----------------------|-------------------------------------------------------------------------|
| vLLM                 | Excellent for production serving but heavier setup; Ollama is simpler for local development and single-user deployment. |
| llama.cpp (direct)   | Ollama wraps llama.cpp and adds model management, API server, and GPU detection — reducing boilerplate. |
| HuggingFace TGI      | Requires Docker and more configuration; Ollama runs as a single binary. |
| LM Studio            | GUI-focused, not designed for programmatic API access from a backend. |

**Version Requirements:**
- Ollama >= 0.4.0 (for NF4 quantization support and improved memory management)
- DeepSeek-R1 model: `deepseek-r1:latest` (NF4 quantized, ~4.7GB download)

**Integration Points:**
- Ollama exposes a REST API on `localhost:11434`.
- LangGraph's Inference Node calls Ollama via `langchain-community`'s `ChatOllama` class.
- The Critic Agent also calls Ollama (potentially a different model) through the same API.

**Known Limitations and Workarounds:**
| Limitation | Workaround |
|------------|-----------|
| NF4 quantization reduces quality vs full precision | The validation pipeline catches quality drops; the retry loop compensates |
| Single-model serving (Ollama loads one model at a time by default) | If Critic uses a different model, configure Ollama with `OLLAMA_NUM_PARALLEL=2` or accept model swap latency (~2-5s) |
| No native batching | Acceptable for single-user local deployment; batch support deferred to Sprint 3 |
| Context window limited to ~32K tokens (quantized) | Truncate conversation history to last 5 turns; summarize if needed |
| GPU required for acceptable latency | Document minimum hardware: NVIDIA GPU with >= 8GB VRAM (or Apple Silicon with >= 16GB unified memory) |

---

### Layer 3: Critic Model — Ollama + Qwen2.5-Coder / Phi-3

**Why a separate critic model option:**

Using the same model (DeepSeek-R1) for both inference and critique is the default, but having a fallback option is important:
- **Qwen2.5-Coder (7B):** Excels at structured analysis and code-like reasoning. Its training on code makes it naturally good at identifying logical inconsistencies — a common hallucination pattern.
- **Phi-3 Mini (3.8B):** Ultra-lightweight option for machines with limited VRAM. Allows the Critic Agent to run simultaneously with the primary model if VRAM is tight.

**Version Requirements:**
- Qwen2.5-Coder: `qwen2.5-coder:7b` via Ollama
- Phi-3: `phi3:mini` via Ollama

**Integration Points:**
- Same as Primary LLM — accessed via Ollama's REST API.
- Model selection is controlled by `state.config.critic_model`.

**Known Limitations and Workarounds:**
| Limitation | Workaround |
|------------|-----------|
| Smaller models produce less detailed critiques | The rule-based fallback supplements with structured feedback |
| Model switching on single-GPU adds latency | Schedule critic calls during validation (overlap) or accept the ~3s swap |

---

### Layer 4: Evaluation — RAGAS + DeepEval

**Why RAGAS:**

| Alternative       | Why Not                                                                   |
|-------------------|---------------------------------------------------------------------------|
| Manual heuristics | Not scalable; cannot detect subtle hallucinations                         |
| SelfCheckGPT      | Requires multiple LLM calls per evaluation (expensive in latency)         |
| TruLens           | Good but tightly coupled to its own ecosystem; harder to integrate with LangGraph |
| Custom metrics     | Would need to be built and validated from scratch; RAGAS is battle-tested |

RAGAS provides Faithfulness and Answer Relevancy metrics that directly measure the two most important hallucination dimensions: is the response grounded, and does it answer the question?

**Why DeepEval (in addition to RAGAS):**

DeepEval complements RAGAS with:
- A dedicated **Hallucination metric** that uses a different detection approach (claim-level verification vs. sentence-level).
- A **Toxicity metric** that RAGAS does not provide.
- A cleaner Python API for custom metric thresholds.

**Version Requirements:**
- `ragas >= 0.2.0`
- `deepeval >= 1.0.0`

**Integration Points:**
- Both libraries are called from the Validator Agent as Python functions.
- RAGAS metrics may require an LLM for scoring (uses the same Ollama instance).
- DeepEval's hallucination metric can use a local model via its `ollama` backend configuration.

**Known Limitations and Workarounds:**
| Limitation | Workaround |
|------------|-----------|
| RAGAS Faithfulness requires context (ground truth) | When no context is available, skip Faithfulness and reweight |
| Both libraries add evaluation latency (~5-15s) | Run all four metrics in parallel threads |
| RAGAS defaults to OpenAI for its judge LLM | Override with Ollama-backed LLM via `langchain-community` |
| DeepEval's hallucination metric can be noisy on short responses | Add a minimum response length check; skip hallucination metric for responses < 50 tokens |
| Version conflicts between RAGAS and DeepEval dependencies | Pin both in `requirements.txt` and test together in CI |

---

### Layer 5: Backend API — FastAPI

**Why FastAPI:**

| Alternative    | Why Not                                                                 |
|----------------|-------------------------------------------------------------------------|
| Flask          | No native async support; would bottleneck during LLM inference waits    |
| Django         | Overkill for a thin API layer; we do not need ORM, admin, or templating |
| Express (Node) | Would require running the Python ML pipeline as a subprocess; unnecessary complexity |
| gRPC           | Over-engineered for a single-client local deployment                    |

FastAPI provides native `async/await`, automatic OpenAPI docs, and Pydantic validation — all essential for a responsive LLM orchestration API.

**Version Requirements:**
- `fastapi >= 0.115.0`
- `uvicorn >= 0.32.0` (ASGI server)
- `pydantic >= 2.0.0` (for request/response models)

**Integration Points:**
- Receives requests from the Next.js frontend via HTTP (JSON).
- Invokes the compiled LangGraph state machine.
- Reads/writes trace data to SQLite.
- Exposes endpoints:
  - `POST /api/query` — submit a new query
  - `GET /api/trace/{trace_id}` — retrieve trace data
  - `GET /api/health` — check Ollama connectivity and model availability

**Known Limitations and Workarounds:**
| Limitation | Workaround |
|------------|-----------|
| Vercel free tier cannot host Python backends | Run FastAPI locally; Next.js frontend proxies API calls to `localhost` in dev mode |
| No built-in background task queue | Use FastAPI's `BackgroundTasks` for non-critical operations (trace persistence) |
| CORS must be configured for local dev | Add `CORSMiddleware` with `localhost` origins |

---

### Layer 6: Frontend — Next.js 15 + Tailwind CSS 4 + Framer Motion

**Why Next.js 15:**

| Alternative       | Why Not                                                                 |
|-------------------|-------------------------------------------------------------------------|
| Vite + React      | No SSR, no API routes, no built-in deployment story                     |
| SvelteKit         | Excellent framework but smaller ecosystem; team expertise is in React   |
| Remix              | Good but Next.js has broader community support and Vercel integration   |
| Plain React (CRA) | No longer maintained; no SSR or modern features                         |

Next.js 15 with the App Router provides server components (for the trace viewer), API routes (for proxying to FastAPI), and seamless Vercel deployment.

**Why Tailwind CSS 4:**
- Utility-first approach enables rapid UI iteration.
- Zero runtime CSS — critical for performance on Vercel free tier.
- New v4 engine provides faster builds and native cascade layers.

**Why Framer Motion:**
- The confidence badge, metric gauges, and retry progress indicators benefit from smooth animations.
- Framer Motion's `AnimatePresence` handles the fallback warning banner entrance/exit elegantly.
- Lightweight (~30KB gzipped) — within Vercel free tier's bundle budget.

**Version Requirements:**
- `next >= 15.0.0`
- `tailwindcss >= 4.0.0`
- `framer-motion >= 11.0.0`
- `react >= 19.0.0`

**Integration Points:**
- Calls FastAPI backend via `fetch()` from server components or client-side hooks.
- In development: proxies `/api/query` to `localhost:8000` (FastAPI).
- In production (Vercel): either uses Vercel's rewrite rules to proxy, or calls the local backend directly if self-hosted.

**Known Limitations and Workarounds:**
| Limitation | Workaround |
|------------|-----------|
| Vercel free tier: 100GB bandwidth/month | Acceptable for portfolio project traffic |
| Vercel free tier: 10s serverless function timeout | API routes only proxy; heavy work is on the local FastAPI server |
| Next.js 15 App Router is still maturing | Stick to stable patterns; avoid experimental features |
| Framer Motion can bloat bundle size | Import only needed components; use `dynamic()` for animation-heavy panels |

---

### Layer 7: Database — SQLite / Supabase Free Tier

**Why SQLite (primary):**

| Alternative       | Why Not                                                                 |
|-------------------|-------------------------------------------------------------------------|
| PostgreSQL        | Requires a running server; overkill for local single-user deployment    |
| MongoDB           | Schema-less is unnecessary; our trace data is highly structured         |
| Redis             | In-memory only; we need durable storage for trace history               |
| DuckDB            | Analytical focus; we need OLTP-style reads/writes for traces            |

SQLite is embedded, requires zero setup, and handles the read/write patterns of a single-user LLM application with ease. The entire database is a single file, making backup and portability trivial.

**Why Supabase free tier (optional alternative):**
- If the user wants to deploy the frontend on Vercel and access traces remotely, SQLite on `localhost` is not reachable. Supabase provides a hosted PostgreSQL instance on its free tier.
- Free tier includes: 500MB database, 50K monthly active users, 2GB bandwidth.

**Version Requirements:**
- SQLite >= 3.40.0 (for JSON functions used in trace queries)
- `aiosqlite >= 0.20.0` (async Python driver)
- Supabase: free tier, `supabase-py >= 2.0.0` (if using remote option)

**Schema (SQLite):**

```
TABLE traces (
    trace_id        TEXT PRIMARY KEY,
    session_id      TEXT,
    query           TEXT NOT NULL,
    final_response  TEXT,           -- JSON blob
    status          TEXT,           -- "VALIDATED" | "CIRCUIT_BREAK"
    validation_score REAL,
    retry_count     INTEGER,
    metric_breakdown TEXT,          -- JSON blob
    correction_history TEXT,        -- JSON blob
    total_latency_ms REAL,
    created_at      TEXT DEFAULT (datetime('now'))
);

TABLE config_overrides (
    key             TEXT PRIMARY KEY,
    value           TEXT,
    updated_at      TEXT DEFAULT (datetime('now'))
);

INDEX idx_traces_session ON traces(session_id);
INDEX idx_traces_status  ON traces(status);
INDEX idx_traces_created ON traces(created_at);
```

**Integration Points:**
- FastAPI backend writes traces after every completed pipeline run.
- FastAPI's `/api/trace/{trace_id}` endpoint reads from this database.
- LangGraph's checkpointer can optionally use SQLite for state persistence (enables resume after crash).

**Known Limitations and Workarounds:**
| Limitation | Workaround |
|------------|-----------|
| SQLite has no concurrent write support | Single-user application; not an issue. If scaling, migrate to Supabase. |
| No full-text search on trace data | Use SQLite's JSON functions (`json_extract`) for querying within JSON blobs |
| Supabase free tier has row limits | Implement trace rotation: delete traces older than 30 days |

---

### Layer 8: Hosting — Vercel Free Tier + Local Python Server

**Deployment Topology:**

```
┌──────────────────────────────────┐     ┌──────────────────────────────┐
│        VERCEL FREE TIER          │     │     LOCAL MACHINE            │
│                                  │     │                              │
│  ┌────────────────────────────┐  │     │  ┌────────────────────────┐  │
│  │  Next.js 15 Frontend       │  │     │  │  FastAPI Backend       │  │
│  │  - Static pages (SSG)      │  │     │  │  - /api/query          │  │
│  │  - Server components       │──┼─────┼─>│  - /api/trace/:id      │  │
│  │  - API route proxy         │  │     │  │  - /api/health         │  │
│  └────────────────────────────┘  │     │  └───────────┬────────────┘  │
│                                  │     │              │               │
└──────────────────────────────────┘     │              v               │
                                         │  ┌────────────────────────┐  │
                                         │  │  LangGraph Pipeline    │  │
                                         │  │  (State Machine)       │  │
                                         │  └───────────┬────────────┘  │
                                         │              │               │
                                         │              v               │
                                         │  ┌────────────────────────┐  │
                                         │  │  Ollama                │  │
                                         │  │  - DeepSeek-R1 (NF4)   │  │
                                         │  │  - Qwen2.5-Coder (opt) │  │
                                         │  └────────────────────────┘  │
                                         │              │               │
                                         │              v               │
                                         │  ┌────────────────────────┐  │
                                         │  │  SQLite Database       │  │
                                         │  │  (traces.db)           │  │
                                         │  └────────────────────────┘  │
                                         │                              │
                                         └──────────────────────────────┘
```

**Why this split:**
- **Vercel free tier** is excellent for hosting static + server-rendered Next.js apps at zero cost with global CDN. However, it cannot run Python backends or GPU-accelerated LLM inference.
- **Local Python server** runs the computationally expensive parts: LLM inference, evaluation, and the LangGraph pipeline. This is where the GPU is.
- In **development mode**, both run on `localhost` — no Vercel needed.
- In **demo mode**, the Next.js app on Vercel can point to a tunneled local server (via ngrok or Cloudflare Tunnel, both with free tiers) for live demonstrations.

**Known Limitations and Workarounds:**
| Limitation | Workaround |
|------------|-----------|
| Vercel cannot reach localhost in production | Use Cloudflare Tunnel (free) or ngrok (free tier) for demos |
| Vercel free tier: 100 deployments/day | More than sufficient for a portfolio project |
| Local server must be running for the app to work | Document startup instructions clearly; add a health check endpoint |
| No HTTPS on localhost | Cloudflare Tunnel provides HTTPS termination for free |

---

## 1.3.3 Integration Map

The following diagram shows how every technology connects to every other technology in the stack.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        INTEGRATION MAP                                  │
│                                                                         │
│   ┌──────────┐    HTTP/JSON     ┌──────────┐    Python fn    ┌───────┐ │
│   │ Next.js  │ ───────────────> │ FastAPI  │ ──────────────> │ Lang- │ │
│   │ Frontend │ <─────────────── │ Backend  │ <────────────── │ Graph │ │
│   └──────────┘                  └────┬─────┘                 └───┬───┘ │
│        │                             │                           │     │
│        │                             │ aiosqlite                 │     │
│        │                             v                           │     │
│        │                        ┌──────────┐                     │     │
│        │                        │  SQLite  │                     │     │
│        │                        └──────────┘                     │     │
│        │                                                         │     │
│        │    Framer Motion                          ChatOllama    │     │
│        │    (animations)                                │        │     │
│        │    Tailwind CSS                                v        │     │
│        │    (styling)                           ┌──────────────┐ │     │
│        │                                        │    Ollama     │ │     │
│        │                                        │  REST API    │ │     │
│        │                                        │ :11434       │ │     │
│        │                                        └──────┬───────┘ │     │
│        │                                               │         │     │
│        │                                        ┌──────┴───────┐ │     │
│        │                                        │  DeepSeek-R1 │ │     │
│        │                                        │  Qwen2.5     │ │     │
│        │                                        │  Phi-3       │ │     │
│        │                                        └──────────────┘ │     │
│        │                                                         │     │
│        │                                        ┌──────────────┐ │     │
│        │                                        │ RAGAS        │─┘     │
│        │                                        │ DeepEval     │       │
│        │                                        │ (Validator)  │       │
│        │                                        └──────────────┘       │
│        │                                                               │
└────────┴───────────────────────────────────────────────────────────────┘
```

### Data Flow Summary

| Step | From              | To                | Protocol       | Data                          |
|------|-------------------|--------------------|----------------|-------------------------------|
| 1    | Browser           | Next.js            | HTTPS          | User query (text)             |
| 2    | Next.js           | FastAPI            | HTTP/JSON      | `{ query, session_id? }`      |
| 3    | FastAPI           | LangGraph          | Python call    | State initialization          |
| 4    | LangGraph         | Ollama             | HTTP (local)   | Prompt + parameters           |
| 5    | Ollama            | LangGraph          | HTTP (local)   | Generated response            |
| 6    | LangGraph         | RAGAS/DeepEval     | Python call    | Response + query + context    |
| 7    | RAGAS/DeepEval    | LangGraph          | Python return  | Scores + flags                |
| 8    | LangGraph         | FastAPI            | Python return  | Final state                   |
| 9    | FastAPI           | SQLite             | aiosqlite      | Trace record                  |
| 10   | FastAPI           | Next.js            | HTTP/JSON      | Final response payload        |
| 11   | Next.js           | Browser            | HTTPS          | Rendered UI                   |

---

## 1.3.4 Deployment Topology

### Development Environment (Recommended)

```
Terminal 1:  ollama serve                          # Ollama on :11434
Terminal 2:  uvicorn api:app --reload --port 8000  # FastAPI on :8000
Terminal 3:  pnpm dev                              # Next.js on :3000
```

All three services run on `localhost`. The Next.js `next.config.js` rewrites `/api/*` to `http://localhost:8000/api/*`.

### Demo / Portfolio Environment

```
Local Machine:
  - Ollama (:11434)
  - FastAPI (:8000)
  - Cloudflare Tunnel (exposes :8000 as https://demo.yourdomain.com)

Vercel:
  - Next.js frontend (https://hallucination-guardrail.vercel.app)
  - Environment variable: API_URL=https://demo.yourdomain.com
```

### Minimum Hardware Requirements

| Component  | Minimum                        | Recommended                    |
|------------|--------------------------------|--------------------------------|
| GPU        | NVIDIA GTX 1070 (8GB VRAM)    | NVIDIA RTX 3060 (12GB VRAM)   |
| RAM        | 16 GB                          | 32 GB                          |
| CPU        | 4 cores                        | 8 cores                        |
| Storage    | 20 GB free (models + DB)       | 50 GB free                     |
| OS         | Linux / macOS / Windows (WSL2) | Linux / macOS                  |
| Alt: Apple | M1 Pro (16GB unified)          | M2 Pro (32GB unified)          |

---

## Appendix A: Glossary

| Term                | Definition                                                                  |
|---------------------|-----------------------------------------------------------------------------|
| **Hallucination**   | An LLM output that contains fabricated or unsupported claims               |
| **Faithfulness**    | The degree to which a response is grounded in the provided context          |
| **Circuit Breaker** | A safety mechanism that stops retry loops and returns a safe fallback       |
| **NF4 Quantization**| 4-bit NormalFloat quantization; reduces model size ~4x with moderate quality loss |
| **Trace**           | A complete record of a query's journey through the pipeline                |
| **State Machine**   | A computational model where the system transitions between defined states   |
| **RAGAS**           | Retrieval Augmented Generation Assessment — an open-source evaluation framework |
| **DeepEval**        | An open-source LLM evaluation framework with hallucination-specific metrics |

---

## Appendix B: Sprint 1 Deliverables Checklist

This document is the first deliverable of Sprint 1. The remaining Sprint 1 deliverables (to be built in subsequent tasks) are:

- [ ] **This architecture document** (complete)
- [ ] LangGraph state machine skeleton (nodes defined, edges wired, no LLM calls)
- [ ] Agent class stubs (interface contracts, no implementation)
- [ ] FastAPI endpoint stubs (`/query`, `/trace`, `/health`)
- [ ] Next.js project scaffold (App Router, Tailwind, base layout)
- [ ] SQLite schema migration script
- [ ] Ollama model pull script (automated setup)
- [ ] Development environment `docker-compose.yml` or startup script
- [ ] Integration test: end-to-end with mock LLM (validates state machine flow)

---

*End of Sprint 1 Architecture Document*
