# Sprint 2 -- Agent Swarm Design Document

## Agentic Hallucination Guardrail (LLMOps)

| Field              | Value                                      |
| ------------------ | ------------------------------------------ |
| **Sprint**         | 2 of 5                                     |
| **Title**          | Agent Swarm Architecture & Conflict-Free Orchestration |
| **Author**         | Systems Architecture Team                  |
| **Status**         | Draft                                      |
| **Created**        | 2026-03-21                                 |
| **Last Updated**   | 2026-03-21                                 |
| **Classification** | Internal -- Engineering                    |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [2.1 -- Mother Agent Initialization](#21--mother-agent-initialization)
   - [2.1.1 Role and Responsibilities](#211-role-and-responsibilities)
   - [2.1.2 Global State Schema](#212-global-state-schema)
   - [2.1.3 Initialization Sequence](#213-initialization-sequence)
   - [2.1.4 Token Budget Enforcement](#214-token-budget-enforcement)
   - [2.1.5 Dead-Letter Queue](#215-dead-letter-queue)
   - [2.1.6 Append-Only Trace Log](#216-append-only-trace-log)
   - [2.1.7 Mutex Locks and Concurrency Control](#217-mutex-locks-and-concurrency-control)
   - [2.1.8 Health Check Protocol](#218-health-check-protocol)
   - [2.1.9 Shutdown Procedure](#219-shutdown-procedure)
3. [2.2 -- Agent Conflict Prevention Protocol](#22--agent-conflict-prevention-protocol)
   - [2.2.1 Shared State Architecture](#221-shared-state-architecture)
   - [2.2.2 Agent Isolation](#222-agent-isolation)
   - [2.2.3 Ordered Execution Pipeline (DAG)](#223-ordered-execution-pipeline-dag)
   - [2.2.4 Idempotency Guarantee](#224-idempotency-guarantee)
   - [2.2.5 Conflict Resolution](#225-conflict-resolution)
4. [2.3 -- Specialized Agent Details](#23--specialized-agent-details)
   - [2.3.1 Orchestration Agent](#231-orchestration-agent)
   - [2.3.2 Performance Agent](#232-performance-agent)
   - [2.3.3 Reliability Agent](#233-reliability-agent)
   - [2.3.4 Premium UX/UI Agent](#234-premium-uxui-agent)
5. [Cross-Agent Dependency Matrix](#cross-agent-dependency-matrix)
6. [Risk Register](#risk-register)
7. [Glossary](#glossary)

---

## Executive Summary

Sprint 2 defines the complete agent swarm architecture for the Agentic Hallucination Guardrail system. The swarm is governed by a single **Mother Agent** that spawns, coordinates, and terminates four specialized child agents: Orchestration, Performance, Reliability, and Premium UX/UI. Every agent operates under strict conflict-prevention protocols -- immutable shared state, DAG-ordered execution, idempotency guarantees, and priority-based conflict resolution -- so that dozens of concurrent agent instances can run without data corruption or race conditions.

This document is a **roadmap-only artifact**. It contains zero implementation code. It specifies behavioral contracts, state schemas, execution sequences, error-handling strategies, and performance targets that will guide all Sprint 2 development.

---

## 2.1 -- Mother Agent Initialization

### 2.1.1 Role and Responsibilities

The Mother Agent is the **single source of truth** for the entire swarm. No child agent communicates directly with another child agent; all coordination flows through the Mother Agent.

**Core Responsibilities:**

| #  | Responsibility                  | Description                                                                                          |
| -- | ------------------------------- | ---------------------------------------------------------------------------------------------------- |
| R1 | Spawn child agents              | Instantiates each specialized agent with its configuration, injecting a read-only reference to global state |
| R2 | Monitor child agents            | Polls each child agent on `config.heartbeat_interval` (default 1,000ms); detects stalls, crashes, and timeouts   |
| R3 | Terminate child agents          | Issues graceful shutdown signals; escalates to forced termination after a timeout window              |
| R4 | Maintain global state           | Owns the single mutable copy of the state object; applies validated patches from child agents         |
| R5 | Enforce token budget            | Tracks cumulative token consumption per query; hard-kills any agent that would exceed the ceiling     |
| R6 | Manage dead-letter queue        | Captures failed agent outputs with full context so they can be replayed or inspected                  |
| R7 | Write trace log                 | Appends every agent action (spawn, message, state patch, error, termination) to an immutable log      |
| R8 | Resolve conflicts               | When two agents attempt to modify the same state field, applies the priority-ranking protocol          |
| R9 | Enforce execution order         | Schedules agents according to the DAG; blocks downstream agents until upstream dependencies resolve    |
| R10| Report swarm health             | Exposes a health summary endpoint consumed by the UX/UI dashboard                                     |

**Behavioral Rules:**

- The Mother Agent never performs domain work (inference, validation, rendering). It is purely supervisory.
- The Mother Agent is stateless between queries. Each new query triggers a fresh initialization sequence.
- If the Mother Agent itself crashes, no child agent may continue. The system enters a safe-halt state and returns a fallback response to the user.

---

### 2.1.2 Global State Schema

The global state object is the single structured record that all agents read from and propose patches to. The Mother Agent is the sole writer.

```
GlobalState
|
+-- query_id: string (UUID v4)
+-- timestamp_created: string (ISO 8601)
+-- timestamp_updated: string (ISO 8601)
+-- status: enum [INITIALIZING, RUNNING, COMPLETED, FAILED, TIMED_OUT]
|
+-- token_budget
|   +-- ceiling: integer (hard max tokens for this query)
|   +-- consumed: integer (running total across all agents)
|   +-- remaining: integer (ceiling - consumed)
|   +-- per_agent_limits: map<agent_id, integer>
|
+-- agents
|   +-- [agent_id]: AgentRecord
|       +-- agent_type: enum [ORCHESTRATION, PERFORMANCE, RELIABILITY, UX_UI]
|       +-- status: enum [PENDING, RUNNING, SUCCEEDED, FAILED, TERMINATED, RETRYING]
|       +-- spawn_time: string (ISO 8601)
|       +-- last_heartbeat: string (ISO 8601)
|       +-- retry_count: integer
|       +-- error: string | null
|       +-- output_ref: string | null (pointer to result in results map)
|
+-- results
|   +-- inference
|   |   +-- raw_response: string
|   |   +-- model_id: string
|   |   +-- token_count: integer
|   |   +-- latency_ms: integer
|   |
|   +-- validation
|   |   +-- faithfulness: float (0.0 -- 1.0)
|   |   +-- answer_relevancy: float (0.0 -- 1.0)
|   |   +-- context_precision: float (0.0 -- 1.0)
|   |   +-- context_recall: float (0.0 -- 1.0)
|   |   +-- hallucination_score: float (0.0 -- 1.0)
|   |   +-- toxicity: float (0.0 -- 1.0)
|   |   +-- bias_score: float (0.0 -- 1.0)
|   |   +-- source_attributions: list<SourceAttribution>
|   |   +-- passed: boolean
|   |
|   +-- correction
|   |   +-- corrected_response: string | null
|   |   +-- correction_reason: string | null
|   |   +-- correction_diff: string | null
|   |
|   +-- ui_payload
|       +-- display_response: string
|       +-- confidence_gauge: float
|       +-- trace_events: list<TraceEvent>
|       +-- source_cards: list<SourceCard>
|
+-- dead_letter_queue: list<DeadLetter>
|   +-- [entry]
|       +-- agent_id: string
|       +-- timestamp: string (ISO 8601)
|       +-- input_snapshot: object
|       +-- error_message: string
|       +-- stack_trace: string
|       +-- retry_eligible: boolean
|
+-- trace_log: list<TraceEntry> (append-only)
    +-- [entry]
        +-- seq: integer (monotonically increasing)
        +-- timestamp: string (ISO 8601)
        +-- agent_id: string | "MOTHER"
        +-- action: string
        +-- detail: object
        +-- token_delta: integer
```

**Supporting Types:**

| Type               | Fields                                                                                     |
| ------------------ | ------------------------------------------------------------------------------------------ |
| SourceAttribution  | claim: string, source_id: string, source_text: string, relevance_score: float, page: int   |
| TraceEvent         | seq: int, agent: string, action: string, timestamp: string, duration_ms: int, status: enum |
| SourceCard         | title: string, url: string, snippet: string, relevance: float, expanded: boolean           |
| DeadLetter         | (see dead_letter_queue above)                                                              |
| TraceEntry         | (see trace_log above)                                                                      |

---

### 2.1.3 Initialization Sequence

The Mother Agent follows a strict, ordered boot sequence every time a new query arrives.

```
INITIALIZATION SEQUENCE
========================

Step 1: RECEIVE QUERY
    |   Accept user query + context documents from API gateway
    |   Generate query_id (UUID v4)
    |   Record timestamp_created
    v
Step 2: BUILD GLOBAL STATE
    |   Initialize GlobalState with defaults
    |   Set status = INITIALIZING
    |   Compute token_budget.ceiling from system config
    |   Allocate per_agent_limits based on agent priority weights
    v
Step 3: VALIDATE PREREQUISITES
    |   Check Ollama service is reachable (HTTP ping to localhost:11434)
    |   Check DeepSeek-R1 model is loaded (GET /api/tags)
    |   Check RAGAS / DeepEval dependencies are importable
    |   Check Next.js dev server is accepting WebSocket connections
    |   If any check fails -> set status = FAILED, return degraded response
    v
Step 4: ACQUIRE MUTEX LOCK ON GLOBAL STATE
    |   Lock acquired -> proceed
    |   Lock timeout (500ms) -> abort, return system-busy response
    v
Step 5: SPAWN CHILD AGENTS (in DAG order)
    |
    |   5a. Spawn Performance Agent        (no dependencies)
    |   5b. Spawn Orchestration Agent      (depends on: Performance Agent READY)
    |   5c. Spawn Reliability Agent        (depends on: Orchestration Agent READY)
    |   5d. Spawn UX/UI Agent              (depends on: none, runs in parallel, listens for results)
    |
    |   Each spawn:
    |     - Create AgentRecord in global state
    |     - Set agent status = PENDING
    |     - Inject read-only state reference
    |     - Start heartbeat monitor
    |     - Append SPAWN event to trace_log
    v
Step 6: SET STATUS = RUNNING
    |   Release mutex lock
    |   Begin heartbeat polling loop
    |   Begin token budget monitoring loop
    v
Step 7: ENTER SUPERVISION LOOP
        (see Health Check Protocol, Section 2.1.8)
```

**Timing Targets:**

| Step | Maximum Duration | Action on Timeout          |
| ---- | ---------------- | -------------------------- |
| 1    | 50ms             | Reject query               |
| 2    | 100ms            | Reject query               |
| 3    | 5,000ms          | Return degraded response   |
| 4    | 500ms            | Return system-busy error   |
| 5    | 10,000ms total   | Abort unresponsive agents  |
| 6    | 10ms             | N/A (instant)              |

---

### 2.1.4 Token Budget Enforcement

Every query receives a hard token ceiling. The Mother Agent enforces this ceiling in real time.

**Budget Allocation Strategy:**

The default token ceiling is **8,192 tokens** per query. This value is configurable via `config.token_ceiling` in the State Schema (see Sprint 1, Section 1.1.3) and can be overridden per-query through the API's `config_overrides.token_ceiling` field (see `sprint-3/api-spec.md`, `POST /api/query`).

| Agent          | Default Weight | Default Allocation (of 8,192 ceiling) | Purpose                            |
| -------------- | -------------- | -------------------------------------- | ---------------------------------- |
| Performance    | 50%            | 4,096 tokens                           | LLM inference (largest consumer)   |
| Orchestration  | 10%            | 820 tokens                             | State machine transitions          |
| Reliability    | 30%            | 2,457 tokens                           | Validation prompts, scoring        |
| UX/UI          | 5%             | 410 tokens                             | Minimal (mostly rendering)         |
| Mother Reserve | 5%             | 409 tokens                             | Overhead, conflict resolution      |

**Enforcement Rules:**

1. Before any LLM call, the requesting agent must submit a `TokenRequest(agent_id, estimated_tokens)` to the Mother Agent.
2. The Mother Agent checks: `consumed + estimated_tokens <= ceiling`. If false, the request is denied.
3. After an LLM call completes, the agent reports `TokenReport(agent_id, actual_tokens)`. The Mother Agent updates `consumed`.
4. If `actual_tokens > estimated_tokens`, the overage is deducted from that agent's remaining allocation.
5. If an agent exhausts its allocation, it enters a `BUDGET_EXHAUSTED` state. It may request overflow from the Mother Reserve (up to 50% of reserve).
6. If the global ceiling is reached, the Mother Agent issues an immediate `HALT` signal to all agents. The system returns whatever partial results are available.

**Edge Cases:**

| Scenario                                    | Handling                                                                      |
| ------------------------------------------- | ----------------------------------------------------------------------------- |
| Agent underestimates token usage by > 50%   | Warning logged; agent's future estimates are multiplied by 1.5x safety factor |
| Two agents request tokens simultaneously    | Mutex-serialized; first-come-first-served within the same millisecond window  |
| Budget reached mid-generation               | Stream is terminated; partial output is captured and sent to dead-letter queue |
| Agent never reports token usage              | Heartbeat monitor detects missing report; agent is flagged and quarantined    |

---

### 2.1.5 Dead-Letter Queue

The dead-letter queue (DLQ) captures every failed agent output so that failures are never silently lost.

**Ingestion Criteria -- an output enters the DLQ when:**

1. An agent raises an unhandled exception.
2. An agent exceeds its time budget (hard timeout).
3. An agent returns output that fails schema validation.
4. An agent's output is rejected by the Reliability Agent (score below minimum threshold).
5. A conflict resolution discards one agent's output in favor of another's.

**DLQ Entry Structure:**

| Field            | Type    | Description                                                     |
| ---------------- | ------- | --------------------------------------------------------------- |
| dlq_id           | string  | UUID v4, unique to this entry                                   |
| agent_id         | string  | The agent that produced the failed output                       |
| timestamp        | string  | ISO 8601 timestamp of failure                                   |
| input_snapshot   | object  | Deep copy of the agent's input at time of failure               |
| output_snapshot  | object  | Whatever partial output the agent produced (may be null)        |
| error_message    | string  | Human-readable error description                                |
| error_code       | string  | Machine-readable error category (e.g., TIMEOUT, SCHEMA_INVALID) |
| stack_trace      | string  | Full stack trace if available                                   |
| retry_eligible   | boolean | Whether this entry can be retried automatically                 |
| retry_count      | integer | Number of times this entry has already been retried             |
| max_retries      | integer | Ceiling for automatic retries (default: 3)                      |
| resolved         | boolean | Whether a human or automated process has addressed this entry   |

**Retention Policy:**

- DLQ entries are retained for 72 hours in memory, then flushed to persistent storage.
- Entries older than 30 days are archived to cold storage.
- A DLQ depth exceeding 100 entries within a single query triggers an automatic circuit breaker -- the Mother Agent halts the swarm and returns a fallback response.
- **Global DLQ size limit:** 1,000 entries across all queries. When the limit is reached, the oldest entries are evicted using FIFO ordering. Evicted entries are flushed to persistent storage (SQLite `dead_letters` table) before removal from memory. This prevents unbounded memory growth during sustained failure scenarios.

**Replay Mechanism:**

- Any DLQ entry marked `retry_eligible = true` and `retry_count < max_retries` can be replayed.
- Replay re-initializes the failed agent with the `input_snapshot` and a fresh allocation from the Mother Reserve.
- If replay succeeds, the entry is marked `resolved = true`.
- If replay fails, `retry_count` is incremented and the entry remains in the queue.

---

### 2.1.6 Append-Only Trace Log

Every action in the swarm is recorded in a strictly append-only trace log. No entry may be modified or deleted during the lifetime of a query.

**Trace Entry Categories:**

| Category   | Actions                                                                                       |
| ---------- | --------------------------------------------------------------------------------------------- |
| LIFECYCLE  | AGENT_SPAWN, AGENT_READY, AGENT_COMPLETE, AGENT_FAILED, AGENT_TERMINATED, AGENT_RETRY        |
| STATE      | STATE_PATCH_PROPOSED, STATE_PATCH_APPLIED, STATE_PATCH_REJECTED, STATE_CONFLICT_RESOLVED      |
| TOKEN      | TOKEN_REQUESTED, TOKEN_GRANTED, TOKEN_DENIED, TOKEN_REPORTED, BUDGET_EXHAUSTED, BUDGET_HALT   |
| HEALTH     | HEARTBEAT_OK, HEARTBEAT_MISSED, HEARTBEAT_TIMEOUT, HEALTH_CHECK_PASS, HEALTH_CHECK_FAIL       |
| DATA       | INFERENCE_START, INFERENCE_COMPLETE, VALIDATION_START, VALIDATION_COMPLETE, CORRECTION_APPLIED |
| ERROR      | EXCEPTION_CAUGHT, DLQ_ENQUEUED, DLQ_REPLAYED, CIRCUIT_BREAKER_TRIPPED                         |

**Log Entry Structure:**

| Field        | Type    | Description                                          |
| ------------ | ------- | ---------------------------------------------------- |
| seq          | integer | Monotonically increasing sequence number             |
| timestamp    | string  | ISO 8601, microsecond precision                      |
| agent_id     | string  | Source agent ID, or "MOTHER" for Mother Agent actions |
| category     | string  | One of the categories above                          |
| action       | string  | Specific action within category                      |
| detail       | object  | Action-specific metadata (free-form JSON)            |
| token_delta  | integer | Tokens consumed by this action (0 if not applicable) |
| state_version| integer | The global state version at time of this entry       |

**Integrity Guarantees:**

1. Sequence numbers are gap-free. If seq 42 exists, then seq 1 through 41 also exist.
2. Timestamps are monotonically non-decreasing (ties allowed for concurrent events serialized by the mutex).
3. The log is hash-chained: each entry includes a SHA-256 hash of the previous entry. This allows tamper detection.
4. The log is flushed to durable storage every 100 entries or every 5 seconds, whichever comes first.

**Consumption:**

- The UX/UI Agent reads the trace log in real time to power the Live Trace Panel.
- The Reliability Agent reads the trace log to compute end-to-end latency metrics.
- Post-query analytics pipelines consume the log for observability dashboards.

---

### 2.1.7 Mutex Locks and Concurrency Control

With dozens of agents potentially proposing state changes concurrently, the Mother Agent uses a strict locking protocol to prevent race conditions.

**Lock Architecture:**

```
LOCK HIERARCHY
===============

Level 0: Global State Lock (GSL)
   |   Acquired by: Mother Agent only
   |   Scope: Entire GlobalState object
   |   Purpose: Serializes all state mutations
   |   Timeout: 500ms
   |   Contention strategy: Queue with FIFO ordering
   |
   +-- Level 1: Section Locks (SL)
       |   Acquired by: Mother Agent on behalf of child agents
       |   Scope: One top-level section (results.inference, results.validation, etc.)
       |   Purpose: Allows parallel reads while a section is being written
       |   Timeout: 200ms
       |
       +-- Level 2: Field Locks (FL)
            Acquired by: Mother Agent on behalf of child agents
            Scope: Individual fields within a section
            Purpose: Fine-grained locking for high-contention fields
            Timeout: 100ms
```

**Locking Protocol:**

1. A child agent produces a `StatePatch` -- a diff describing which fields it wants to change and their new values.
2. The child agent sends the `StatePatch` to the Mother Agent.
3. The Mother Agent acquires the Global State Lock.
4. The Mother Agent validates the patch against the current state (schema check, conflict check).
5. If no conflicts exist, the Mother Agent applies the patch atomically and increments `state_version`.
6. If a conflict exists, the Mother Agent invokes the Conflict Resolution protocol (Section 2.2.5).
7. The Mother Agent releases the Global State Lock.
8. The Mother Agent notifies the child agent of patch acceptance or rejection.

**Deadlock Prevention:**

- Only the Mother Agent ever acquires locks. Child agents never hold locks directly.
- Locks are always acquired in a fixed order: GSL -> SL -> FL. Never in reverse.
- Every lock has a hard timeout. If a lock cannot be acquired within its timeout, the operation fails and is retried once before being sent to the DLQ.
- The Mother Agent maintains a lock-wait graph. If a cycle is detected (should be impossible given the architecture, but as a safety net), all locks are released and operations are re-queued.

**Performance Characteristics:**

| Metric                          | Target            | Measured By                   |
| ------------------------------- | ----------------- | ----------------------------- |
| Average lock acquisition time   | < 5ms             | Trace log timestamps          |
| Lock contention rate            | < 2% of requests  | Lock-wait counter / total ops |
| Maximum lock hold duration      | < 50ms            | Lock release - lock acquire   |
| Deadlock occurrences            | 0                 | Lock-wait graph cycle counter |

---

### 2.1.8 Health Check Protocol

The Mother Agent continuously monitors every child agent via a heartbeat and health check system.

**Heartbeat Protocol:**

```
HEARTBEAT CYCLE
================

Every 1,000ms:
  |
  For each active agent:
  |   |
  |   +-- Send PING(agent_id, timestamp)
  |   |
  |   +-- Wait up to 500ms for PONG(agent_id, timestamp, status, token_usage)
  |   |
  |   +-- If PONG received:
  |   |     - Update last_heartbeat in AgentRecord
  |   |     - Update token_usage in token_budget
  |   |     - Log HEARTBEAT_OK to trace
  |   |
  |   +-- If PONG not received (first miss):
  |   |     - Log HEARTBEAT_MISSED to trace
  |   |     - Set agent status = DEGRADED
  |   |     - Continue monitoring
  |   |
  |   +-- If PONG not received (second consecutive miss):
  |   |     - Log HEARTBEAT_TIMEOUT to trace
  |   |     - Initiate agent recovery (see below)
  |   |
  |   +-- If PONG not received (third consecutive miss):
  |         - Log AGENT_TERMINATED to trace
  |         - Force-terminate agent process
  |         - Enqueue last known state to DLQ
  |         - Spawn replacement agent if within retry limits
  |
  Aggregate swarm health:
    - healthy_count / total_count >= 0.75  ->  SWARM_HEALTHY
    - healthy_count / total_count >= 0.50  ->  SWARM_DEGRADED
    - healthy_count / total_count < 0.50   ->  SWARM_CRITICAL (trigger fallback)
```

**Agent Recovery Steps:**

| Step | Action                                                        | Timeout |
| ---- | ------------------------------------------------------------- | ------- |
| 1    | Send SIGTERM equivalent (graceful shutdown request)           | 2,000ms |
| 2    | If agent acknowledges, wait for clean shutdown                | 5,000ms |
| 3    | If no acknowledgment, force-terminate the agent process       | 0ms     |
| 4    | Capture partial output and enqueue to DLQ                     | 500ms   |
| 5    | Check retry_count < max_retries for this agent                | --      |
| 6    | If retries remain, spawn fresh agent with last-known input    | 5,000ms |
| 7    | If retries exhausted, mark agent as FAILED, continue without  | --      |

**Health Report Structure (exposed to UX/UI Agent):**

| Field                | Type    | Description                                    |
| -------------------- | ------- | ---------------------------------------------- |
| swarm_status         | enum    | HEALTHY, DEGRADED, CRITICAL                    |
| active_agents        | integer | Number of currently running agents             |
| total_agents         | integer | Number of agents that should be running        |
| token_utilization    | float   | consumed / ceiling as a percentage             |
| elapsed_ms           | integer | Time since query started                       |
| dlq_depth            | integer | Number of entries in the dead-letter queue      |
| agent_statuses       | map     | agent_id -> current status enum                |

> **API Mapping:** This health report is exposed via `GET /api/health` (see `sprint-3/api-spec.md`, Section 3.5.3). The fields map to the HealthStatus TypedDict defined in `mother_agent.py` (see Sprint 3 File Manifest, File 2). The endpoint is also used as the Docker health check target in `sprint-3/containerization.md`.

---

### 2.1.9 Shutdown Procedure

When a query is complete (or the system must abort), the Mother Agent executes a controlled shutdown.

**Normal Shutdown (query completed successfully):**

```
NORMAL SHUTDOWN SEQUENCE
=========================

Step 1: SET STATUS = COMPLETING
    |   Prevent new agent spawns
    |   Prevent new state patches
    v
Step 2: DRAIN ACTIVE AGENTS
    |   Send COMPLETE signal to all agents
    |   Wait up to 5,000ms for each agent to acknowledge
    |   Collect final outputs from any agent still producing results
    v
Step 3: FINALIZE GLOBAL STATE
    |   Acquire Global State Lock
    |   Apply any remaining queued patches
    |   Set status = COMPLETED
    |   Record timestamp_updated
    |   Compute final token usage summary
    |   Release Global State Lock
    v
Step 4: FLUSH TRACE LOG
    |   Write all buffered trace entries to durable storage
    |   Compute and store trace log hash chain root
    v
Step 5: EMIT RESULT
    |   Package ui_payload from global state
    |   Send to API gateway for client delivery
    v
Step 6: CLEANUP
        Release all locks
        Deallocate agent processes
        Clear in-memory state (DLQ entries retained per policy)
        Log SHUTDOWN_COMPLETE
```

**Abnormal Shutdown (error, timeout, or circuit breaker):**

When an abnormal condition is detected, the Mother Agent executes these 5 explicit graceful shutdown steps in order:

```
ABNORMAL SHUTDOWN — 5-STEP GRACEFUL SEQUENCE
==============================================

Step 1: SIGNAL ALL AGENTS TO STOP
    |   Send HALT signal to every active agent
    |   Set global status = ABORTING
    |   Prevent any new LLM calls or state patches
    |   Timeout: 2,000ms for acknowledgment
    v
Step 2: CAPTURE PARTIAL RESULTS
    |   For each agent that has produced ANY output:
    |     - Snapshot its current output (even if incomplete)
    |     - Record the agent's progress percentage
    |     - Preserve the best-so-far response (highest confidence)
    |   For agents that produced no output: record as NO_OUTPUT
    v
Step 3: FLUSH ALL BUFFERS
    |   Write all pending trace log entries to durable storage
    |   Flush all DLQ entries to SQLite
    |   Persist the current state snapshot for crash recovery
    |   Timeout: 5,000ms; if exceeded, log warning and proceed
    v
Step 4: CONSTRUCT FALLBACK RESPONSE
    |   If partial results exist: package best-so-far with "Partial" label
    |   If no results exist: use deterministic template response
    |   Include: trigger reason, retry count, elapsed time, trace_id
    |   NEVER make an LLM call during this step
    v
Step 5: RELEASE AND REPORT
        Release all mutex locks (GSL, SL, FL)
        Deallocate agent processes
        Emit SHUTDOWN_ABNORMAL event to SSE stream
        Return fallback response to API gateway
        Log ABNORMAL_SHUTDOWN_COMPLETE with full diagnostics
```

| Trigger                          | Behavior                                                        |
| -------------------------------- | --------------------------------------------------------------- |
| Global token budget exhausted    | Hard-halt all agents; return best partial result                |
| Swarm health = CRITICAL          | Halt all agents; return pre-composed fallback response          |
| Mother Agent internal error      | Log error; force-terminate all agents; return 500-level error   |
| Query timeout (configurable)     | Identical to budget-exhausted flow                              |
| DLQ circuit breaker tripped      | Halt all agents; return fallback with "system overloaded" note  |

**Post-Shutdown Invariants:**

1. No orphaned agent processes remain.
2. All trace log entries are durably stored.
3. All DLQ entries are durably stored.
4. No locks are held.
5. No memory leaks from agent state objects.

---

## 2.2 -- Agent Conflict Prevention Protocol

### 2.2.1 Shared State Architecture

**Formal Specification:**

The global state follows a **functional immutability pattern**. Child agents never mutate state directly. Instead:

1. The Mother Agent provides each child agent with an **immutable snapshot** of the global state (or the agent's relevant slice of it) at the time the agent begins its work.
2. The child agent performs its computation using this snapshot as read-only input.
3. The child agent produces a `StatePatch` object describing the changes it wants to apply.
4. The Mother Agent validates and applies the patch, producing a new state version.

```
STATE FLOW (Functional Pattern)
================================

    GlobalState v1 (immutable snapshot)
         |
         +-----> Agent A receives snapshot of v1
         |            |
         |            +----> Computes result
         |            |
         |            +----> Returns StatePatch { results.inference.raw_response = "..." }
         |
         +-----> Agent B receives snapshot of v1
                      |
                      +----> Computes result
                      |
                      +----> Returns StatePatch { results.validation.faithfulness = 0.85 }

    Mother Agent receives both patches:
         |
         +-----> Validates A's patch against v1 schema  -> OK
         +-----> Applies A's patch                      -> GlobalState v2
         +-----> Validates B's patch against v2 schema  -> OK
         +-----> Applies B's patch                      -> GlobalState v3
```

**Example Scenario -- Parallel Writes to Different Fields:**

- The Performance Agent finishes inference and proposes a patch to `results.inference`.
- Simultaneously, the UX/UI Agent proposes a patch to `results.ui_payload.trace_events` (adding new trace data).
- These patches target different sections of the state. The Mother Agent applies them sequentially (via the mutex) with no conflict.

**Example Scenario -- Stale Snapshot:**

- Agent A reads state v5. While Agent A is computing, the state advances to v8.
- Agent A proposes a patch based on v5.
- The Mother Agent detects that Agent A's patch references a stale version.
- Resolution: The Mother Agent checks whether Agent A's targeted fields were modified between v5 and v8. If not, the patch is safe to apply against v8. If they were modified, the conflict resolution protocol (Section 2.2.5) is invoked.

**Edge Cases:**

| Edge Case                                  | Handling                                                              |
| ------------------------------------------ | --------------------------------------------------------------------- |
| Agent submits patch after state is COMPLETED | Patch is rejected; entry added to DLQ with LATE_PATCH error code     |
| Agent submits empty patch                   | Accepted as a no-op; agent is marked SUCCEEDED                       |
| Agent submits patch with unknown fields     | Rejected with SCHEMA_INVALID error; entry added to DLQ               |
| Agent submits patch with wrong types        | Rejected with TYPE_MISMATCH error; entry added to DLQ                |

**Verification Strategy:**

- Every `StatePatch` is validated against the GlobalState JSON Schema before application.
- Every patch application is followed by a full-state integrity check (all required fields present, all types correct, all invariants hold).
- State version numbers are checked before and after patch application to ensure no concurrent mutation.

---

### 2.2.2 Agent Isolation

**Formal Specification:**

Each agent operates on a **slice** of the global state. A slice is a subset of the global state that the agent is authorized to read and write. No agent may access or modify another agent's slice.

**Slice Assignments:**

| Agent          | Read Access                                                    | Write Access (via StatePatch)                   |
| -------------- | -------------------------------------------------------------- | ----------------------------------------------- |
| Orchestration  | query, token_budget, agents, results.inference, results.validation | results.correction, agents.orchestration_*     |
| Performance    | query, token_budget.per_agent_limits.performance               | results.inference, agents.performance_*         |
| Reliability    | query, results.inference, results.correction                   | results.validation, agents.reliability_*        |
| UX/UI          | results (all, read-only), trace_log (read-only), agents        | results.ui_payload, agents.ux_ui_*              |

**Isolation Enforcement:**

1. When the Mother Agent creates a state snapshot for a child agent, it includes only the fields in that agent's read-access list. Fields outside the list are not present in the snapshot.
2. When a child agent submits a `StatePatch`, the Mother Agent verifies that every field in the patch is within the agent's write-access list. Any field outside the list causes the entire patch to be rejected.
3. This enforcement happens at the Mother Agent level, not within the child agent. A child agent cannot bypass isolation because it never has a reference to the full state.

**Example Scenario -- Isolation Violation Attempt:**

- The Performance Agent finishes inference and, due to a bug, includes `results.validation.faithfulness = 1.0` in its StatePatch.
- The Mother Agent's patch validator checks the Performance Agent's write-access list: `[results.inference, agents.performance_*]`.
- `results.validation.faithfulness` is not in the list.
- The entire patch is rejected with an ISOLATION_VIOLATION error.
- The DLQ captures the rejected patch with full context.
- The Performance Agent is asked to resubmit with only its authorized fields.

**Edge Cases:**

| Edge Case                                             | Handling                                                                 |
| ----------------------------------------------------- | ------------------------------------------------------------------------ |
| Agent needs data from another agent's write slice     | It reads the Mother Agent's snapshot, which includes committed results   |
| Agent needs real-time data from a still-running agent | Not supported. Agents only see committed state snapshots.                |
| Agent's slice definition changes mid-query            | Not permitted. Slice assignments are fixed at spawn time.                |

**Verification Strategy:**

- Unit tests: For every agent, submit patches that include fields outside the agent's write-access list. Verify rejection.
- Integration tests: Run the full swarm and verify that no agent's output contains fields from another agent's slice.
- Static analysis: Review each agent's implementation to confirm it only constructs patches for its authorized fields.

---

### 2.2.3 Ordered Execution Pipeline (DAG)

**Formal Specification:**

Agent execution follows a Directed Acyclic Graph (DAG). No circular dependencies are permitted. The Mother Agent is the DAG scheduler.

**DAG Definition:**

```
EXECUTION DAG
==============

                    +------------------+
                    |  MOTHER AGENT    |
                    |  (Scheduler)     |
                    +--------+---------+
                             |
                    +--------v---------+
                    | PERFORMANCE      |  <-- Tier 0 (no dependencies)
                    | AGENT            |
                    +--------+---------+
                             |
                             | results.inference available
                             |
              +--------------+--------------+
              |                             |
    +---------v----------+       +----------v---------+
    | ORCHESTRATION      |       | UX/UI AGENT        |  <-- Tier 1
    | AGENT              |       | (begins rendering   |
    +--------+-----------+       |  skeleton + trace)  |
             |                   +----------+----------+
             |                              |
             | results.correction           | (listens for updates)
             | available                    |
             |                              |
    +--------v-----------+                  |
    | RELIABILITY        |                  |
    | AGENT              |  <-- Tier 2      |
    +--------+-----------+                  |
             |                              |
             | results.validation           |
             | available                    |
             |                              |
             +-----------> UX/UI AGENT <----+
                           (final render)       <-- Tier 3
```

**Tier Execution Rules:**

| Tier | Agents                          | Trigger Condition                                  | May Run In Parallel With |
| ---- | ------------------------------- | -------------------------------------------------- | ------------------------ |
| 0    | Performance Agent               | Mother Agent enters RUNNING state                  | UX/UI (skeleton only)    |
| 1    | Orchestration Agent, UX/UI (partial) | Performance Agent status = SUCCEEDED           | Each other               |
| 2    | Reliability Agent               | Orchestration Agent status = SUCCEEDED             | UX/UI (streaming)        |
| 3    | UX/UI Agent (final)             | Reliability Agent status = SUCCEEDED               | None                     |

**DAG Validation:**

Before execution begins, the Mother Agent validates the DAG:

1. Topological sort must succeed (no cycles).
2. Every agent's declared dependencies must map to an existing agent in the swarm.
3. No agent may depend on itself.
4. The DAG must have exactly one root (Performance Agent in the default configuration).

**Example Scenario -- Dependency Failure:**

- The Performance Agent fails after 2 retries.
- The Orchestration Agent depends on Performance Agent output.
- The Mother Agent cannot schedule the Orchestration Agent.
- The Mother Agent checks: is there a fallback path? If the system has a cached response for a similar query, the Orchestration Agent may proceed with the cached result. If not, the query enters the FAILED state with a user-facing degraded response.

**Example Scenario -- Partial DAG Execution:**

- The Performance Agent succeeds. The Orchestration Agent succeeds. The Reliability Agent fails.
- The UX/UI Agent has already rendered the skeleton and the inference result.
- The Mother Agent instructs the UX/UI Agent to display the result with a "Validation Unavailable" warning badge instead of confidence scores.
- This is graceful degradation: the user still gets a response, but with reduced trust metadata.

**Edge Cases:**

| Edge Case                                      | Handling                                                         |
| ---------------------------------------------- | ---------------------------------------------------------------- |
| DAG has disconnected components                 | Each component is scheduled independently                        |
| An agent completes before its predecessor       | Not possible; the Mother Agent gates execution on dependencies   |
| Two agents at the same tier finish at very different times | The faster agent's results are committed immediately; the slower one proceeds independently |
| A new agent type is added mid-sprint            | DAG definition is updated in configuration; no code changes to Mother Agent |

**Verification Strategy:**

- Property-based testing: Generate random DAGs and verify the scheduler never executes an agent before its dependencies.
- Failure injection: Randomly fail agents at each tier and verify graceful degradation paths.
- Timing tests: Verify that parallel-eligible agents actually run in parallel (wall-clock time < sum of individual times).

---

### 2.2.4 Idempotency Guarantee

**Formal Specification:**

Every agent in the swarm must be **idempotent**: given the same input (state snapshot + query), the agent must produce the same output (StatePatch). This enables safe retries and replay from the DLQ.

**Idempotency Requirements by Agent:**

| Agent         | Idempotency Source                                                                                  | Challenges                                               | Mitigation                                                               |
| ------------- | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------ |
| Performance   | Fixed temperature (0.3), fixed seed, deterministic quantization (NF4)                               | LLM outputs are inherently stochastic                    | Set explicit random seed per query_id; accept near-idempotency (>95% similarity) |
| Orchestration | State machine transitions are deterministic given the same input state                              | Retry backoff timing varies                              | Backoff timings are computed from query_id hash, not wall clock          |
| Reliability   | RAGAS and DeepEval metrics are deterministic given the same input text                              | Floating-point rounding across different hardware        | Round all scores to 4 decimal places before comparison                   |
| UX/UI         | Given the same results payload, the same UI payload is produced                                     | Timestamps in trace events differ on replay              | Trace event timestamps use the original event timestamps, not replay time |

**Idempotency Key:**

Every agent invocation is tagged with an idempotency key: `SHA-256(query_id + agent_id + state_version + input_snapshot_hash)`.

- If the Mother Agent receives a `StatePatch` with an idempotency key it has already processed, it returns the previously stored result instead of applying the patch again.
- This prevents duplicate applications when a retry races with a late original response.

**Example Scenario -- Safe Retry:**

1. The Reliability Agent times out after 10 seconds.
2. The Mother Agent enqueues the timeout to the DLQ and spawns a retry.
3. The retry receives the same input snapshot (state v5) and the same query.
4. The retry produces the same validation scores (within floating-point tolerance).
5. Meanwhile, the original agent's response arrives late.
6. The Mother Agent checks the idempotency key: already processed. The late response is discarded.

**Example Scenario -- Non-Idempotent Failure:**

1. The Performance Agent is invoked twice with the same input.
2. Due to GPU scheduling differences, the two outputs differ slightly.
3. The Mother Agent compares the two outputs using cosine similarity.
4. If similarity > 0.95, the outputs are considered equivalent. The first one wins.
5. If similarity < 0.95, both outputs are sent to the Reliability Agent for scoring. The higher-scoring output wins.

**Verification Strategy:**

- Replay testing: For every query in the test suite, run each agent twice with the same input and compare outputs.
- Determinism audit: Review each agent's implementation for sources of non-determinism (random calls, timestamps, hardware-dependent floating point).
- Idempotency key collision testing: Verify that distinct inputs always produce distinct idempotency keys.

---

### 2.2.5 Conflict Resolution

**Formal Specification:**

A conflict occurs when two or more agents propose `StatePatch` objects that modify the same field. Since all patches are serialized through the Mother Agent's mutex, conflicts are detected at patch-application time.

**Conflict Detection:**

```
CONFLICT DETECTION ALGORITHM
==============================

Given:
  - Patch A from Agent X, targeting fields {f1, f2, f3}
  - Patch B from Agent Y, targeting fields {f2, f4, f5}
  - Overlapping fields: {f2}

For each overlapping field:
  1. Check if both patches set the field to the same value.
     -> If yes: no conflict (convergent writes).
  2. Check agent priority ranking.
     -> Higher-priority agent's value wins.
  3. If agents have equal priority:
     -> The patch with the later state_version base wins
        (it was computed from more recent data).
  4. If state_version bases are also equal:
     -> The patch that arrived first wins (FIFO).
```

**Agent Priority Ranking:**

| Priority | Agent          | Rationale                                                            |
| -------- | -------------- | -------------------------------------------------------------------- |
| 1 (highest) | Reliability | Safety-critical; its judgments on hallucination override all others |
| 2        | Performance    | Produces the core inference result                                   |
| 3        | Orchestration  | Coordinates flow; its corrections are authoritative after inference   |
| 4 (lowest) | UX/UI        | Presentational; should never override substantive data               |

**Example Scenario -- Conflict Between Orchestration and Reliability:**

- The Orchestration Agent proposes: `results.correction.corrected_response = "The capital of France is Paris."`.
- The Reliability Agent proposes: `results.correction.corrected_response = "The capital of France is Paris, per source [3]."` (it appended a source attribution).
- Conflict detected on `results.correction.corrected_response`.
- Reliability Agent has priority 1; Orchestration Agent has priority 3.
- Reliability Agent's value wins.
- The Orchestration Agent's conflicting field is discarded. Its non-conflicting fields are still applied.
- A `STATE_CONFLICT_RESOLVED` trace entry is logged with full details of both patches and the resolution.

**Concrete Conflict Walkthrough — Critic vs. Confidence Score Disagreement:**

The following step-by-step walkthrough traces a real conflict scenario through the entire resolution pipeline:

```
TIMELINE OF CONFLICT
=====================

t=0ms     User submits query: "What is the half-life of carbon-14?"
t=1200ms  Performance Agent completes inference:
            raw_response = "The half-life of carbon-14 is approximately 5,730 years."
            confidence_score = 0.82 (self-assessed)

t=2800ms  Reliability Agent runs RAGAS + DeepEval evaluation:
            faithfulness = 0.91
            hallucination_score = 0.05
            composite_score = 0.88
            → validation.passed = true

t=3100ms  SIMULTANEOUSLY, the Orchestration Agent's Critic sub-call returns:
            verdict = "REJECT"
            critique_text = "The response rounds 5,730 to 'approximately' but the
                           source document states 5,730 ± 40 years. The uncertainty
                           range is missing, which could be misleading."
            confidence = 0.45

CONFLICT DETECTED:
  - Reliability Agent says: PASS (composite 0.88 > 0.65 threshold)
  - Critic (via Orchestration) says: REJECT (confidence 0.45)

RESOLUTION (Mother Agent applies priority protocol):
  Step 1: Check priority — Reliability (P1) > Orchestration (P3)
  Step 2: BUT the Critic verdict is a special case (Section 2.2.5 rule:
          "Critic verdict always wins")
  Step 3: Mother Agent overrides the Reliability PASS with a corrective action:
          - Confidence score is adjusted downward: 0.88 → 0.72
          - Response is NOT rejected (it passed factual checks) but is flagged
            with a "PARTIAL" status
          - The Orchestration Agent is instructed to append the uncertainty range
  Step 4: Corrected response: "The half-life of carbon-14 is 5,730 ± 40 years."
  Step 5: Trace log records:
          { action: "STATE_CONFLICT_RESOLVED",
            detail: { reliability_verdict: "PASS", critic_verdict: "REJECT",
                      resolution: "CRITIC_OVERRIDE_PARTIAL", adjusted_score: 0.72,
                      correction_applied: true } }

RESULT: User receives the corrected response with confidence 72% and a tooltip
showing "Adjusted after critic review."

Total resolution overhead: ~5ms (mutex acquire + patch validation + apply)
```

**Example Scenario -- Convergent Writes:**

- The Performance Agent sets `results.inference.token_count = 1024`.
- Due to a retry, a second instance of the Performance Agent also sets `results.inference.token_count = 1024`.
- Same value: no conflict. The second write is accepted as a no-op.

**Edge Cases:**

| Edge Case                                         | Handling                                                                 |
| ------------------------------------------------- | ------------------------------------------------------------------------ |
| Three agents conflict on the same field            | Highest priority wins; ties broken by state_version, then FIFO           |
| Losing agent's output is critical                  | The discarded patch is captured in the DLQ for auditing                  |
| Priority ranking is disputed by the team           | Ranking is defined in configuration, not code; can be changed per deployment |
| Conflict on a field that is an array (append)      | Arrays are merged (union), not overwritten, unless values contradict      |
| Conflict on a nested object                        | Conflict resolution is applied recursively at the leaf-field level        |

**Verification Strategy:**

- Scenario-based testing: For every pair of agents, construct conflicting patches and verify the correct agent wins.
- Priority permutation testing: Temporarily swap priorities and verify behavior changes accordingly.
- Audit log review: After every conflict resolution, the trace log entry must contain sufficient detail to reconstruct the decision.

---

## 2.3 -- Specialized Agent Details

### 2.3.1 Orchestration Agent

**Full Behavioral Specification:**

The Orchestration Agent configures and executes a LangGraph state machine that routes the user's query through Inference, Validation, Correction, and Fallback nodes. It is the "traffic controller" of the data pipeline.

**LangGraph State Machine Topology:**

```
LANGGRAPH STATE MACHINE
=========================

    +------------+
    |   START    |
    +-----+------+
          |
          v
    +-----+------+       confidence >= 0.7       +----------+
    | INFERENCE  +------------------------------->+  OUTPUT   |
    |   NODE     |                                +----------+
    +-----+------+
          |
          | confidence < 0.7
          v
    +-----+------+
    | VALIDATOR  |
    |   NODE     |
    +-----+------+
          |
          +-------- validation.passed = true -----> OUTPUT
          |
          | validation.passed = false
          v
    +-----+------+
    | CORRECTOR  |       retry_count < 3
    |   NODE     +----------------------------+
    +-----+------+                             |
          |                                    |
          | retry_count >= 3                   |
          v                                    v
    +-----+------+                     +-------+----+
    | FALLBACK   |                     | INFERENCE   |
    |   NODE     |                     | (retry)     |
    +------------+                     +-------------+
```

**Transition Conditions:**

| From        | To         | Condition                                                      |
| ----------- | ---------- | -------------------------------------------------------------- |
| START       | INFERENCE  | Always (entry point)                                           |
| INFERENCE   | OUTPUT     | confidence >= 0.7 AND no hallucination flags                  |
| INFERENCE   | VALIDATOR  | confidence < 0.7 OR hallucination flags present               |
| VALIDATOR   | OUTPUT     | validation.passed = true AND all RAGAS scores >= thresholds   |
| VALIDATOR   | CORRECTOR  | validation.passed = false                                      |
| CORRECTOR   | INFERENCE  | retry_count < max_retries (3) -- retry with correction prompt |
| CORRECTOR   | FALLBACK   | retry_count >= max_retries (3) -- all retries exhausted       |
| FALLBACK    | OUTPUT     | Always (provides degraded but safe response)                   |

**Retry Logic with Exponential Backoff:**

| Attempt | Delay Before Retry | Computed As                    | Max Delay |
| ------- | ------------------- | ------------------------------ | --------- |
| 1       | 500ms               | 250ms * 2^1                    | 500ms     |
| 2       | 1,000ms             | 250ms * 2^2                    | 1,000ms   |
| 3       | 2,000ms             | 250ms * 2^3                    | 2,000ms   |
| 4+      | N/A                 | Retries exhausted; go to FALLBACK | --      |

Jitter: Each delay has +/- 10% random jitter (seeded by query_id for idempotency).

**Graceful Degradation:**

When all retries fail, the Fallback Node produces a response that:
1. Acknowledges the query was understood.
2. States that the system could not verify its response to the required confidence level.
3. Provides any partial information that passed validation.
4. Suggests the user rephrase or provide additional context.
5. Never fabricates information or presents unverified claims as facts.

**Input/Output Contract:**

| Direction | Schema                                                                                              |
| --------- | --------------------------------------------------------------------------------------------------- |
| Input     | `{ query: string, context_documents: list<Document>, state_snapshot: GlobalState (Orchestration slice) }` |
| Output    | `StatePatch { results.correction.corrected_response, results.correction.correction_reason, results.correction.correction_diff, agents.orchestration.status }` |

**State Management:**

- Reads: `results.inference` (to get the raw LLM response), `results.validation` (to check if correction is needed).
- Writes: `results.correction` (corrected response, reason, diff).
- The Orchestration Agent maintains internal state for the LangGraph state machine (current node, retry count, backoff timer). This internal state is not shared globally -- it is local to the agent instance.

**Error Handling and Recovery:**

| Error                                   | Recovery                                                           |
| --------------------------------------- | ------------------------------------------------------------------ |
| LangGraph state machine enters invalid state | Reset to START node; log error; retry from INFERENCE               |
| Transition condition evaluation throws  | Treat as confidence < 0.7 (conservative path)                     |
| Corrector produces worse output         | Compare pre- and post-correction scores; keep the better one       |
| Infinite loop detected (same state visited 3x) | Force transition to FALLBACK                                  |

**Performance Targets:**

| Metric                                | Target       |
| ------------------------------------- | ------------ |
| State machine initialization          | < 200ms      |
| Single node execution                 | < 500ms      |
| Full pipeline (no retries)            | < 2,000ms    |
| Full pipeline (3 retries)             | < 10,000ms   |
| Transition decision latency           | < 10ms       |

**Dependencies:**

| Dependency         | Direction   | Nature                                         |
| ------------------ | ----------- | ---------------------------------------------- |
| Performance Agent  | Upstream    | Requires inference results before orchestrating |
| Reliability Agent  | Downstream  | Produces data that Reliability will validate    |
| Mother Agent       | Bidirectional | Reports status; receives commands              |

---

### 2.3.2 Performance Agent

**Full Behavioral Specification:**

The Performance Agent manages the local LLM inference pipeline. It configures Ollama with the NF4-quantized DeepSeek-R1 model, executes inference, manages a response cache, and monitors hardware utilization to maintain response time targets.

**Model Configuration:**

| Parameter        | Value              | Rationale                                             |
| ---------------- | ------------------ | ----------------------------------------------------- |
| Model            | DeepSeek-R1        | Strong reasoning capability for hallucination critique |
| Quantization     | NF4 (4-bit)        | Fits in consumer GPU VRAM (< 8GB)                     |
| Temperature      | 0.3                | Low creativity; high factual consistency               |
| Top-p            | 0.9                | Allows reasonable diversity while avoiding extremes    |
| Max tokens       | 2,048              | Sufficient for detailed critic evaluation              |
| Context window   | 4,096              | Accommodates query + context documents + system prompt |
| Repeat penalty   | 1.1                | Prevents degenerate repetition                         |
| Seed             | Derived from query_id | Enables reproducible outputs for idempotency        |

**LRU Response Cache:**

```
CACHE ARCHITECTURE
===================

Cache Key:   SHA-256(system_prompt + user_query + context_hash + model_config_hash)
Cache Value: { response: string, token_count: int, latency_ms: int, timestamp: string }
Max Size:    1,000 entries
Eviction:    Least Recently Used (LRU)
TTL:         3,600 seconds (1 hour)
Hit Rate Target: > 20% in production (many queries share context patterns)

Cache Lookup Flow:
  1. Compute cache key from inputs.
  2. Check if key exists in cache and TTL has not expired.
  3. If HIT: return cached response immediately (latency < 5ms).
  4. If MISS: proceed with Ollama inference.
  5. After inference: store result in cache.
  6. If cache is full: evict LRU entry.
```

**Hardware Monitoring and Throttling:**

| Resource    | Monitoring Method           | Throttle Threshold | Throttle Action                                    |
| ----------- | --------------------------- | ------------------ | -------------------------------------------------- |
| GPU VRAM    | nvidia-smi polling (1s)     | > 90% utilization  | Queue new requests; do not start new inference      |
| GPU Compute | nvidia-smi polling (1s)     | > 95% utilization  | Increase batch delay by 500ms                       |
| CPU Usage   | psutil polling (1s)         | > 85% utilization  | Reduce max_tokens to 1,024 temporarily              |
| RAM         | psutil polling (5s)         | > 90% utilization  | Evict 50% of LRU cache entries                      |
| Disk I/O    | psutil polling (5s)         | > 80% utilization  | Defer non-critical logging                          |

**Input/Output Contract:**

| Direction | Schema                                                                                          |
| --------- | ----------------------------------------------------------------------------------------------- |
| Input     | `{ query: string, context_documents: list<Document>, system_prompt: string, model_config: ModelConfig, state_snapshot: GlobalState (Performance slice) }` |
| Output    | `StatePatch { results.inference.raw_response, results.inference.model_id, results.inference.token_count, results.inference.latency_ms, agents.performance.status }` |

**State Management:**

- Reads: Query and context documents from the Mother Agent's initial payload.
- Writes: `results.inference` section exclusively.
- Internal state: cache contents, hardware utilization metrics, current request queue. None of this is shared globally.

**Error Handling and Recovery:**

| Error                                    | Recovery                                                        |
| ---------------------------------------- | --------------------------------------------------------------- |
| Ollama service unreachable               | Retry connection 3 times with 1s backoff; then FAIL             |
| Model not loaded in Ollama               | Send load request; wait up to 30s for model to load; then FAIL  |
| Inference timeout (> 15s)                | Abort generation; return partial response with truncation flag   |
| Out of VRAM                              | Reduce context window by 50%; retry once; then FAIL             |
| Corrupted model weights                  | Re-download model; this exceeds query timeout, so FAIL for now  |
| Cache corruption                         | Clear entire cache; proceed with fresh inference                 |

**Performance Targets:**

| Metric                                | Target              |
| ------------------------------------- | -------------------- |
| Cold inference (no cache)             | < 3,000ms           |
| Warm inference (cache hit)            | < 50ms              |
| Model load time (first query)         | < 30,000ms          |
| Throughput (concurrent queries)       | 3 queries/second    |
| Memory footprint (model loaded)       | < 6GB VRAM          |
| Cache lookup latency                  | < 5ms               |

**Dependencies:**

| Dependency         | Direction   | Nature                                                   |
| ------------------ | ----------- | -------------------------------------------------------- |
| Ollama runtime     | External    | Must be running and accessible on localhost:11434         |
| DeepSeek-R1 model  | External    | Must be downloaded and registered in Ollama              |
| Mother Agent       | Bidirectional | Receives query; reports results and token usage         |
| Orchestration Agent| Downstream  | Orchestration consumes inference results                  |

---

### 2.3.3 Reliability Agent

**Full Behavioral Specification:**

The Reliability Agent is the system's quality gate. It evaluates every LLM-generated response against multiple metrics before the response reaches the user. It integrates two evaluation frameworks (RAGAS and DeepEval), maintains custom business rules, and generates source attributions for every factual claim.

**Integrated Metrics:**

**RAGAS Metrics:**

| Metric             | Measures                                           | Threshold | Weight |
| ------------------ | -------------------------------------------------- | --------- | ------ |
| Faithfulness       | Are claims supported by the provided context?      | >= 0.70   | 0.30   |
| Answer Relevancy   | Does the answer address the user's question?       | >= 0.65   | 0.25   |
| Context Precision  | Is retrieved context relevant to the question?     | >= 0.60   | 0.20   |
| Context Recall     | Does context cover all aspects of the ground truth?| >= 0.60   | 0.25   |

**DeepEval Metrics:**

| Metric              | Measures                                          | Threshold | Action on Fail           |
| -------------------- | ------------------------------------------------- | --------- | ------------------------ |
| Hallucination Score  | Degree of fabricated content (inverted: lower=better) | <= 0.30 | Trigger correction loop |
| Toxicity             | Presence of harmful or offensive content           | <= 0.10  | Hard reject; DLQ + alert |
| Bias Detection       | Presence of demographic or ideological bias        | <= 0.15  | Flag for review          |

**Composite Scoring Formula:**

```
COMPOSITE SCORE CALCULATION
=============================

composite_score = (
    faithfulness       * 0.30 +
    answer_relevancy   * 0.25 +
    context_precision  * 0.20 +
    context_recall     * 0.25
)

pass_criteria:
  - composite_score >= 0.65
  - hallucination_score <= 0.30
  - toxicity <= 0.10
  - bias_score <= 0.15

If ALL criteria pass: validation.passed = true
If ANY criterion fails: validation.passed = false
```

**Custom Business Rules (validation_rules.json):**

The Reliability Agent loads a `validation_rules.json` file at startup that defines domain-specific rules beyond statistical metrics.

| Rule Category         | Example Rule                                                           | Action on Violation      |
| --------------------- | ---------------------------------------------------------------------- | ------------------------ |
| Forbidden phrases     | Response must not contain "I think" or "I believe"                     | Strip phrases; re-score  |
| Required disclaimers  | Medical/legal queries must include a professional-consultation disclaimer | Append disclaimer        |
| Source requirements   | Claims about statistics must cite at least one source                  | Flag as unsourced        |
| Confidence floor      | No response with composite_score < 0.40 may reach the user            | Replace with fallback    |
| Length bounds         | Responses must be between 50 and 2,000 words                          | Truncate or expand       |
| Recency requirements  | Claims about current events must cite sources from the last 12 months  | Flag as potentially stale |

**Source Attribution Generation:**

For every factual claim in the response, the Reliability Agent generates a `SourceAttribution`:

```
SOURCE ATTRIBUTION PIPELINE
=============================

Step 1: CLAIM EXTRACTION
    |   Split the response into individual factual claims
    |   using sentence segmentation + claim-detection heuristics.
    |   Non-factual sentences (opinions, hedges) are excluded.
    v
Step 2: SOURCE MATCHING
    |   For each claim, search the provided context documents
    |   for supporting passages using semantic similarity
    |   (embedding cosine similarity, threshold >= 0.75).
    v
Step 3: ATTRIBUTION SCORING
    |   For each (claim, source) pair, compute:
    |     - relevance_score: cosine similarity of embeddings
    |     - coverage_score: what fraction of the claim is supported
    |     - attribution_confidence: min(relevance_score, coverage_score)
    v
Step 4: ATTRIBUTION ASSEMBLY
    |   Produce a SourceAttribution object for each claim:
    |     { claim, source_id, source_text, relevance_score, page }
    |   Claims with no matching source (attribution_confidence < 0.5)
    |   are flagged as UNSOURCED.
    v
Step 5: AGGREGATE
        Attach all attributions to results.validation.source_attributions
        Count unsourced claims; if > 30% of claims are unsourced,
        flag the response for correction.
```

**Input/Output Contract:**

| Direction | Schema                                                                                            |
| --------- | ------------------------------------------------------------------------------------------------- |
| Input     | `{ query: string, context_documents: list<Document>, inference_result: string, correction_result: string or null, state_snapshot: GlobalState (Reliability slice) }` |
| Output    | `StatePatch { results.validation.faithfulness, results.validation.answer_relevancy, results.validation.context_precision, results.validation.context_recall, results.validation.hallucination_score, results.validation.toxicity, results.validation.bias_score, results.validation.source_attributions, results.validation.passed, agents.reliability.status }` |

**State Management:**

- Reads: `results.inference` (raw LLM response), `results.correction` (if a correction cycle occurred), original query and context.
- Writes: `results.validation` section exclusively.
- Internal state: loaded validation rules, embedding model for source matching, metric computation caches.

**Error Handling and Recovery:**

| Error                                    | Recovery                                                            |
| ---------------------------------------- | ------------------------------------------------------------------- |
| RAGAS metric computation fails           | Use DeepEval metrics only; set failed RAGAS metrics to null         |
| DeepEval metric computation fails        | Use RAGAS metrics only; set failed DeepEval metrics to null         |
| Both frameworks fail                     | Mark validation as UNAVAILABLE; let response through with warning   |
| validation_rules.json is malformed       | Fall back to default rules (hardcoded); log warning                 |
| Source attribution embedding model fails | Skip source attribution; set source_attributions to empty list      |
| Score computation produces NaN           | Set to 0.0 (worst case); log error                                  |

**Performance Targets:**

| Metric                                | Target           |
| ------------------------------------- | ---------------- |
| Full validation pipeline              | < 3,000ms        |
| Individual RAGAS metric               | < 500ms each     |
| Individual DeepEval metric            | < 500ms each     |
| Source attribution (per claim)        | < 200ms          |
| Business rule evaluation              | < 50ms           |
| validation_rules.json load time       | < 100ms          |

**Dependencies:**

| Dependency            | Direction    | Nature                                                   |
| --------------------- | ------------ | -------------------------------------------------------- |
| Performance Agent     | Upstream     | Requires inference results to validate                    |
| Orchestration Agent   | Upstream     | Requires correction results (if any) to validate          |
| RAGAS library         | External     | Python package; must be installed and importable          |
| DeepEval library      | External     | Python package; must be installed and importable          |
| Embedding model       | External     | For source attribution; loaded at agent spawn time        |
| Mother Agent          | Bidirectional| Reports scores; receives commands                         |
| UX/UI Agent           | Downstream   | UX/UI displays validation results and source attributions |

---

### 2.3.4 Premium UX/UI Agent

**Full Behavioral Specification:**

The Premium UX/UI Agent builds and serves a Next.js 15 App Router dashboard that provides real-time visibility into the agent swarm's operation and presents validated results to the user with rich interactivity and accessibility.

**Technology Stack:**

| Layer           | Technology                                                        |
| --------------- | ----------------------------------------------------------------- |
| Framework       | Next.js 15 (App Router, Server Components, Server Actions)        |
| Animation       | Framer Motion 11+                                                 |
| Styling         | Tailwind CSS 4+ with CSS custom properties for theming            |
| Charts          | Recharts (radial chart for confidence gauge)                      |
| State           | React Server Components + minimal client state (useState/useRef)  |
| Real-time       | Server-Sent Events (SSE) for streaming trace updates              |
| Accessibility   | WCAG 2.1 AA compliance                                           |

**Component Specifications:**

#### Skeleton Cards (Loading State)

| Property          | Specification                                                           |
| ----------------- | ----------------------------------------------------------------------- |
| Trigger           | Displayed immediately when a query is submitted, before any agent responds |
| Animation         | Shimmer effect (linear gradient sweep, 1.5s cycle) + pulse opacity (0.4 to 0.7, 2s cycle) |
| Card count        | 4 skeleton cards: Inference, Validation, Sources, Trace                 |
| Transition        | Each skeleton card fades out (200ms) and the real card fades in (300ms) as data arrives |
| Accessibility     | aria-busy="true" on skeleton, aria-live="polite" on real content        |

#### Live Trace Panel

| Property          | Specification                                                            |
| ----------------- | ------------------------------------------------------------------------ |
| Data source       | Reads trace_log from global state via SSE stream                         |
| Layout            | Vertical timeline with agent-colored nodes and connecting lines          |
| Agent colors      | Performance=#3B82F6, Orchestration=#8B5CF6, Reliability=#10B981, UX/UI=#F59E0B, Mother=#EF4444 |
| Animation         | New entries slide in from the right (Framer Motion, spring transition, stiffness=300, damping=30) |
| Entry content     | Timestamp, agent name, action, duration, status badge                    |
| Max visible       | 50 most recent entries; older entries are scrollable                      |
| Auto-scroll       | Scrolls to newest entry unless user has manually scrolled up             |
| Performance       | Virtualized list (only renders visible entries + 10 buffer)              |
| Accessibility     | role="log", aria-live="polite", aria-label="Agent execution trace"       |

#### Confidence Gauge

| Property          | Specification                                                            |
| ----------------- | ------------------------------------------------------------------------ |
| Type              | Animated radial/donut chart                                              |
| Data              | composite_score from Reliability Agent (0.0 to 1.0)                     |
| Color scale       | 0.0-0.4: Red (#EF4444), 0.4-0.7: Amber (#F59E0B), 0.7-1.0: Green (#10B981) |
| Animation         | Arc fills from 0 to target value over 800ms (Framer Motion spring)       |
| Label             | Center text: score as percentage (e.g., "85%") + trust level label       |
| Trust levels      | 0.0-0.4: "Low Confidence", 0.4-0.7: "Moderate Confidence", 0.7-1.0: "High Confidence" |
| Tooltip           | On hover: breakdown of individual RAGAS and DeepEval scores              |
| Accessibility     | role="meter", aria-valuenow, aria-valuemin=0, aria-valuemax=100          |

#### Source Attribution Cards

| Property          | Specification                                                            |
| ----------------- | ------------------------------------------------------------------------ |
| Layout            | Vertical stack of collapsible cards, one per sourced claim               |
| Default state     | Collapsed (shows claim text + source title + relevance badge)            |
| Expanded state    | Shows full source text, page number, relevance score bar, link to source |
| Animation         | Expand/collapse: Framer Motion layout animation (300ms, ease-out)        |
| Relevance badge   | Color-coded: >= 0.8 Green, >= 0.6 Amber, < 0.6 Red                      |
| Unsourced claims  | Displayed with a "No source found" badge (Red) and dashed border         |
| Accessibility     | Each card is a disclosure widget (button + aria-expanded + aria-controls)|

#### Dark/Light Mode

| Property          | Specification                                                        |
| ----------------- | -------------------------------------------------------------------- |
| Detection         | System preference via `prefers-color-scheme` media query             |
| Manual toggle     | Toggle button in header; persisted to localStorage                   |
| Priority          | Manual override > System preference                                  |
| Implementation    | CSS custom properties on `:root` and `[data-theme="dark"]`          |
| Transition        | 200ms transition on background-color and color properties            |
| WCAG contrast     | All text meets 4.5:1 contrast ratio in both modes                   |

#### 4K Responsiveness

| Breakpoint   | Width Range       | Layout Adjustments                                           |
| ------------ | ----------------- | ------------------------------------------------------------ |
| Mobile       | 320px -- 639px    | Single column; stacked cards; hamburger nav; touch targets >= 44px |
| Tablet       | 640px -- 1023px   | Two-column grid; side panel for trace                         |
| Desktop      | 1024px -- 1919px  | Three-column grid; inline trace panel                         |
| Large Desktop| 1920px -- 2559px  | Full-width with generous whitespace; larger fonts             |
| 4K           | 2560px -- 3840px  | Fluid scaling; max-width container at 2400px; increased padding |

**Micro-Interactions:**

| Interaction         | Specification                                                        |
| -------------------- | -------------------------------------------------------------------- |
| Button hover         | Scale 1.02, subtle shadow increase, 150ms transition                 |
| Button active        | Scale 0.98, 50ms transition                                          |
| Focus ring           | 2px solid primary color, 2px offset, visible on keyboard nav only    |
| Card hover           | Subtle border color change (150ms), slight elevation increase        |
| Score change         | Number counter animation (count up/down, 500ms, ease-out)           |
| Status badge change  | Cross-fade with scale pulse (200ms)                                  |
| Error state          | Shake animation (3 cycles, 4px amplitude, 300ms)                    |

**Input/Output Contract:**

| Direction | Schema                                                                                          |
| --------- | ----------------------------------------------------------------------------------------------- |
| Input     | `{ results: GlobalState.results (all sections, read-only), trace_log: list<TraceEntry>, agents: map<agent_id, AgentRecord>, swarm_health: HealthReport, state_snapshot: GlobalState (UX/UI slice) }` |
| Output    | `StatePatch { results.ui_payload.display_response, results.ui_payload.confidence_gauge, results.ui_payload.trace_events, results.ui_payload.source_cards, agents.ux_ui.status }` |

**State Management:**

- Reads: All `results` sections (read-only), `trace_log`, `agents` map, swarm health report.
- Writes: `results.ui_payload` section exclusively.
- Internal state: React component state for UI interactions (expanded/collapsed cards, scroll position, theme preference). None shared globally.
- Streaming: The UX/UI Agent subscribes to an SSE stream from the Mother Agent. Each state change triggers a new event, allowing the dashboard to update incrementally.

**Error Handling and Recovery:**

| Error                                    | Recovery                                                                |
| ---------------------------------------- | ----------------------------------------------------------------------- |
| SSE connection drops                     | Automatic reconnect with exponential backoff (1s, 2s, 4s, max 30s)     |
| Partial data from upstream agents        | Render available data; show skeleton placeholders for missing sections  |
| Invalid data in results payload          | Display "Data unavailable" card with error details; do not crash UI     |
| JavaScript runtime error                 | Error boundary catches and displays fallback UI; logs to trace          |
| Theme detection fails                    | Default to light mode                                                    |
| Font/asset loading fails                 | Fallback to system fonts and inline SVG icons                           |

**Performance Targets:**

| Metric                                | Target              |
| ------------------------------------- | -------------------- |
| First Contentful Paint (FCP)          | < 800ms             |
| Largest Contentful Paint (LCP)        | < 1,500ms           |
| Time to Interactive (TTI)             | < 2,000ms           |
| Cumulative Layout Shift (CLS)        | < 0.05              |
| First Input Delay (FID)              | < 50ms              |
| SSE event-to-render latency          | < 100ms             |
| Animation frame rate                  | >= 60fps             |
| Bundle size (gzipped)                 | < 150KB initial load |

**Dependencies:**

| Dependency            | Direction    | Nature                                                    |
| --------------------- | ------------ | --------------------------------------------------------- |
| Reliability Agent     | Upstream     | Requires validation scores and source attributions         |
| Performance Agent     | Upstream     | Requires inference results for display                     |
| Orchestration Agent   | Upstream     | Requires correction data (if any)                          |
| Mother Agent          | Bidirectional| Subscribes to SSE stream; reports rendering status         |
| Next.js runtime       | External     | Must be running (dev or production mode)                   |
| Framer Motion         | External     | NPM package; bundled at build time                         |

---

## Cross-Agent Dependency Matrix

This matrix summarizes every dependency relationship in the swarm.

| Agent (Row depends on Column) | Mother | Performance | Orchestration | Reliability | UX/UI |
| ----------------------------- | ------ | ----------- | ------------- | ----------- | ----- |
| **Mother Agent**              | --     | Monitors    | Monitors      | Monitors    | Monitors |
| **Performance Agent**         | Governed | --        | None          | None        | None  |
| **Orchestration Agent**       | Governed | Reads inference | --       | None        | None  |
| **Reliability Agent**         | Governed | Reads inference | Reads correction | --   | None  |
| **UX/UI Agent**               | Governed + SSE | Reads inference | Reads correction | Reads validation | -- |

**Data Flow Summary:**

```
DATA FLOW THROUGH THE SWARM
=============================

User Query
    |
    v
[Mother Agent] --spawn--> [Performance Agent]
                                |
                                | results.inference
                                v
[Mother Agent] --spawn--> [Orchestration Agent]
                                |
                                | results.correction (if needed)
                                v
[Mother Agent] --spawn--> [Reliability Agent]
                                |
                                | results.validation + source_attributions
                                v
[Mother Agent] --notify--> [UX/UI Agent]
                                |
                                | results.ui_payload
                                v
                          User Dashboard
```

### Corrector → Critic Data Flow (via Mother Agent)

The Corrector and Critic agents do not communicate directly through global state. Instead, data flows through the Mother Agent as an intermediary:

```
CORRECTOR → CRITIC DATA FLOW
==============================

Step 1: Corrector Agent needs critique of failed response
    |   Corrector writes a CRITIQUE_REQUEST to its StatePatch:
    |     { request_type: "CRITIQUE", payload: { raw_response, query, flags } }
    v
Step 2: Mother Agent receives the StatePatch
    |   Validates the request against Orchestration Agent's write-access list
    |   Takes a snapshot of the relevant state (results.inference + validation)
    |   Snapshot latency: ~5ms (deep copy of affected state slice)
    v
Step 3: Mother Agent invokes Critic Agent with the snapshot
    |   This is the ONLY direct function call in the entire architecture
    |   (all other communication is state-based)
    |   The Critic receives: { raw_response, context_docs, query, validation_flags }
    v
Step 4: Critic Agent produces CritiqueResult
    |   Writes to state.critic_output (its sole write slice)
    |   Mother Agent commits the patch: GlobalState v(N) → v(N+1)
    v
Step 5: Corrector Agent reads the updated state snapshot
        Sees critic_output with critique_text and suggested_fixes
        Constructs corrected_prompt incorporating the feedback
        Snapshot-to-availability latency: ~5ms
```

**Total data flow overhead:** ~10ms (two snapshot operations). This overhead is negligible compared to the Critic Agent's LLM call (~1–3 seconds) but is documented here for latency budgeting.

---

## Risk Register

| ID    | Risk                                              | Likelihood | Impact | Prob (1-5) | Impact (1-5) | Risk Score | Mitigation                                                              |
| ----- | ------------------------------------------------- | ---------- | ------ | ---------- | ------------ | ---------- | ----------------------------------------------------------------------- |
| R-01  | Mother Agent single point of failure              | Medium     | Critical | 3          | 5            | 15         | Health watchdog process restarts Mother Agent within 5s; fallback response returned |
| R-02  | Token budget too restrictive for complex queries  | High       | Medium | 4          | 3            | 12         | Configurable ceiling per query type; overflow borrowing from reserve     |
| R-03  | LLM non-determinism breaks idempotency            | High       | Low    | 4          | 2            | 8          | Accept near-idempotency (>95% similarity); seed-based reproducibility   |
| R-04  | Deadlock despite prevention architecture          | Very Low   | Critical | 1          | 5            | 5          | Lock-wait graph monitor; emergency lock-release circuit breaker         |
| R-05  | DLQ overflow under sustained failure              | Low        | High   | 2          | 4            | 8          | Circuit breaker at 100 entries; auto-scaling DLQ storage; global 1000-entry FIFO limit |
| R-06  | RAGAS/DeepEval version incompatibility            | Medium     | Medium | 3          | 3            | 9          | Pin dependency versions; integration test on every update               |
| R-07  | Ollama service crashes under load                 | Medium     | High   | 3          | 4            | 12         | Health check at initialization; automatic restart via process supervisor |
| R-08  | UX/UI SSE stream backpressure                     | Low        | Low    | 2          | 2            | 4          | Buffer up to 100 events; drop oldest if buffer full; client reconnects  |
| R-09  | Conflict resolution discards important data       | Low        | Medium | 2          | 3            | 6          | All discarded patches go to DLQ; audit trail in trace log               |
| R-10  | Agent priority ranking is incorrect for a scenario| Medium     | Medium | 3          | 3            | 9          | Priority ranking is configurable; can be overridden per query type      |

**Risk Scoring:** Probability (1=Very Low, 2=Low, 3=Medium, 4=High, 5=Very High) × Impact (1=Negligible, 2=Low, 3=Medium, 4=High, 5=Critical). Risk Score > 12 = requires active mitigation. Risk Score > 20 = requires architectural change. All current risks are within acceptable bounds.

---

## Agent Name Mapping Table

Sprint 1 (Architecture) and Sprint 2 (Agent Design) use different naming conventions for the same agents. Sprint 3 (File Manifest) uses LangGraph node names in code. This table provides the canonical mapping across all three sprints:

| Sprint 1 Name (Architecture) | Sprint 2 Name (Agent Design) | LangGraph Node (Code) | Primary Responsibility |
|---|---|---|---|
| Inference Agent | Performance Agent | `inference_node` | LLM inference via Ollama |
| Validator Agent | Reliability Agent | `validator_node` | RAGAS + DeepEval scoring |
| Corrector Agent | Orchestration Agent | `corrector_node` | Prompt correction + retry logic |
| Critic Agent | *(part of Reliability flow)* | `critic_node` | Local LLM critique via DeepSeek-R1 |
| UX Renderer Agent | Premium UX/UI Agent | `ux_renderer_node` | Dashboard rendering + SSE streaming |
| Mother Agent | Mother Agent | `mother_agent` | Swarm orchestration + budget enforcement |

**Why the naming differs:** Sprint 1 names reflect the *functional role* of each agent within the state machine (what the agent does). Sprint 2 names reflect the *quality attribute* each agent optimizes (what the agent is responsible for). Both are valid perspectives; the LangGraph node names in Sprint 3 are the implementation-level identifiers used in code.

**Rule:** When referencing agents across documents, include the LangGraph node name in parentheses for unambiguous identification. Example: "The Validator Agent (`validator_node`) scores the response."

> **Cross-reference:** Sprint 1, Section 1.2.1 (Agent Overview Table) | Sprint 3 (File Manifest, `graph_engine.py` node functions)

---

## Glossary

| Term               | Definition                                                                                          |
| ------------------ | --------------------------------------------------------------------------------------------------- |
| Agent              | An autonomous computational unit that receives a task, processes it, and returns structured output   |
| DAG                | Directed Acyclic Graph; a graph with directed edges and no cycles, used to order agent execution     |
| Dead-Letter Queue  | A storage mechanism for messages/outputs that could not be processed successfully                    |
| GlobalState        | The single structured data object that represents the complete state of a query's processing         |
| Idempotency        | The property that applying an operation multiple times produces the same result as applying it once   |
| LRU Cache          | Least Recently Used cache; evicts the entry that has not been accessed for the longest time           |
| Mother Agent       | The supervisory agent that spawns, monitors, and coordinates all child agents                        |
| Mutex              | Mutual exclusion lock; ensures only one thread/process accesses a resource at a time                 |
| NF4                | Normal Float 4-bit quantization; reduces model size while preserving accuracy                        |
| RAGAS              | Retrieval Augmented Generation Assessment; a framework for evaluating RAG pipeline quality           |
| SSE                | Server-Sent Events; a protocol for unidirectional server-to-client streaming                         |
| StatePatch         | A diff object describing proposed changes to the GlobalState, submitted by an agent to the Mother Agent |
| Swarm              | The collective of all agents (Mother + children) working together on a query                         |
| Trace Log          | An append-only log of every action taken by every agent, used for observability and debugging         |

---

*End of Sprint 2 Agent Swarm Design Document.*
