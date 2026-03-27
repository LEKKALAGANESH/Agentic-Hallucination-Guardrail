# Sprint 3 File Manifest

## Agentic Hallucination Guardrail (LLMOps)

| Field | Value |
|---|---|
| **Document** | Sprint 3 -- File Manifest & Dependency Map |
| **Project** | Agentic Hallucination Guardrail |
| **Domain** | LLMOps / Retrieval-Augmented Generation Safety |
| **Sprint** | 3 (Implementation Target: Sprint 6) |
| **Status** | Roadmap -- No Code |
| **Created** | 2026-03-21 |
| **Last Updated** | 2026-03-21 |

---

## Table of Contents

- [3.1 Core Files to Generate](#31-core-files-to-generate)
  - [3.1.1 Backend -- Orchestration & Inference](#311-backend--orchestration--inference)
  - [3.1.2 Backend -- Evaluation & Configuration](#312-backend--evaluation--configuration)
  - [3.1.3 Frontend -- UI Components](#313-frontend--ui-components)
  - [3.1.4 Frontend -- Infrastructure (API, Hooks, Types)](#314-frontend--infrastructure-api-hooks-types)
- [3.2 Error Handling Strategy (Global Circuit Breaker)](#32-error-handling-strategy-global-circuit-breaker)
  - [3.2.1 Level 1 -- Agent-Level Circuit Breaker](#321-level-1--agent-level-circuit-breaker)
  - [3.2.2 Level 2 -- Node-Level Circuit Breaker](#322-level-2--node-level-circuit-breaker)
  - [3.2.3 Level 3 -- Swarm-Level Circuit Breaker](#323-level-3--swarm-level-circuit-breaker)
  - [3.2.4 Level 4 -- Global Circuit Breaker](#324-level-4--global-circuit-breaker)
  - [3.2.5 Cross-Cutting Concerns](#325-cross-cutting-concerns)
- [3.3 File Dependency Graph](#33-file-dependency-graph)
- [3.4 Implementation Priority Order](#34-implementation-priority-order)

---

## 3.1 Core Files to Generate

### Master File Index

| # | File | Layer | Priority | Estimated Complexity | Est. LOC |
|---|------|-------|----------|---------------------|----------|
| 1 | `graph_engine.py` | Backend -- Orchestration | P0 | High | ~450 |
| 2 | `mother_agent.py` | Backend -- Orchestration | P0 | High | ~500 |
| 3 | `critic_agent.py` | Backend -- Inference | P1 | High | ~350 |
| 4 | `evaluator.py` | Backend -- Evaluation | P1 | Medium-High | ~300 |
| 5 | `validation_rules.json` | Backend -- Configuration | P2 | Low | ~80 |
| 6 | `SkeletonLoader.tsx` | Frontend -- UI | P3 | Low-Medium | ~120 |
| 7 | `LiveTrace.tsx` | Frontend -- UI | P3 | Medium-High | ~280 |
| 8 | `ConfidenceGauge.tsx` | Frontend -- UI | P3 | Medium | ~200 |
| 9 | `SourceAttribution.tsx` | Frontend -- UI | P3 | Medium | ~220 |
| 10 | `CircuitBreaker.tsx` | Frontend -- UI | P3 | Medium | ~180 |
| 11 | `Dashboard.tsx` | Frontend -- UI | P4 | Medium | ~250 |
| 12 | `App_4K_Responsive.css` | Frontend -- Styles | P4 | Medium | ~400 |
| 13 | `api/stream.ts` | Frontend -- API | P3 | Medium | ~150 |
| 14 | `hooks/useAgentStream.ts` | Frontend -- Hooks | P3 | Medium | ~120 |
| 15 | `types/index.ts` | Frontend -- Types | P2 | Low | ~100 |

**Total estimated LOC: ~3,700** (backend ~1,680, frontend ~2,020)

---

### 3.1.1 Backend -- Orchestration & Inference

---

#### File 1: `graph_engine.py`

| Attribute | Detail |
|---|---|
| **Path** | `src/backend/orchestration/graph_engine.py` |
| **Purpose** | Implements the LangGraph state machine that governs the entire agent execution lifecycle. Defines every node (Retriever, Generator, Critic, Corrector, Evaluator), every edge (conditional transitions based on confidence scores and validation outcomes), retry logic with exponential backoff, and the circuit breaker integration points. This is the central nervous system of the pipeline. |
| **Sprint References** | Sprint 1 (architecture decision: LangGraph over CrewAI), Sprint 2 (state schema definition, node contracts) |

**Key Functions, Classes, and Exports**

| Symbol | Kind | Description |
|---|---|---|
| `GuardrailState` | TypedDict | Immutable state object passed between nodes. Fields: `query`, `context_docs`, `generated_response`, `confidence_score`, `validation_result`, `trace_events`, `retry_count`, `token_budget_remaining`, `circuit_breaker_state`, `partial_results`, `state_hash`. |
| `build_graph()` | Function | Factory function that constructs and returns the compiled `StateGraph`. Registers all nodes, wires all edges (including conditional edges), and sets the entry/exit points. Returns a `CompiledGraph` instance. |
| `retriever_node(state)` | Function | Invokes the RAG retrieval pipeline. Fetches top-k documents from the vector store, attaches relevance scores, and writes `context_docs` into state. Enforces a minimum source count from `validation_rules.json`. |
| `generator_node(state)` | Function | Calls the primary LLM (GPT-4o / Claude) with the retrieved context. Produces a candidate response and an initial self-assessed confidence score. Writes `generated_response` and `confidence_score` to state. |
| `critic_node(state)` | Function | Delegates to `critic_agent.py` for local DeepSeek-R1 critique. Receives a structured critique (factual accuracy, grounding, completeness) and updates `validation_result` in state. |
| `corrector_node(state)` | Function | Takes a failed validation result and re-generates the response with explicit correction instructions derived from the critique. Decrements `retry_count` in state. |
| `evaluator_node(state)` | Function | Delegates to `evaluator.py` for RAGAS + DeepEval scoring. Writes final metric scores into state. Acts as the terminal quality gate. |
| `should_retry(state)` | Function | Conditional edge function. Returns `"corrector"` if confidence is below threshold and retries remain, `"evaluator"` if confidence passes, or `"circuit_break"` if retries are exhausted. |
| `circuit_break_node(state)` | Function | Terminal failure node. Packages partial results, logs the failure reason, emits a `TraceEvent` of type `CIRCUIT_BREAK`, and returns state with `circuit_breaker_state = "OPEN"`. |
| `compute_state_hash(state)` | Function | Produces a deterministic SHA-256 hash of the mutable fields in state for loop detection. Used by Level 3 circuit breaker. |
| `RetryPolicy` | dataclass | Configurable retry parameters: `max_retries` (default 3), `backoff_base` (default 2.0), `backoff_max` (default 10.0), `jitter` (default True). |

**Dependencies (Imports)**

| Imported From | Symbols Used |
|---|---|
| `langgraph.graph` | `StateGraph`, `END` |
| `langgraph.prebuilt` | `ToolNode` (if tool-use nodes are needed) |
| `mother_agent.py` | `MotherAgent` (for health checks and budget enforcement callbacks) |
| `critic_agent.py` | `CriticAgent.critique()` |
| `evaluator.py` | `run_evaluation()` |
| `validation_rules.json` | Loaded at graph build time via `json.load()` |
| `hashlib` | `sha256` (for state hashing) |
| `logging` | Standard library logger |
| `time` | `monotonic` (for timeout enforcement) |

---

#### File 2: `mother_agent.py`

| Attribute | Detail |
|---|---|
| **Path** | `src/backend/orchestration/mother_agent.py` |
| **Purpose** | The Mother Agent is the top-level swarm orchestrator. It spawns, monitors, and terminates child agents (Retriever, Generator, Critic, Corrector, Evaluator). It enforces the global token budget, detects conflicts between agent outputs, resolves deadlocks, and provides a unified health-monitoring interface consumed by the SSE stream for real-time UI updates. |
| **Sprint References** | Sprint 1 (swarm architecture decision), Sprint 2 (budget ceiling definition, agent lifecycle contracts) |

**Key Functions, Classes, and Exports**

| Symbol | Kind | Description |
|---|---|---|
| `MotherAgent` | Class | Singleton orchestrator. Manages the full lifecycle of a query through the guardrail pipeline. Holds references to all child agent instances, the compiled graph, the token budget ledger, and the circuit breaker state machine. |
| `MotherAgent.__init__(config)` | Method | Accepts a configuration dict (loaded from `validation_rules.json` and environment variables). Initializes the token budget, retry counters, and the LangGraph instance via `build_graph()`. |
| `MotherAgent.run(query)` | Method | Primary entry point. Accepts a user query, initializes `GuardrailState`, invokes the compiled graph, and returns the final state. Emits `TraceEvent` objects at each stage via the registered event callback. This is an `async` method that yields SSE-compatible events. |
| `MotherAgent.enforce_budget(state)` | Method | Called before every LLM invocation. Checks `token_budget_remaining` against the projected token cost of the next call. If the budget would be exceeded, triggers Level 4 circuit breaker immediately. Returns a boolean (proceed / halt). |
| `MotherAgent.health_check()` | Method | Returns a `HealthStatus` dict: `{ agents: {name: status}, budget_remaining: int, retries_used: int, circuit_breaker: str, uptime_ms: int }`. Consumed by the SSE stream at 1-second intervals. |
| `MotherAgent.resolve_conflict(results)` | Method | When multiple agents produce contradictory outputs (e.g., Critic says "reject" but confidence score is above threshold), this method applies a deterministic resolution policy: Critic verdict always wins, confidence score is overridden downward, and the conflict is logged as a `TraceEvent`. |
| `MotherAgent.kill_branch(branch_id, reason)` | Method | Forcefully terminates a specific execution branch. Used by Level 3 circuit breaker when a loop is detected. Logs the kill event, preserves partial results from the branch, and updates `circuit_breaker_state`. |
| `MotherAgent.register_event_callback(fn)` | Method | Registers a callback function that receives `TraceEvent` objects in real time. The SSE endpoint (`api/stream.ts`) registers its push function here. |
| `HealthStatus` | TypedDict | Schema for the health check response. Fields: `agents`, `budget_remaining`, `retries_used`, `circuit_breaker`, `uptime_ms`, `active_node`. |
| `TokenLedger` | dataclass | Tracks token consumption across all agents. Fields: `budget_total`, `budget_used`, `budget_remaining`, `entries` (list of per-call records with agent name, token count, timestamp). |

**Dependencies (Imports)**

| Imported From | Symbols Used |
|---|---|
| `graph_engine.py` | `build_graph()`, `GuardrailState`, `compute_state_hash()` |
| `critic_agent.py` | `CriticAgent` |
| `evaluator.py` | `run_evaluation()` |
| `validation_rules.json` | Loaded at init time |
| `asyncio` | `create_task`, `wait_for`, `TimeoutError` |
| `logging` | Standard library logger |
| `time` | `monotonic` |
| `uuid` | `uuid4` (for branch IDs) |

---

#### File 3: `critic_agent.py`

| Attribute | Detail |
|---|---|
| **Path** | `src/backend/agents/critic_agent.py` |
| **Purpose** | Wraps the local DeepSeek-R1 model running via Ollama in NF4-quantized mode. This agent receives a generated response and its source context, then produces a structured critique assessing factual grounding, hallucination risk, completeness, and citation accuracy. The critique is returned as a typed dict consumed by the graph engine's conditional routing logic. |
| **Sprint References** | Sprint 1 (model selection: DeepSeek-R1), Sprint 2 (NF4 quantization decision, Ollama integration, critique schema) |

**Key Functions, Classes, and Exports**

| Symbol | Kind | Description |
|---|---|---|
| `CriticAgent` | Class | Stateless agent that interfaces with the local Ollama instance. Manages prompt construction, inference invocation, and response parsing. |
| `CriticAgent.__init__(model_name, ollama_url, timeout)` | Method | Configures the Ollama connection. `model_name` defaults to `"deepseek-r1:7b-nf4"`. `ollama_url` defaults to `"http://localhost:11434"`. `timeout` defaults to 30 seconds. |
| `CriticAgent.critique(response, context_docs, query)` | Method | Core method. Sends a structured prompt to DeepSeek-R1 that asks the model to evaluate the `response` against the `context_docs` for the given `query`. Parses the model output into a `CritiqueResult`. If the model fails or times out, returns a `CritiqueResult` with `verdict = "ERROR"` and `confidence = 0.0`. |
| `CriticAgent.build_critique_prompt(response, context_docs, query)` | Method | Constructs the system + user prompt for the critique task. Includes explicit instructions for JSON-formatted output with fields: `verdict`, `confidence`, `factual_accuracy`, `grounding_score`, `completeness`, `issues_found`, `suggested_corrections`. |
| `CriticAgent.parse_critique_response(raw_output)` | Method | Extracts structured JSON from the raw model output. Handles common failure modes: malformed JSON, missing fields, confidence values outside [0, 1]. Falls back to a conservative "REJECT" verdict if parsing fails entirely. |
| `CriticAgent.health_check()` | Method | Pings the Ollama API at `/api/tags` to verify the model is loaded and responsive. Returns `{ status: "ok" | "error", latency_ms: int, model_loaded: bool }`. |
| `CritiqueResult` | TypedDict | Structured output: `verdict` ("ACCEPT" / "REJECT" / "PARTIAL" / "ERROR"), `confidence` (float 0--1), `factual_accuracy` (float 0--1), `grounding_score` (float 0--1), `completeness` (float 0--1), `issues_found` (list of strings), `suggested_corrections` (list of strings). |
| `CRITIQUE_SYSTEM_PROMPT` | Constant | The system-level prompt instructing DeepSeek-R1 to behave as a factual grounding critic. Stored as a module-level string constant for testability. |

**Dependencies (Imports)**

| Imported From | Symbols Used |
|---|---|
| `httpx` | `AsyncClient` (for non-blocking Ollama API calls) |
| `json` | `loads`, `dumps` |
| `validation_rules.json` | Loaded for confidence thresholds and banned-pattern list |
| `logging` | Standard library logger |
| `asyncio` | `wait_for`, `TimeoutError` |
| `re` | Regex fallback parsing for malformed JSON extraction |

---

### 3.1.2 Backend -- Evaluation & Configuration

---

#### File 4: `evaluator.py`

| Attribute | Detail |
|---|---|
| **Path** | `src/backend/evaluation/evaluator.py` |
| **Purpose** | Integrates RAGAS and DeepEval libraries to provide a comprehensive scoring pipeline for generated responses. Computes individual metrics (faithfulness, answer relevancy, context precision, context recall, hallucination score), aggregates them into a single composite score, and enforces pass/fail thresholds defined in `validation_rules.json`. This is the final quality gate before a response is returned to the user. |
| **Sprint References** | Sprint 2 (metric selection, threshold calibration, RAGAS/DeepEval integration decision) |

**Key Functions, Classes, and Exports**

| Symbol | Kind | Description |
|---|---|---|
| `run_evaluation(state)` | Function | Primary entry point. Accepts a `GuardrailState`, extracts the query, context docs, and generated response, runs all configured metrics, and returns an `EvaluationResult`. This is the function called by `evaluator_node()` in the graph engine. |
| `EvaluationPipeline` | Class | Orchestrates the scoring process. Initializes RAGAS and DeepEval metric instances, runs them in parallel where possible, and collects results. |
| `EvaluationPipeline.score_faithfulness(response, context)` | Method | RAGAS faithfulness metric. Measures whether every claim in the response is supported by the provided context. Returns a float in [0, 1]. |
| `EvaluationPipeline.score_answer_relevancy(response, query)` | Method | RAGAS answer relevancy metric. Measures whether the response actually addresses the query. Returns a float in [0, 1]. |
| `EvaluationPipeline.score_context_precision(context, query)` | Method | RAGAS context precision metric. Measures whether the retrieved context is relevant to the query. Returns a float in [0, 1]. |
| `EvaluationPipeline.score_context_recall(context, ground_truth)` | Method | RAGAS context recall metric. Measures whether the context covers all necessary information. Returns a float in [0, 1]. Only runs when ground truth is available (evaluation mode). |
| `EvaluationPipeline.score_hallucination(response, context)` | Method | DeepEval hallucination metric. Specifically detects fabricated entities, events, or relationships not present in context. Returns a float in [0, 1] where 0 = no hallucination and 1 = fully hallucinated. |
| `EvaluationPipeline.aggregate(scores)` | Method | Computes a weighted composite score from all individual metrics. Weights are loaded from `validation_rules.json`. Returns a single float in [0, 1]. |
| `EvaluationPipeline.enforce_thresholds(result)` | Method | Compares each individual score and the composite score against minimum thresholds from `validation_rules.json`. Returns a `pass` / `fail` / `partial` verdict. |
| `EvaluationResult` | TypedDict | Complete evaluation output: `faithfulness` (float), `answer_relevancy` (float), `context_precision` (float), `context_recall` (float or None), `hallucination` (float), `composite_score` (float), `verdict` ("PASS" / "FAIL" / "PARTIAL"), `failed_metrics` (list of metric names that fell below threshold), `timestamp` (ISO 8601). |
| `MetricWeights` | TypedDict | Per-metric weighting for composite aggregation: `faithfulness_weight`, `relevancy_weight`, `precision_weight`, `recall_weight`, `hallucination_weight`. |

**Dependencies (Imports)**

| Imported From | Symbols Used |
|---|---|
| `ragas.metrics` | `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall` |
| `deepeval.metrics` | `HallucinationMetric` |
| `deepeval.test_case` | `LLMTestCase` |
| `validation_rules.json` | Loaded for thresholds and metric weights |
| `logging` | Standard library logger |
| `datetime` | `datetime.utcnow` |
| `asyncio` | `gather` (for parallel metric execution) |

---

#### File 5: `validation_rules.json`

| Attribute | Detail |
|---|---|
| **Path** | `src/backend/config/validation_rules.json` |
| **Purpose** | Single source of truth for all configurable validation parameters. Consumed by the graph engine, mother agent, critic agent, and evaluator at initialization time. Externalized to allow runtime tuning without code changes and to support environment-specific overrides (dev/staging/prod). |
| **Sprint References** | Sprint 1 (externalized configuration decision), Sprint 2 (threshold values, banned patterns list, source count requirements) |

**Key Structure and Fields**

| Top-Level Key | Type | Description |
|---|---|---|
| `confidence_thresholds` | Object | Per-stage confidence minimums. |
| `confidence_thresholds.critic_accept` | float | Minimum critic confidence to accept without correction. Default: `0.85`. |
| `confidence_thresholds.critic_partial` | float | Minimum critic confidence for "partial accept" routing. Default: `0.60`. |
| `confidence_thresholds.evaluator_pass` | float | Minimum composite evaluation score to pass. Default: `0.80`. |
| `confidence_thresholds.evaluator_warn` | float | Score below this triggers a warning banner in UI. Default: `0.65`. |
| `max_retries` | Object | Retry limits per circuit breaker level. |
| `max_retries.agent_level` | int | Max retries for a single agent before escalation. Default: `3`. |
| `max_retries.node_level` | int | Max times a node can route to Corrector. Default: `3`. |
| `max_retries.global` | int | Absolute maximum retries across all levels. Default: `10`. |
| `banned_patterns` | Array[string] | Regex patterns that trigger automatic rejection. Examples: `"As an AI"`, `"I cannot verify"`, `"I don't have access to"`, `"hallucinated-url\\.com"`. |
| `required_sources` | Object | Source citation requirements. |
| `required_sources.min_count` | int | Minimum number of source documents required. Default: `2`. |
| `required_sources.min_relevance_score` | float | Minimum relevance score per source. Default: `0.70`. |
| `token_budget` | Object | Cost control limits. |
| `token_budget.max_tokens_per_query` | int | Hard ceiling for total tokens consumed per query across all agents. Default: `50000`. |
| `token_budget.cost_ceiling_usd` | float | Maximum dollar cost per query. Default: `0.00` (portfolio demo mode: zero spend). |
| `timeout` | Object | Timing constraints. |
| `timeout.agent_timeout_seconds` | int | Max seconds any single agent may run. Default: `30`. |
| `timeout.total_pipeline_timeout_seconds` | int | Max seconds for the entire pipeline. Default: `120`. |
| `evaluation_weights` | Object | Weights for composite score aggregation. |
| `evaluation_weights.faithfulness` | float | Default: `0.30`. |
| `evaluation_weights.answer_relevancy` | float | Default: `0.20`. |
| `evaluation_weights.context_precision` | float | Default: `0.20`. |
| `evaluation_weights.context_recall` | float | Default: `0.10`. |
| `evaluation_weights.hallucination` | float | Default: `0.20`. |
| `circuit_breaker` | Object | Circuit breaker configuration. |
| `circuit_breaker.loop_detection_window` | int | Number of previous states to compare against for loop detection. Default: `5`. |
| `circuit_breaker.half_open_retry_after_seconds` | int | Seconds before a tripped circuit breaker transitions to half-open. Default: `60`. |
| `ui` | Object | Frontend display thresholds. |
| `ui.confidence_red_below` | float | Confidence below this renders the gauge red. Default: `0.50`. |
| `ui.confidence_yellow_below` | float | Confidence below this renders the gauge yellow. Default: `0.75`. |
| `ui.confidence_green_above` | float | Confidence at or above this renders the gauge green. Default: `0.75`. |

**Dependencies**

| Consumed By | How |
|---|---|
| `graph_engine.py` | `json.load()` at graph build time |
| `mother_agent.py` | `json.load()` at `MotherAgent.__init__()` |
| `critic_agent.py` | `json.load()` for banned patterns and thresholds |
| `evaluator.py` | `json.load()` for metric weights and thresholds |
| `api/stream.ts` | Served via a `/config` REST endpoint for frontend consumption |

---

### 3.1.3 Frontend -- UI Components

---

#### File 6: `SkeletonLoader.tsx`

| Attribute | Detail |
|---|---|
| **Path** | `src/frontend/components/SkeletonLoader.tsx` |
| **Purpose** | Provides skeleton placeholder cards displayed while agents are processing. Implements shimmer animation to indicate loading, thought-process mimicry (skeleton shapes that resemble the eventual content: text lines, source cards, confidence gauge), and progressive reveal where skeleton elements are replaced one-by-one as real data arrives from the SSE stream. |
| **Sprint References** | Sprint 2 (UX decision: never show blank screens, progressive loading pattern) |

**Key Functions, Classes, and Exports**

| Symbol | Kind | Description |
|---|---|---|
| `SkeletonLoader` | Component | Top-level skeleton wrapper. Renders a grid of skeleton cards matching the dashboard layout. Accepts `revealedSections` prop to progressively unmask completed areas. |
| `SkeletonCard` | Component | Individual skeleton card. Props: `width`, `height`, `lines` (number of text placeholder lines), `variant` ("text" / "gauge" / "source" / "trace"). |
| `ShimmerOverlay` | Component | CSS-animated gradient overlay that creates the shimmer/pulse effect. Uses `@keyframes` with `translateX` for the sweep animation. |
| `ThoughtMimicry` | Component | Renders animated pseudo-text lines that subtly pulse at different rates, mimicking the visual cadence of "thinking." Accepts `stage` prop ("retrieving" / "generating" / "critiquing" / "evaluating") and adjusts placeholder shapes accordingly. |

**Dependencies (Imports)**

| Imported From | Symbols Used |
|---|---|
| `react` | `React`, `FC`, `memo` |
| `types/index.ts` | `AgentState` (to determine which sections to reveal) |
| `App_4K_Responsive.css` | Global responsive grid classes |
| `framer-motion` | `motion`, `AnimatePresence` (for reveal transitions) |

---

#### File 7: `LiveTrace.tsx`

| Attribute | Detail |
|---|---|
| **Path** | `src/frontend/components/LiveTrace.tsx` |
| **Purpose** | Renders a real-time animated node graph showing agent execution progress. Each node in the LangGraph state machine is represented visually. Edges animate as transitions occur. Active nodes pulse, completed nodes show a checkmark with duration, and failed nodes show a red X. Uses Framer Motion for all animations. This is the primary "observability" component giving users transparency into what the system is doing. |
| **Sprint References** | Sprint 2 (observability requirement, trace event schema) |

**Key Functions, Classes, and Exports**

| Symbol | Kind | Description |
|---|---|---|
| `LiveTrace` | Component | Main trace visualization. Accepts `traceEvents` (array of `TraceEvent`) and `currentNode` (string). Renders a directed graph of nodes with animated edges. |
| `TraceNode` | Component | Individual node in the graph. Props: `name`, `status` ("idle" / "active" / "completed" / "failed" / "skipped"), `duration_ms`, `retry_count`. Renders with appropriate color, icon, and animation state. |
| `TraceEdge` | Component | Animated SVG line connecting two `TraceNode` components. Animates a traveling dot along the edge when a transition occurs. Props: `from`, `to`, `active`, `animated`. |
| `TraceTimeline` | Component | Optional linear timeline view (alternative to graph view). Shows events in chronological order with timestamps and durations. Toggle between graph and timeline via a tab control. |
| `useTraceLayout` | Hook | Computes node positions for the graph layout using a simple layered/hierarchical algorithm. Returns `{ nodes: NodePosition[], edges: EdgePosition[] }`. |

**Dependencies (Imports)**

| Imported From | Symbols Used |
|---|---|
| `react` | `React`, `FC`, `useMemo`, `useCallback` |
| `framer-motion` | `motion`, `AnimatePresence`, `useAnimation` |
| `types/index.ts` | `TraceEvent`, `AgentState` |
| `hooks/useAgentStream.ts` | `useAgentStream` (to receive live trace events) |
| `App_4K_Responsive.css` | Responsive container classes |

---

#### File 8: `ConfidenceGauge.tsx`

| Attribute | Detail |
|---|---|
| **Path** | `src/frontend/components/ConfidenceGauge.tsx` |
| **Purpose** | Animated radial (circular arc) gauge that displays the current confidence score. Color-coded: red below 0.50, yellow between 0.50 and 0.75, green at or above 0.75 (thresholds loaded from config). Includes a tooltip on hover/tap that breaks down the confidence into its component scores (faithfulness, relevancy, grounding, etc.). Animates smoothly between values as scores update in real time. |
| **Sprint References** | Sprint 2 (confidence visualization requirement, color-coding thresholds) |

**Key Functions, Classes, and Exports**

| Symbol | Kind | Description |
|---|---|---|
| `ConfidenceGauge` | Component | Main gauge component. Props: `score` (float 0--1), `breakdown` (optional `ConfidenceScore` object), `size` ("sm" / "md" / "lg"), `animated` (boolean, default true). |
| `RadialArc` | Component | SVG-based circular arc that fills proportionally to the score. Uses `stroke-dasharray` and `stroke-dashoffset` for the fill animation. Color is computed from score thresholds. |
| `ScoreLabel` | Component | Centered numeric display inside the gauge. Shows the score as a percentage (e.g., "87%"). Font size scales with gauge size. |
| `BreakdownTooltip` | Component | Popover/tooltip that appears on hover. Renders a mini bar chart of individual metric scores. Props: `breakdown` (`ConfidenceScore`). |
| `getGaugeColor(score, thresholds)` | Function | Pure function that returns a CSS color string based on the score and configured thresholds. Returns `"#ef4444"` (red), `"#f59e0b"` (yellow), or `"#22c55e"` (green). |

**Dependencies (Imports)**

| Imported From | Symbols Used |
|---|---|
| `react` | `React`, `FC`, `useMemo` |
| `framer-motion` | `motion`, `useSpring`, `useTransform` |
| `types/index.ts` | `ConfidenceScore` |
| `App_4K_Responsive.css` | Responsive sizing classes |

---

#### File 9: `SourceAttribution.tsx`

| Attribute | Detail |
|---|---|
| **Path** | `src/frontend/components/SourceAttribution.tsx` |
| **Purpose** | Renders expandable cards for each source document cited in the response. Each card shows the source title, a relevance score badge, a citation link, and an expandable section that highlights the specific passages matched by the retriever. Designed to give users full transparency into what evidence supports the generated response. |
| **Sprint References** | Sprint 2 (source transparency requirement, minimum source count enforcement) |

**Key Functions, Classes, and Exports**

| Symbol | Kind | Description |
|---|---|---|
| `SourceAttribution` | Component | Container component. Accepts `sources` (array of `SourceDocument`). Renders a list of `SourceCard` components. Shows a warning if source count is below the configured minimum. |
| `SourceCard` | Component | Individual expandable card. Props: `source` (`SourceDocument`). Collapsed state shows title + relevance badge. Expanded state reveals matched passages with highlighted text spans. Uses `AnimatePresence` for expand/collapse animation. |
| `RelevanceBadge` | Component | Color-coded badge showing the relevance score. Uses the same red/yellow/green thresholds as the confidence gauge for visual consistency. |
| `HighlightedPassage` | Component | Renders a text block with specific spans highlighted (wrapped in `<mark>` tags). Props: `text`, `highlights` (array of `{ start: number, end: number }`). |
| `CitationLink` | Component | Clickable link to the original source. Opens in a new tab. Shows a truncated URL with a copy-to-clipboard button. |

**Dependencies (Imports)**

| Imported From | Symbols Used |
|---|---|
| `react` | `React`, `FC`, `useState`, `useCallback` |
| `framer-motion` | `motion`, `AnimatePresence` |
| `types/index.ts` | `SourceDocument` (part of `AgentState`) |
| `App_4K_Responsive.css` | Card layout and responsive classes |

---

#### File 10: `CircuitBreaker.tsx`

| Attribute | Detail |
|---|---|
| **Path** | `src/frontend/components/CircuitBreaker.tsx` |
| **Purpose** | UI component that renders the circuit breaker state to the user. When the circuit breaker trips at any level, this component displays a contextual warning banner with the specific reason, a retry button (if recovery is possible), detailed error information in an expandable section, and any partial results available. This is the critical "graceful degradation" component that ensures users are never left with a blank screen. |
| **Sprint References** | Sprint 1 (graceful degradation requirement), Sprint 2 (circuit breaker level definitions, partial results schema) |

**Key Functions, Classes, and Exports**

| Symbol | Kind | Description |
|---|---|---|
| `CircuitBreaker` | Component | Main component. Props: `state` (`CircuitBreakerState`), `partialResults` (optional partial `AgentState`), `onRetry` (callback), `onDismiss` (callback). Renders differently based on which level was triggered. |
| `WarningBanner` | Component | Top-level alert banner. Color varies by severity: amber for Level 1-2 (recoverable), red for Level 3-4 (terminal). Shows a human-readable summary message. |
| `ErrorDetails` | Component | Expandable section showing technical details: which agent failed, what the error was, how many retries were attempted, token budget status. Intended for power users and debugging. |
| `PartialResultsPanel` | Component | Renders whatever partial results are available (e.g., retrieved sources without a generated response, or a generated response without evaluation). Clearly labels each section with its completeness status. |
| `RetryButton` | Component | Conditional retry button. Only displayed for Level 1 and Level 2 breakers. Disabled during the "half-open" cooldown period. Shows a countdown timer if in cooldown. |
| `SafetyMessage` | Component | Static message displayed for Level 4 breaker: "System paused for safety. Here's what we know so far." Cannot be dismissed, retry is not offered. |

**Dependencies (Imports)**

| Imported From | Symbols Used |
|---|---|
| `react` | `React`, `FC`, `useState`, `useEffect` |
| `framer-motion` | `motion`, `AnimatePresence` |
| `types/index.ts` | `CircuitBreakerState`, `AgentState` |
| `hooks/useAgentStream.ts` | `useAgentStream` (to receive circuit breaker state changes) |
| `App_4K_Responsive.css` | Banner and panel layout classes |

---

#### File 11: `Dashboard.tsx`

| Attribute | Detail |
|---|---|
| **Path** | `src/frontend/components/Dashboard.tsx` |
| **Purpose** | Main dashboard layout component that composes all other UI components into a 4K-responsive grid. Manages the top-level state flow: receives data from the `useAgentStream` hook, distributes it to child components via props, and handles the progressive reveal sequence (skeleton to live data). Acts as the single entry point for the entire frontend UI. |
| **Sprint References** | Sprint 2 (dashboard layout specification, 4K responsive requirement, component composition plan) |

**Key Functions, Classes, and Exports**

| Symbol | Kind | Description |
|---|---|---|
| `Dashboard` | Component | Root layout component. Uses CSS Grid for a responsive multi-panel layout. Panels: Live Trace (top-left, spans 2 columns on large screens), Confidence Gauge (top-right), Source Attribution (middle, full width), Generated Response (bottom-left), Circuit Breaker (overlay, conditional). |
| `DashboardHeader` | Component | Top bar with query input, run button, and system health indicator (green/yellow/red dot sourced from `MotherAgent.health_check()`). |
| `QueryInput` | Component | Text input with submit handler. Triggers `MotherAgent.run()` via the API. Disabled while a query is in progress. |
| `ResponsePanel` | Component | Renders the final generated response with inline source citation markers (clickable, linked to `SourceAttribution` cards). Shows the evaluation verdict badge. |
| `useDashboardState` | Hook | Local state management hook that orchestrates the data flow. Calls `useAgentStream`, derives which skeleton sections to reveal, handles error states, and provides a unified state object to all child components. |

**Dependencies (Imports)**

| Imported From | Symbols Used |
|---|---|
| `react` | `React`, `FC`, `useState`, `useEffect`, `useCallback` |
| `SkeletonLoader.tsx` | `SkeletonLoader` |
| `LiveTrace.tsx` | `LiveTrace` |
| `ConfidenceGauge.tsx` | `ConfidenceGauge` |
| `SourceAttribution.tsx` | `SourceAttribution` |
| `CircuitBreaker.tsx` | `CircuitBreaker` |
| `hooks/useAgentStream.ts` | `useAgentStream` |
| `types/index.ts` | `AgentState`, `TraceEvent`, `ConfidenceScore`, `ValidationResult` |
| `App_4K_Responsive.css` | Global grid layout, responsive breakpoints |

---

### 3.1.4 Frontend -- Infrastructure (API, Hooks, Types)

---

#### File 12: `App_4K_Responsive.css`

| Attribute | Detail |
|---|---|
| **Path** | `src/frontend/styles/App_4K_Responsive.css` |
| **Purpose** | Global responsive stylesheet defining the breakpoint system, fluid typography scale, CSS Grid layout templates, and utility classes used across all frontend components. Supports six breakpoints from mobile (320px) to ultra-wide 4K (3840px) with fluid interpolation between each. |
| **Sprint References** | Sprint 2 (4K support requirement, responsive breakpoint specification) |

**Key Structure and Contents**

| Section | Description |
|---|---|
| **CSS Custom Properties** | Root-level variables: `--font-size-base`, `--grid-columns`, `--grid-gap`, `--container-max-width`, `--color-red`, `--color-yellow`, `--color-green`, color palette tokens for light/dark mode. |
| **Fluid Typography** | Uses `clamp()` for font sizes that scale smoothly between breakpoints. Base: `clamp(0.875rem, 0.8rem + 0.25vw, 1.125rem)`. Headings scale proportionally. |
| **Breakpoint: 320px** (Mobile) | Single column grid. Stacked layout. Touch-friendly tap targets (minimum 44px). Gauge renders at "sm" size. |
| **Breakpoint: 768px** (Tablet) | Two column grid. Trace and gauge side by side. Source cards in a single column. |
| **Breakpoint: 1024px** (Desktop) | Three column grid. Trace spans 2 columns. Gauge in right column. Sources below in 2-column sub-grid. |
| **Breakpoint: 1440px** (Large Desktop) | Four column grid. All panels visible simultaneously. Full trace graph with expanded nodes. |
| **Breakpoint: 2560px** (QHD) | Four column grid with increased gap and padding. Font sizes scale up. Gauge renders at "lg" size. |
| **Breakpoint: 3840px** (4K UHD) | Four column grid with maximum spacing. All elements at largest comfortable size. No horizontal scroll at any content length. |
| **Shimmer Animation** | `@keyframes shimmer` used by `SkeletonLoader`. Gradient sweep from left to right over 1.5 seconds, infinite loop. |
| **Utility Classes** | `.visually-hidden`, `.truncate`, `.badge-red`, `.badge-yellow`, `.badge-green`, `.card`, `.card-expandable`, `.overlay`, `.banner-warning`, `.banner-error`. |

**Dependencies**

| Consumed By | How |
|---|---|
| All `.tsx` components | Imported directly or via CSS module scope |
| `Dashboard.tsx` | Grid layout template classes |
| `SkeletonLoader.tsx` | Shimmer animation keyframes |

---

#### File 13: `api/stream.ts`

| Attribute | Detail |
|---|---|
| **Path** | `src/frontend/api/stream.ts` |
| **Purpose** | Server-Sent Events (SSE) endpoint that bridges the backend Python pipeline and the frontend React application. When a query is submitted, this endpoint opens a long-lived HTTP connection, registers an event callback with the Mother Agent, and pushes `TraceEvent` objects to the client as they occur. Handles connection lifecycle (open, message, error, close) and implements heartbeat keep-alive to prevent proxy timeouts. |
| **Sprint References** | Sprint 2 (real-time streaming requirement, SSE over WebSocket decision) |

**Key Functions, Classes, and Exports**

| Symbol | Kind | Description |
|---|---|---|
| `createStreamEndpoint()` | Function | Factory that returns an HTTP handler (compatible with Next.js API routes or Express). Accepts configuration for heartbeat interval and max connection duration. |
| `handleStreamRequest(req, res)` | Function | Core request handler. Validates the query parameter, sets SSE headers (`Content-Type: text/event-stream`, `Cache-Control: no-cache`, `Connection: keep-alive`), calls the backend API to start the pipeline, and pipes events to the response stream. |
| `formatSSEMessage(event)` | Function | Serializes a `TraceEvent` into SSE wire format: `data: {json}\n\n`. Adds event type field for client-side routing: `event: trace`, `event: health`, `event: result`, `event: error`, `event: circuit_break`. |
| `startHeartbeat(res, interval)` | Function | Sends a comment line (`: heartbeat\n\n`) at a configurable interval (default 15 seconds) to prevent reverse proxies and load balancers from closing idle connections. Returns a cleanup function. |
| `StreamConfig` | Interface | Configuration type: `heartbeat_interval_ms` (number), `max_connection_duration_ms` (number), `backend_url` (string). |

**Dependencies (Imports)**

| Imported From | Symbols Used |
|---|---|
| `types/index.ts` | `TraceEvent`, `AgentState`, `ConfidenceScore` |
| `node:http` or framework-specific | `IncomingMessage`, `ServerResponse` (or Next.js/Express equivalents) |

---

#### File 14: `hooks/useAgentStream.ts`

| Attribute | Detail |
|---|---|
| **Path** | `src/frontend/hooks/useAgentStream.ts` |
| **Purpose** | Custom React hook that consumes the SSE stream from `api/stream.ts` and manages all client-side state for a running query. Handles connection lifecycle, reconnection with exponential backoff, parsing of incoming events, and exposes a clean API of loading/error/success states to consuming components. This is the single data source for all frontend components. |
| **Sprint References** | Sprint 2 (frontend state management approach, SSE consumption pattern) |

**Key Functions, Classes, and Exports**

| Symbol | Kind | Description |
|---|---|---|
| `useAgentStream(query)` | Hook | Primary export. Accepts a query string (or null to idle). Returns a `StreamState` object. When `query` is non-null, opens an `EventSource` connection to the SSE endpoint and begins accumulating state. Automatically closes the connection on unmount or when `query` changes. |
| `StreamState` | Interface | Return type of the hook: `status` ("idle" / "connecting" / "streaming" / "completed" / "error"), `traceEvents` (TraceEvent[]), `agentState` (partial AgentState, progressively populated), `confidenceScore` (ConfidenceScore or null), `circuitBreakerState` (CircuitBreakerState or null), `error` (Error or null), `partialResults` (partial AgentState or null), `retry()` (function to restart the stream). |
| `parseSSEEvent(raw)` | Function | Internal parser. Extracts the `event` type and `data` JSON from a raw SSE message string. Returns a typed discriminated union based on event type. |
| `useReconnect(url, options)` | Hook | Internal hook for exponential backoff reconnection. Tracks retry count and delay. Caps at 3 reconnection attempts before surfacing a permanent error. |

**Dependencies (Imports)**

| Imported From | Symbols Used |
|---|---|
| `react` | `useState`, `useEffect`, `useCallback`, `useRef` |
| `types/index.ts` | `TraceEvent`, `AgentState`, `ConfidenceScore`, `CircuitBreakerState` |

---

#### File 15: `types/index.ts`

| Attribute | Detail |
|---|---|
| **Path** | `src/frontend/types/index.ts` |
| **Purpose** | Central TypeScript type definitions shared across all frontend files. Defines the data contracts between the SSE stream and the UI components. Every type here mirrors a corresponding Python TypedDict or dataclass from the backend, ensuring type safety across the full stack. |
| **Sprint References** | Sprint 2 (type schema definitions, frontend-backend contract) |

**Key Types and Exports**

| Symbol | Kind | Description |
|---|---|---|
| `AgentState` | interface | Mirrors `GuardrailState` from `graph_engine.py`. Fields: `query` (string), `contextDocs` (SourceDocument[]), `generatedResponse` (string or null), `confidenceScore` (number or null), `validationResult` (ValidationResult or null), `traceEvents` (TraceEvent[]), `retryCount` (number), `tokenBudgetRemaining` (number), `circuitBreakerState` (CircuitBreakerState), `partialResults` (Partial\<AgentState\> or null). |
| `TraceEvent` | interface | Single event in the execution trace. Fields: `id` (string), `timestamp` (string, ISO 8601), `node` (string), `eventType` ("NODE_START" / "NODE_END" / "TRANSITION" / "RETRY" / "CIRCUIT_BREAK" / "ERROR"), `duration_ms` (number or null), `metadata` (Record\<string, unknown\>). |
| `ConfidenceScore` | interface | Detailed confidence breakdown. Fields: `overall` (number), `faithfulness` (number), `answerRelevancy` (number), `contextPrecision` (number), `contextRecall` (number or null), `hallucination` (number). |
| `ValidationResult` | interface | Critic output. Fields: `verdict` ("ACCEPT" / "REJECT" / "PARTIAL" / "ERROR"), `confidence` (number), `factualAccuracy` (number), `groundingScore` (number), `completeness` (number), `issuesFound` (string[]), `suggestedCorrections` (string[]). |
| `SourceDocument` | interface | A retrieved source. Fields: `id` (string), `title` (string), `url` (string), `relevanceScore` (number), `matchedPassages` (MatchedPassage[]). |
| `MatchedPassage` | interface | A highlighted span within a source. Fields: `text` (string), `startOffset` (number), `endOffset` (number). |
| `CircuitBreakerState` | enum | `"CLOSED"` (healthy), `"OPEN"` (tripped), `"HALF_OPEN"` (testing recovery). |
| `CircuitBreakerLevel` | enum | `"AGENT"` (Level 1), `"NODE"` (Level 2), `"SWARM"` (Level 3), `"GLOBAL"` (Level 4). |
| `EvaluationResult` | interface | Mirrors `EvaluationResult` from `evaluator.py`. Fields: `faithfulness`, `answerRelevancy`, `contextPrecision`, `contextRecall`, `hallucination`, `compositeScore`, `verdict`, `failedMetrics`, `timestamp`. |
| `HealthStatus` | interface | Mirrors `HealthStatus` from `mother_agent.py`. Fields: `agents` (Record\<string, string\>), `budgetRemaining` (number), `retriesUsed` (number), `circuitBreaker` (CircuitBreakerState), `uptimeMs` (number), `activeNode` (string or null). |
| `StreamEventType` | union type | Discriminated union: `"trace"`, `"health"`, `"result"`, `"error"`, `"circuit_break"`. Used by SSE parser. |

**Dependencies (Imports)**

| Imported From | Symbols Used |
|---|---|
| (none) | This file has zero dependencies. It is the leaf of the dependency tree. All other frontend files import from it. |

---

## 3.2 Error Handling Strategy (Global Circuit Breaker)

### Overview

The Agentic Hallucination Guardrail implements a 4-level circuit breaker strategy inspired by Michael Nygard's "Release It!" stability patterns. Each level represents an escalating scope of failure, with increasingly aggressive responses. The design principle is: **never show a blank screen, never silently fail, and never exceed the cost budget**.

```
                    +---------------------------+
                    |   Level 4: GLOBAL         |
                    |   Cost / Total Retries    |
                    +---------------------------+
                              |
                    +---------------------------+
                    |   Level 3: SWARM          |
                    |   Loop Detection          |
                    +---------------------------+
                              |
                    +---------------------------+
                    |   Level 2: NODE           |
                    |   Low Confidence Output   |
                    +---------------------------+
                              |
                    +---------------------------+
                    |   Level 1: AGENT          |
                    |   Single Agent Failure    |
                    +---------------------------+
```

---

### 3.2.1 Level 1 -- Agent-Level Circuit Breaker

| Attribute | Detail |
|---|---|
| **Scope** | Single agent (Retriever, Generator, Critic, or Evaluator) |
| **Purpose** | Handle transient failures in individual agent execution without disrupting the pipeline |

**Trigger Conditions**

| Condition | Threshold | Example |
|---|---|---|
| Agent raises an unhandled exception | Any exception | Ollama connection refused, LLM API 500 error, JSON parse failure |
| Agent timeout | > 30 seconds (`timeout.agent_timeout_seconds`) | DeepSeek-R1 inference hangs due to GPU memory pressure |
| Agent returns malformed output | Schema validation failure | Critic returns a string instead of `CritiqueResult` |
| Agent returns empty output | `None` or empty string for required fields | Generator returns `""` for `generated_response` |

**Response Actions**

| Step | Action | Detail |
|---|---|---|
| 1 | Log the failure | Write to structured log: agent name, error type, error message, attempt number, elapsed time, state snapshot hash |
| 2 | Increment retry counter | `state.retry_count += 1` (agent-level counter, separate from global) |
| 3 | Modify parameters | Apply parameter perturbation: lower `temperature` by 0.1, reduce `max_tokens` by 20%, add explicit instruction "respond only with information from the provided context" |
| 4 | Re-invoke agent | Call the same agent with modified parameters |
| 5 | If retry succeeds | Continue pipeline normally. Log the recovery event. |
| 6 | If all 3 retries fail | Escalate to Level 2 (route to Corrector node with error context) |

**State Management During Escalation**

| State Field | Behavior |
|---|---|
| `retry_count` | Incremented on each retry. Reset to 0 when the agent eventually succeeds. |
| `trace_events` | A `TraceEvent` of type `RETRY` is appended for each retry attempt. |
| `circuit_breaker_state` | Remains `CLOSED` during Level 1 retries. |
| `partial_results` | Not affected. Previous node outputs are preserved. |

**Recovery Procedure**

| Scenario | Recovery |
|---|---|
| Transient network error (Ollama, LLM API) | Exponential backoff: 1s, 2s, 4s (with jitter). |
| Persistent error after 3 retries | Escalate to Level 2. The Corrector node receives the last valid state and the error context. |
| Timeout (agent killed) | Agent task is cancelled via `asyncio.wait_for` timeout. Resources are released. Error is logged with the state at the moment of timeout. |

**UI Behavior**

| Element | Behavior |
|---|---|
| `LiveTrace.tsx` | The active node shows a yellow retry icon with the attempt number (e.g., "Retry 2/3"). Edge to the node pulses amber. |
| `SkeletonLoader.tsx` | No change. The skeleton for downstream sections remains visible. |
| `CircuitBreaker.tsx` | Not rendered. Level 1 is handled silently from the user's perspective unless they are watching the live trace. |
| `ConfidenceGauge.tsx` | Not updated. Gauge remains in its previous state (or skeleton). |

---

### 3.2.2 Level 2 -- Node-Level Circuit Breaker

| Attribute | Detail |
|---|---|
| **Scope** | A pipeline node (graph engine node) that has produced output but of insufficient quality |
| **Purpose** | Catch low-confidence or partially valid outputs and route them through the correction loop before they pollute downstream nodes |

**Trigger Conditions**

| Condition | Threshold | Example |
|---|---|---|
| Critic confidence below partial threshold | `confidence < 0.60` (`confidence_thresholds.critic_partial`) | Critic returns `{ verdict: "REJECT", confidence: 0.42 }` |
| Evaluation composite score below pass threshold | `composite_score < 0.80` (`confidence_thresholds.evaluator_pass`) | Evaluator returns `{ composite_score: 0.71, verdict: "FAIL" }` |
| Banned pattern detected in response | Regex match against `banned_patterns` list | Response contains "As an AI language model" |
| Insufficient source citations | `len(context_docs) < required_sources.min_count` | Only 1 source retrieved when minimum is 2 |
| Source relevance below threshold | Any source has `relevance_score < 0.70` | Source with relevance 0.45 included in context |

**Response Actions**

| Step | Action | Detail |
|---|---|---|
| 1 | Log the quality failure | Write structured log: node name, confidence score, failed metrics, banned patterns matched (if any) |
| 2 | Route to Corrector node | The `should_retry()` conditional edge returns `"corrector"`. The Corrector receives the original query, the failed response, and the Critic's `suggested_corrections`. |
| 3 | Corrector generates revised response | The Corrector node re-invokes the Generator with explicit correction instructions and the Critic's feedback appended to the prompt. |
| 4 | Re-evaluate | The corrected response is routed back through the Critic and then the Evaluator. |
| 5 | If correction succeeds | Pipeline continues to output. Total correction count is logged. |
| 6 | If correction fails after max node retries (3) | Escalate to Level 3. |

**State Management During Escalation**

| State Field | Behavior |
|---|---|
| `retry_count` | Incremented for each correction cycle. Tracked separately as `node_retry_count`. |
| `generated_response` | Overwritten with the corrected version on each correction attempt. Previous versions are preserved in `trace_events` metadata. |
| `validation_result` | Updated with each new Critic evaluation. |
| `confidence_score` | Updated with each new evaluation. |
| `trace_events` | Events of type `RETRY` appended with metadata: `{ level: "NODE", correction_round: N }`. |
| `circuit_breaker_state` | Remains `CLOSED`. |

**Recovery Procedure**

| Scenario | Recovery |
|---|---|
| Low confidence, correctable | Corrector produces improved response. Pipeline resumes. Typical recovery in 1-2 correction rounds. |
| Banned pattern detected | Corrector prompt explicitly lists the banned patterns to avoid. Hard constraint, not soft guidance. |
| Insufficient sources | Re-invoke Retriever with broadened query (query expansion). If still insufficient, proceed with available sources and flag in the UI. |
| Persistent low quality | After 3 correction rounds without improvement, escalate to Level 3. |

**UI Behavior**

| Element | Behavior |
|---|---|
| `LiveTrace.tsx` | The Corrector node appears in the graph with a looping edge back to Critic. Loop count is displayed on the edge label. Active correction cycle pulses amber. |
| `ConfidenceGauge.tsx` | Gauge animates to the current (low) score. Color is yellow or red depending on the value. Tooltip shows "Correction in progress..." |
| `CircuitBreaker.tsx` | An amber warning banner appears at the top: "Response quality is being improved. Please wait..." Banner is dismissible. |
| `SkeletonLoader.tsx` | Downstream sections (source attribution, response panel) continue showing skeletons. |

---

### 3.2.3 Level 3 -- Swarm-Level Circuit Breaker

| Attribute | Detail |
|---|---|
| **Scope** | The entire agent swarm (all agents managed by the Mother Agent) |
| **Purpose** | Detect and break infinite loops, oscillating states, and deadlocks where agents repeatedly produce the same output |

**Trigger Conditions**

| Condition | Threshold | Example |
|---|---|---|
| State hash collision detected | `hash(state_n) == hash(state_n-k)` for any `k` in `[1, loop_detection_window]` | The Corrector produces the exact same response twice in a row. State hash matches a hash seen 2 iterations ago. |
| Oscillating confidence | Confidence alternates between two values for > 2 cycles | Score oscillates: 0.58 -> 0.72 -> 0.58 -> 0.72 (same hash both times). |
| Correction loop with no improvement | Composite score does not improve by > 0.05 across 2 consecutive correction rounds | Round 1: 0.62, Round 2: 0.63, Round 3: 0.61. Delta < 0.05 threshold. |
| Agent conflict deadlock | Critic and Evaluator produce contradictory verdicts for > 2 cycles | Critic says ACCEPT (confidence 0.87), Evaluator says FAIL (composite 0.74), repeated twice. |

**Response Actions**

| Step | Action | Detail |
|---|---|---|
| 1 | Detect the loop | `compute_state_hash(state)` is called after every node. The hash is compared against the last `loop_detection_window` (default 5) hashes stored in a ring buffer. |
| 2 | Kill the branch | `MotherAgent.kill_branch(branch_id, reason)` is called. All pending async tasks for this branch are cancelled. |
| 3 | Log the loop | Structured log entry: loop type (exact match / oscillation / stagnation), state hashes involved, number of iterations before detection, full state snapshot at the moment of kill. |
| 4 | Preserve partial results | The best state seen so far (highest composite score) is saved as `partial_results`. |
| 5 | Emit trace event | A `TraceEvent` of type `CIRCUIT_BREAK` is emitted with metadata: `{ level: "SWARM", reason: "...", best_score: N }`. |
| 6 | Attempt fallback | If the loop was in correction (Generator <-> Critic cycle), fall back to the best response seen so far and pass it directly to the Evaluator with a "PARTIAL" flag. |
| 7 | If fallback produces acceptable output | Pipeline completes with a warning. |
| 8 | If fallback fails | Escalate to Level 4. |

**State Management During Escalation**

| State Field | Behavior |
|---|---|
| `circuit_breaker_state` | Transitions to `OPEN`. |
| `partial_results` | Set to the best state snapshot seen during the loop. |
| `trace_events` | `CIRCUIT_BREAK` event appended. All previous events preserved for debugging. |
| `retry_count` | Frozen at current value. No more retries attempted unless fallback triggers a new attempt. |
| `state_hash` | Ring buffer is cleared after the loop is broken. |

**Recovery Procedure**

| Scenario | Recovery |
|---|---|
| Fallback succeeds | The best-so-far response is used with a "PARTIAL" verdict. UI shows a warning but displays the response. Circuit breaker transitions to `HALF_OPEN` after `half_open_retry_after_seconds`. |
| Fallback fails | Escalate to Level 4. No further automatic recovery. |
| Half-open test | After the cooldown period, the next query will be treated as a test. If it succeeds without looping, circuit breaker transitions back to `CLOSED`. If it loops again, it immediately re-opens. |

**UI Behavior**

| Element | Behavior |
|---|---|
| `LiveTrace.tsx` | The looping edge turns red. A "Loop Detected" label appears on the edge. The killed branch nodes are grayed out with a strikethrough. |
| `CircuitBreaker.tsx` | Red warning banner: "A processing loop was detected and stopped. Showing best available results." Error details section shows the loop type and iteration count. |
| `ConfidenceGauge.tsx` | Gauge shows the score of the best partial result. Color reflects the actual score (likely yellow/red). Tooltip: "Partial result -- loop detected." |
| `SourceAttribution.tsx` | Shows sources from the partial result if available. Cards are marked with a "partial" badge. |
| `Dashboard.tsx` | `SkeletonLoader` sections for unresolved components are replaced with a "Not available" placeholder. |

---

### 3.2.4 Level 4 -- Global Circuit Breaker

| Attribute | Detail |
|---|---|
| **Scope** | The entire system. Full stop. |
| **Purpose** | Absolute safety net. Prevents runaway costs, infinite processing, and resource exhaustion. This is the nuclear option. |

**Trigger Conditions**

| Condition | Threshold | Example |
|---|---|---|
| Cost exceeds budget | `token_budget.cost_ceiling_usd` exceeded (default: `$0.00`) | In portfolio demo mode, any API call that would incur cost triggers this. In production, this would be a real dollar threshold. |
| Token budget exhausted | `token_budget_remaining <= 0` | Query has consumed all 50,000 allocated tokens across all agents. |
| Total retries exceeded | Global retry counter > `max_retries.global` (default: 10) | 10 total retries across all levels have been attempted. |
| Pipeline timeout | Total elapsed time > `timeout.total_pipeline_timeout_seconds` (default: 120s) | The entire pipeline has been running for over 2 minutes. |
| Unrecoverable system error | Critical infrastructure failure | Ollama server process died, vector store is unreachable, out of GPU memory. |

**Response Actions**

| Step | Action | Detail |
|---|---|---|
| 1 | FULL STOP | All agent tasks are immediately cancelled. No further LLM calls are made. No further retries are attempted. |
| 2 | Preserve everything | Complete state snapshot is saved: all `trace_events`, all `partial_results`, the `TokenLedger` with every call logged, the exact trigger condition. |
| 3 | Emit final event | SSE stream receives a `circuit_break` event with `level: "GLOBAL"` and the complete state. The stream is then closed gracefully. |
| 4 | Log for post-mortem | Full structured log entry: trigger condition, total tokens consumed, total cost, total time elapsed, number of retries per level, state hash history, all agent health statuses. |
| 5 | Display partial results | Whatever is available is packaged and sent to the UI. This may be as little as "query received, no results" or as much as "here are the sources and a partially-evaluated response." |
| 6 | No automatic recovery | Level 4 does not auto-recover. The user must explicitly start a new query. The circuit breaker remains `OPEN` until manually or time-based reset. |

**State Management During Escalation**

| State Field | Behavior |
|---|---|
| `circuit_breaker_state` | Immediately set to `OPEN`. |
| `partial_results` | Set to the best available state at the moment of trigger. |
| `trace_events` | Final `CIRCUIT_BREAK` event appended with `level: "GLOBAL"`. |
| `token_budget_remaining` | Frozen. May be negative if the trigger was an exceeded budget. |
| All async tasks | Cancelled via `asyncio.CancelledError`. |

**Recovery Procedure**

| Scenario | Recovery |
|---|---|
| Cost ceiling hit | The system remains paused. A new query can only proceed after the budget is reset or increased via configuration. In demo mode, this means switching to a mocked/cached response path. |
| Token budget exhausted | New query starts with a fresh budget. No carry-over of deficit. |
| Total retries exceeded | New query starts with a fresh retry counter. |
| Pipeline timeout | New query starts with a fresh timer. |
| Infrastructure failure | System runs health checks every 10 seconds. Once all agents report healthy, the circuit breaker transitions to `HALF_OPEN`. Next query is a test. |

**UI Behavior**

| Element | Behavior |
|---|---|
| `CircuitBreaker.tsx` | Full-screen overlay with red banner: **"System paused for safety. Here's what we know so far."** The `SafetyMessage` component is rendered. No retry button. No dismiss button. Partial results are displayed below the banner via `PartialResultsPanel`. |
| `LiveTrace.tsx` | All nodes are frozen in their last state. The entire graph has a red border. A "STOPPED" label appears at the top. |
| `ConfidenceGauge.tsx` | If a score is available, it is displayed with the actual color. If no score exists, the gauge shows "N/A" in gray. |
| `SourceAttribution.tsx` | If sources were retrieved, they are displayed with "partial" badges. If no sources exist, the section shows "Sources not available." |
| `Dashboard.tsx` | All skeleton sections that never received data are replaced with "Not available -- system paused" messages. The query input is re-enabled so the user can try a new query. |

---

### 3.2.5 Cross-Cutting Concerns

#### Loop Detection

| Attribute | Detail |
|---|---|
| **Algorithm** | Hash-based state comparison. After every node execution, `compute_state_hash(state)` computes a SHA-256 hash of the mutable fields: `generated_response`, `confidence_score`, `validation_result.verdict`, `retry_count`. |
| **Comparison Window** | The last `loop_detection_window` (default: 5) hashes are stored in a ring buffer. The current hash is compared against all entries. |
| **Match Condition** | If `hash(state_n) == hash(state_n-k)` for any `k` in `[1, window]`, a loop is detected. |
| **Optimization** | Hash comparison is O(window) per node execution. With a window of 5, this is negligible overhead. |
| **Edge Case: Near-Misses** | Hashing only catches exact state matches. Oscillating states with tiny differences (e.g., confidence 0.580001 vs 0.580002) are caught by the separate "no improvement" check (delta < 0.05 over 2 rounds). |

#### Token Budget

| Attribute | Detail |
|---|---|
| **Tracking** | The `TokenLedger` in `MotherAgent` records every LLM call: agent name, model, input tokens, output tokens, estimated cost, timestamp. |
| **Enforcement** | Before every LLM call, `MotherAgent.enforce_budget(state)` checks the remaining budget. If the projected cost of the next call would exceed the remaining budget, the call is blocked and Level 4 is triggered. |
| **Projection** | Projected cost is estimated conservatively using the model's max output token setting and the known input token count. This ensures the budget is never exceeded even if the model generates a maximum-length response. |
| **Hard Ceiling** | `max_tokens_per_query` is an absolute limit. `cost_ceiling_usd` is an absolute limit. Both are checked. |
| **Per-Query Isolation** | Each query gets its own budget. There is no cross-query budget sharing. |
| **Demo Mode** | With `cost_ceiling_usd = 0.00`, the system operates entirely on cached/mocked responses or local models (DeepSeek-R1 via Ollama, which has zero API cost). |

#### Timeout Enforcement

| Attribute | Detail |
|---|---|
| **Agent-Level** | Every agent call is wrapped in `asyncio.wait_for(task, timeout=30)`. If the timeout fires, `asyncio.TimeoutError` is raised and the task is cancelled. |
| **Pipeline-Level** | The entire `MotherAgent.run()` call is wrapped in `asyncio.wait_for(task, timeout=120)`. This is the outer safety net. |
| **Clock Source** | `time.monotonic()` is used for all timing to avoid issues with system clock adjustments. |
| **Timeout Logging** | Every timeout event logs: agent name, elapsed time, state at timeout, whether the timeout was agent-level or pipeline-level. |

#### Graceful Degradation

| Principle | Implementation |
|---|---|
| **Never show a blank screen** | The `SkeletonLoader` is always rendered first. Components are progressively revealed as data arrives. If the pipeline fails, skeletons are replaced with "Not available" messages, never with empty space. |
| **Always show partial results** | The `PartialResultsPanel` in `CircuitBreaker.tsx` displays whatever data was collected before the failure. Even if only the query was processed, the UI shows "Your query was received. Processing was interrupted." |
| **Always explain what happened** | Every circuit breaker level produces a human-readable explanation. Technical details are available in an expandable section for power users. |
| **Never silently retry forever** | All retry loops have hard limits. All timeouts are enforced. The user is always informed when retries are happening (via `LiveTrace.tsx`). |
| **Preserve user trust** | Low-confidence results are always labeled as such. Partial results carry visible warnings. The confidence gauge never shows a misleadingly high score. |

---

## 3.3 File Dependency Graph

### Text-Based Dependency Graph

```
Legend:
  ──────>  imports from / depends on
  -------> data flow (runtime, not import)
  [B]      Backend (Python)
  [F]      Frontend (TypeScript/React)
  [C]      Configuration (JSON)

                    ┌──────────────────────────────┐
                    │   validation_rules.json [C]   │
                    │   (Zero dependencies)         │
                    └──────────────┬────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                     │
              v                    v                     v
   ┌───────────────────┐ ┌──────────────────┐ ┌──────────────────┐
   │ critic_agent.py   │ │ evaluator.py     │ │ mother_agent.py  │
   │ [B]               │ │ [B]              │ │ [B]              │
   │                   │ │                  │ │                  │
   │ Imports:          │ │ Imports:         │ │ Imports:         │
   │  - httpx          │ │  - ragas         │ │  - graph_engine  │
   │  - validation_    │ │  - deepeval      │ │  - critic_agent  │
   │    rules.json     │ │  - validation_   │ │  - evaluator     │
   └───────┬───────────┘ │    rules.json    │ │  - validation_   │
           │              └────────┬─────────┘ │    rules.json    │
           │                       │           └────────┬─────────┘
           │                       │                    │
           v                       v                    v
   ┌──────────────────────────────────────────────────────────────┐
   │                     graph_engine.py [B]                      │
   │                                                              │
   │  Imports:                                                    │
   │   - langgraph                                                │
   │   - mother_agent (callback registration)                    │
   │   - critic_agent (critique invocation)                      │
   │   - evaluator (scoring invocation)                          │
   │   - validation_rules.json (threshold loading)               │
   │                                                              │
   │  Note: Circular dependency between graph_engine and          │
   │  mother_agent is resolved via DEPENDENCY INJECTION.          │
   │  mother_agent passes callbacks at build time;                │
   │  graph_engine does NOT import mother_agent at module level.  │
   │                                                              │
   │  Resolution pattern:                                         │
   │    # graph_engine.py                                         │
   │    def build_graph(budget_callback=None, health_callback=None):│
   │        # Uses callbacks without importing mother_agent       │
   │                                                              │
   │    # mother_agent.py                                         │
   │    from graph_engine import build_graph                      │
   │    graph = build_graph(                                      │
   │        budget_callback=self.enforce_budget,                  │
   │        health_callback=self.health_check                     │
   │    )                                                         │
   │  This breaks the import cycle while preserving type safety   │
   │  via Protocol classes (PEP 544) for callback signatures.     │
   └──────────────────────────┬───────────────────────────────────┘
                              │
                    (Python backend boundary)
                              │
                   ┌──────────┴──────────┐
                   │  HTTP / SSE Bridge  │
                   └──────────┬──────────┘
                              │
                    (TypeScript frontend boundary)
                              │
                    ┌─────────v──────────┐
                    │ types/index.ts [F] │
                    │ (Zero dependencies)│
                    └─────────┬──────────┘
                              │
           ┌──────────────────┼──────────────────┐
           │                  │                   │
           v                  v                   v
  ┌─────────────────┐ ┌───────────────┐ ┌─────────────────────┐
  │ api/stream.ts   │ │ hooks/        │ │ App_4K_Responsive   │
  │ [F]             │ │ useAgent      │ │ .css [F]            │
  │                 │ │ Stream.ts [F] │ │ (Zero dependencies) │
  │ Imports:        │ │               │ └──────────┬──────────┘
  │  - types/index  │ │ Imports:      │            │
  └────────┬────────┘ │  - types/     │            │
           │          │    index      │            │
           │          └───────┬───────┘            │
           │                  │                    │
           │    ┌─────────────┘                    │
           │    │                                  │
           v    v                                  │
  ┌─────────────────────────────────────┐          │
  │        Dashboard.tsx [F]            │<─────────┘
  │                                     │
  │  Imports:                           │
  │   - hooks/useAgentStream            │
  │   - types/index                     │
  │   - App_4K_Responsive.css           │
  │   - SkeletonLoader                  │
  │   - LiveTrace                       │
  │   - ConfidenceGauge                 │
  │   - SourceAttribution               │
  │   - CircuitBreaker                  │
  └──────────────┬──────────────────────┘
                 │
                 │ imports
                 │
    ┌────────────┼──────────────┬──────────────────┬──────────────────┐
    │            │              │                  │                  │
    v            v              v                  v                  v
┌──────────┐┌──────────┐┌──────────────┐┌──────────────────┐┌──────────────┐
│ Skeleton ││ Live     ││ Confidence   ││ Source           ││ Circuit      │
│ Loader   ││ Trace    ││ Gauge.tsx    ││ Attribution.tsx  ││ Breaker.tsx  │
│ .tsx [F] ││ .tsx [F] ││ [F]         ││ [F]             ││ [F]          │
│          ││          ││             ││                 ││              │
│ Imports: ││ Imports: ││ Imports:    ││ Imports:        ││ Imports:     │
│ - types  ││ - types  ││ - types    ││ - types         ││ - types      │
│ - css    ││ - css    ││ - css      ││ - css           ││ - css        │
│ - framer ││ - framer ││ - framer   ││ - framer        ││ - framer     │
│          ││ - hook   ││            ││                 ││ - hook       │
└──────────┘└──────────┘└──────────────┘└──────────────────┘└──────────────┘
```

### Import Relationship Matrix

This matrix shows which file imports from which. Read as: **Row imports from Column**.

| Importer (Row) | `validation_rules.json` | `graph_engine.py` | `mother_agent.py` | `critic_agent.py` | `evaluator.py` | `types/index.ts` | `api/stream.ts` | `hooks/useAgentStream.ts` | `App_4K_Responsive.css` | `SkeletonLoader.tsx` | `LiveTrace.tsx` | `ConfidenceGauge.tsx` | `SourceAttribution.tsx` | `CircuitBreaker.tsx` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **graph_engine.py** | YES | -- | callback | YES | YES | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| **mother_agent.py** | YES | YES | -- | YES | YES | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| **critic_agent.py** | YES | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| **evaluator.py** | YES | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| **api/stream.ts** | -- | -- | -- | -- | -- | YES | -- | -- | -- | -- | -- | -- | -- | -- |
| **hooks/useAgentStream.ts** | -- | -- | -- | -- | -- | YES | -- | -- | -- | -- | -- | -- | -- | -- |
| **SkeletonLoader.tsx** | -- | -- | -- | -- | -- | YES | -- | -- | YES | -- | -- | -- | -- | -- |
| **LiveTrace.tsx** | -- | -- | -- | -- | -- | YES | -- | YES | YES | -- | -- | -- | -- | -- |
| **ConfidenceGauge.tsx** | -- | -- | -- | -- | -- | YES | -- | -- | YES | -- | -- | -- | -- | -- |
| **SourceAttribution.tsx** | -- | -- | -- | -- | -- | YES | -- | -- | YES | -- | -- | -- | -- | -- |
| **CircuitBreaker.tsx** | -- | -- | -- | -- | -- | YES | -- | YES | YES | -- | -- | -- | -- | -- |
| **Dashboard.tsx** | -- | -- | -- | -- | -- | YES | -- | YES | YES | YES | YES | YES | YES | YES |

### Data Flow (Runtime)

```
User Query
    │
    v
Dashboard.tsx ──> api/stream.ts ──> [HTTP] ──> mother_agent.py
                                                     │
                                                     v
                                              graph_engine.py
                                                     │
                                    ┌────────────────┼────────────────┐
                                    v                v                v
                             retriever_node   generator_node   (conditional)
                                    │                │                │
                                    v                v                v
                             critic_agent.py  corrector_node   evaluator.py
                                    │                │                │
                                    v                v                v
                             CritiqueResult   Corrected Resp   EvaluationResult
                                    │                │                │
                                    └────────────────┼────────────────┘
                                                     │
                                                     v
                                              GuardrailState
                                                     │
                                            (SSE TraceEvents)
                                                     │
                                                     v
                                    hooks/useAgentStream.ts
                                                     │
                          ┌──────────┬───────────────┼──────────────┬───────────┐
                          v          v               v              v           v
                     LiveTrace  Confidence    SourceAttrib.   CircuitBrkr  Skeleton
                     .tsx       Gauge.tsx     .tsx            .tsx         Loader.tsx
```

---

## 3.4 Implementation Priority Order

### Build Order Rationale

The build order is determined by the dependency graph. Files with zero or fewer dependencies are built first. Files that depend on earlier files are built later. Within the same priority tier, files can be built in parallel.

### Priority Tiers

#### Tier P0 -- Critical Path (Backend Orchestration)

These files form the backbone of the system. Nothing else functions without them.

| Order | File | Justification | Blocked By | Blocks |
|---|---|---|---|---|
| **0.1** | `validation_rules.json` | Zero dependencies. All other backend files read from this. Must exist first even though it is listed as P2 by feature priority -- it is P0 by dependency order. | Nothing | `graph_engine.py`, `mother_agent.py`, `critic_agent.py`, `evaluator.py` |
| **0.2** | `graph_engine.py` | Defines the state schema (`GuardrailState`) and the graph structure. All nodes reference this schema. Must be built before `mother_agent.py` because the Mother Agent wraps the compiled graph. | `validation_rules.json` | `mother_agent.py` |
| **0.3** | `mother_agent.py` | Orchestrates everything. Cannot function without the graph engine. Must be built after `graph_engine.py` and alongside `critic_agent.py`/`evaluator.py` (stubs acceptable initially). | `graph_engine.py`, `validation_rules.json` | `api/stream.ts` (runtime dependency) |

**Milestone: Backend skeleton is runnable with stub nodes.**

---

#### Tier P1 -- Core Features (Backend Agents & Evaluation)

These files implement the actual intelligence of the system. They can be built in parallel once P0 is complete.

| Order | File | Justification | Blocked By | Blocks |
|---|---|---|---|---|
| **1.1** | `critic_agent.py` | Can be built independently once the `CritiqueResult` schema exists (defined in P0). Requires a running Ollama instance for integration testing but can be unit-tested with mocks. | `validation_rules.json` | `graph_engine.py` (full integration) |
| **1.2** | `evaluator.py` | Can be built independently once the `EvaluationResult` schema exists (defined in P0). Requires RAGAS and DeepEval installed but can be unit-tested with mocks. | `validation_rules.json` | `graph_engine.py` (full integration) |

**Milestone: All backend agents are implemented. Full pipeline can be integration-tested end-to-end.**

---

#### Tier P2 -- Frontend Foundation (Types, API, Hooks, Styles)

These files establish the frontend infrastructure. They must be built before any UI components.

| Order | File | Justification | Blocked By | Blocks |
|---|---|---|---|---|
| **2.1** | `types/index.ts` | Zero frontend dependencies. All frontend files import from this. Must be the first frontend file created. | Nothing (mirrors backend schemas from P0) | All `.tsx` files, `api/stream.ts`, `hooks/useAgentStream.ts` |
| **2.2** | `App_4K_Responsive.css` | Zero dependencies. All UI components use its classes. | Nothing | All `.tsx` files |
| **2.3** | `api/stream.ts` | Depends only on `types/index.ts`. The bridge between backend and frontend. | `types/index.ts` | `hooks/useAgentStream.ts` |
| **2.4** | `hooks/useAgentStream.ts` | Depends on `types/index.ts` and consumes `api/stream.ts` at runtime. All live UI components depend on this hook. | `types/index.ts`, `api/stream.ts` | `LiveTrace.tsx`, `CircuitBreaker.tsx`, `Dashboard.tsx` |

**Milestone: Frontend can connect to backend SSE stream and receive typed events.**

---

#### Tier P3 -- Frontend UI Components (Leaf Components)

These components can be built in parallel. They depend on P2 infrastructure but not on each other (except through `Dashboard.tsx` composition).

| Order | File | Justification | Blocked By | Blocks |
|---|---|---|---|---|
| **3.1** | `SkeletonLoader.tsx` | Leaf component. Depends on `types/index.ts` and `App_4K_Responsive.css`. No dependency on the SSE stream (renders statically until data arrives). Build first because it is the first thing the user sees. | `types/index.ts`, `App_4K_Responsive.css` | `Dashboard.tsx` |
| **3.2** | `ConfidenceGauge.tsx` | Leaf component. Depends on `types/index.ts` and `App_4K_Responsive.css`. Can be developed and tested in isolation with mock data. | `types/index.ts`, `App_4K_Responsive.css` | `Dashboard.tsx` |
| **3.3** | `SourceAttribution.tsx` | Leaf component. Depends on `types/index.ts` and `App_4K_Responsive.css`. Can be developed and tested in isolation with mock data. | `types/index.ts`, `App_4K_Responsive.css` | `Dashboard.tsx` |
| **3.4** | `LiveTrace.tsx` | Depends on `types/index.ts`, `App_4K_Responsive.css`, and `hooks/useAgentStream.ts`. Requires the SSE hook for live data but can be developed with a mock hook. | `types/index.ts`, `App_4K_Responsive.css`, `hooks/useAgentStream.ts` | `Dashboard.tsx` |
| **3.5** | `CircuitBreaker.tsx` | Depends on `types/index.ts`, `App_4K_Responsive.css`, and `hooks/useAgentStream.ts`. Requires the SSE hook for circuit breaker state changes. | `types/index.ts`, `App_4K_Responsive.css`, `hooks/useAgentStream.ts` | `Dashboard.tsx` |

**Milestone: All individual UI components are implemented and testable in isolation (Storybook or equivalent).**

---

#### Tier P4 -- Frontend Composition (Dashboard)

The final assembly step. All components are composed into the dashboard.

| Order | File | Justification | Blocked By | Blocks |
|---|---|---|---|---|
| **4.1** | `Dashboard.tsx` | Depends on every other frontend file. Must be built last. This is the integration point where all components are wired together with live data from the SSE stream. | All P2 and P3 files | Nothing (this is the root component) |

**Milestone: Full frontend is assembled. End-to-end demo is possible.**

---

### Implementation Timeline Summary

```
Week 1 (Days 1-3)     Week 1 (Days 4-5)     Week 2 (Days 1-3)     Week 2 (Days 4-5)
─────────────────     ─────────────────     ─────────────────     ─────────────────
P0: Critical Path     P1: Core Features     P2: FE Foundation     P3-P4: FE UI
                                            + P3: Leaf Components

┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ validation_  │      │ critic_      │      │ types/       │      │ LiveTrace    │
│ rules.json   │      │ agent.py     │      │ index.ts     │      │ .tsx         │
├──────────────┤      ├──────────────┤      ├──────────────┤      ├──────────────┤
│ graph_       │      │ evaluator.py │      │ App_4K_      │      │ Circuit      │
│ engine.py    │      │              │      │ Responsive   │      │ Breaker.tsx  │
├──────────────┤      │              │      │ .css         │      ├──────────────┤
│ mother_      │      │              │      ├──────────────┤      │ Dashboard    │
│ agent.py     │      │              │      │ api/stream   │      │ .tsx         │
│              │      │              │      │ .ts          │      │              │
│              │      │              │      ├──────────────┤      │              │
│              │      │              │      │ useAgent     │      │              │
│              │      │              │      │ Stream.ts    │      │              │
│              │      │              │      ├──────────────┤      │              │
│              │      │              │      │ Skeleton     │      │              │
│              │      │              │      │ Loader.tsx   │      │              │
│              │      │              │      ├──────────────┤      │              │
│              │      │              │      │ Confidence   │      │              │
│              │      │              │      │ Gauge.tsx    │      │              │
│              │      │              │      ├──────────────┤      │              │
│              │      │              │      │ Source       │      │              │
│              │      │              │      │ Attrib.tsx   │      │              │
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘

BE Integration        BE E2E Tests          FE Component Tests    FE Integration
Testing               + Bug Fixes           (Storybook)           + E2E Demo
```

### Critical Path Visualization

The longest dependency chain determines the minimum build time:

```
validation_rules.json
        │
        v
graph_engine.py
        │
        v
mother_agent.py ──────────────> api/stream.ts (runtime)
                                      │
                                      v
                              hooks/useAgentStream.ts
                                      │
                                      v
                                LiveTrace.tsx
                                      │
                                      v
                                Dashboard.tsx
```

**Critical path length: 7 files in series.** All other files can be built in parallel with items on this chain.

### Sprint Timeline Mapping

The implementation priority tiers map to specific sprints in the project roadmap:

| Sprint | Priority Tiers | Deliverables | Target |
|--------|---------------|--------------|--------|
| Sprint 6 | P0 + P1 | `graph_engine.py`, `mother_agent.py`, `critic_agent.py`, `evaluator.py`, `validation_rules.json` | Backend skeleton runnable; all agents implemented |
| Sprint 7 | P2 | `types/index.ts`, `App_4K_Responsive.css`, `api/stream.ts`, `hooks/useAgentStream.ts` | Frontend infrastructure; SSE bridge functional |
| Sprint 8 | P3 | `SkeletonLoader.tsx`, `LiveTrace.tsx`, `ConfidenceGauge.tsx`, `SourceAttribution.tsx`, `CircuitBreaker.tsx` | All leaf UI components testable in isolation |
| Sprint 9 | P4 | `Dashboard.tsx` (composition) + full integration testing + performance tuning | End-to-end demo; all quality gates pass |

> **Cross-reference:** See `sprint-6/testing-strategy.md` for the test plan that accompanies each sprint, and `sprint-3/ci-cd-spec.md` for the CI pipeline that gates each merge.

---

*End of Sprint 3 File Manifest. This document is a roadmap only. No code is included. All file contents, implementations, and tests will be produced in Sprint 6 per the priority order defined in Section 3.4.*
