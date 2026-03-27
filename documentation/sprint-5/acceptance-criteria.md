# Sprint 5 -- User Needs & Acceptance Criteria

## Agentic Hallucination Guardrail (LLMOps)

| Field | Value |
|---|---|
| **Project** | Agentic Hallucination Guardrail |
| **Sprint** | 5 |
| **Document Type** | User Needs & Acceptance Criteria (Roadmap Only -- NO Code) |
| **Status** | Draft |
| **Last Updated** | 2026-03-21 |

### Guiding Principle

> **Every feature exists to serve these user needs. If a feature doesn't map to a need below, it doesn't ship.**

No orphan features. No speculative work. Every line of code traces back to a row in this document.

---

## Table of Contents

- [5.1 Trust & Transparency](#51-trust--transparency)
  - [5.1.1 Confidence Score](#511-confidence-score----can-i-trust-this-answer)
  - [5.1.2 Source Attribution](#512-source-attribution----where-did-this-come-from)
  - [5.1.3 Correction History](#513-correction-history----what-if-the-ai-is-wrong)
  - [5.1.4 Live Trace](#514-live-trace----is-the-system-working)
- [5.2 Reliability & Safety](#52-reliability--safety)
  - [5.2.1 Cost Ceiling & Circuit Breaker](#521-cost-ceiling--circuit-breaker----will-this-cost-me-money)
  - [5.2.2 Loop Detection & Fallback](#522-loop-detection--fallback----what-if-it-gets-stuck)
  - [5.2.3 Local Inference](#523-local-inference----is-my-data-safe)
  - [5.2.4 State Persistence](#524-state-persistence----what-if-the-system-crashes)
- [5.3 Usability & Experience](#53-usability--experience)
  - [5.3.1 Loading Feedback](#531-loading-feedback----i-hate-waiting-with-no-feedback)
  - [5.3.2 4K Responsive Design](#532-4k-responsive-design----it-looks-broken-on-my-screen)
  - [5.3.3 Mobile-First Design](#533-mobile-first-design----i-cant-use-this-on-my-phone)
  - [5.3.4 Dashboard Clarity](#534-dashboard-clarity----i-need-to-understand-quickly)
- [5.4 Performance](#54-performance)
  - [5.4.1 Inference Speed](#541-inference-speed----its-too-slow)
  - [5.4.2 Page Load Performance](#542-page-load-performance----the-page-takes-forever-to-load)
  - [5.4.3 Streaming Results](#543-streaming-results----results-appear-all-at-once)
- [5.5 User Experience Enhancements](#55-user-experience-enhancements)
  - [5.5.1 Multi-Turn Conversation Threading](#551-multi-turn-conversation-threading)
  - [5.5.2 Webhook / Slack Alert Integration](#552-webhook--slack-alert-integration)
  - [5.5.3 Model Selector Dropdown](#553-model-selector-dropdown)
  - [5.5.4 Prompt Version Management](#554-prompt-version-management)
  - [5.5.5 Annotation / Comment System](#555-annotation--comment-system)
- [5.6 Feature-to-Need Traceability Matrix](#56-feature-to-need-traceability-matrix)
- [5.7 Quality Gates](#57-quality-gates)

---

## 5.1 Trust & Transparency

Users interacting with AI-generated outputs need mechanisms to evaluate, verify, and challenge what the system tells them. Trust is not assumed -- it is earned through transparency at every layer.

---

### 5.1.1 Confidence Score -- "Can I trust this answer?"

| Attribute | Detail |
|---|---|
| **User Need** | "Can I trust this answer?" |
| **Solution** | Confidence Score (0-100%) displayed prominently |
| **Component** | `ConfidenceGauge.tsx` |
| **Priority** | P0 -- Critical |

#### User Persona & Scenario

**Persona: Fatima, ML Engineer (Primary)**
Fatima is reviewing LLM-generated responses in a pipeline she manages. She does not have time to manually verify every output. She needs an at-a-glance signal that tells her how much the system trusts its own answer, so she can focus her manual review effort on low-confidence outputs and move fast on high-confidence ones.

**Persona: Derek, Engineering Manager (Secondary)**
Derek is evaluating whether to deploy this guardrail system to his team. He needs to see that the system is self-aware about its own limitations. A confidence score gives him evidence that the system does not treat all outputs as equally reliable.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| CS-01 | A query has been processed through the full agent pipeline (inference, critic evaluation, correction if needed) | The response is rendered in the dashboard | A confidence gauge is displayed prominently in the response card, showing a numerical percentage (0-100%) and a corresponding visual indicator (color-coded arc or bar) |
| CS-02 | The confidence score is below 50% | The response card renders | The gauge displays in red/warning color, and a disclaimer banner appears: "Low confidence -- review source material before relying on this output" |
| CS-03 | The confidence score is between 50% and 79% | The response card renders | The gauge displays in amber/caution color with no automatic disclaimer, but a subtle "Verify sources" link is visible |
| CS-04 | The confidence score is 80% or above | The response card renders | The gauge displays in green/healthy color with no additional warnings |
| CS-05 | The confidence score is exactly 0% | The response card renders | The gauge shows 0%, the entire response card is visually de-emphasized (reduced opacity or muted border), and the disclaimer reads: "The system could not validate this output. Do not rely on it." |
| CS-06 | The confidence score is exactly 100% | The response card renders | The gauge shows 100% without implying infallibility; a tooltip on hover reads: "High confidence based on internal validation. Independent verification is always recommended." |
| CS-07 | The user hovers over or clicks the confidence gauge | The tooltip/popover activates | A breakdown appears showing: (a) the claim count, (b) how many claims were verified, (c) how many were corrected, and (d) the scoring formula used |
| CS-08 | The system is still processing (streaming in progress) | Partial results are displayed | The confidence gauge shows an animated "calculating..." state and does not display a number until the critic agent has completed evaluation |
| CS-09 | The user navigates away from the dashboard and returns | The response card re-renders | The confidence score is persisted in localStorage keyed by `trace_id` and restored on page load. No re-evaluation is triggered. If localStorage is unavailable or the entry has been evicted, the gauge shows "Score unavailable — re-query to recalculate." |

#### Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| Critic agent times out before producing a score | Display "Score unavailable" with a retry button. Do not show 0% -- absence of a score is different from a score of zero. |
| Confidence score returned as a non-numeric value | Log the error, display "Score unavailable," and trigger an internal alert for debugging. |
| Multiple correction rounds produce different scores | Display the final score. The tooltip breakdown should show the progression (e.g., "Round 1: 42% -> Round 2: 78% -> Final: 78%"). |
| User has screen reader active | The gauge must announce: "[Score]% confidence. [Low/Medium/High] confidence rating." Color alone must not be the only indicator. |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Display Latency | Gauge renders within 200ms of score availability | Automated UI timing test |
| Accuracy of Score Display | Score displayed matches `critic_agent.py` output byte-for-byte | End-to-end integration test comparing API response to rendered value |
| User Comprehension | 80% of test users correctly interpret the score meaning in a 5-second task | Usability test with 5+ participants |
| Accessibility Compliance | WCAG 2.1 AA | axe-core automated audit + manual screen reader test |

---

### 5.1.2 Source Attribution -- "Where did this come from?"

| Attribute | Detail |
|---|---|
| **User Need** | "Where did this come from?" |
| **Solution** | Source Attribution with clickable citations |
| **Component** | `SourceAttribution.tsx` |
| **Priority** | P0 -- Critical |

#### User Persona & Scenario

**Persona: Priya, Data Scientist (Primary)**
Priya receives an LLM-generated summary of a research paper. She needs to verify specific claims against the original material. Inline citations let her click through to the exact passage that supports each claim, rather than re-reading the entire source document.

**Persona: Marcus, Compliance Officer (Secondary)**
Marcus needs an audit trail. When a stakeholder asks "where did the system get this information?", Marcus must be able to point to a specific, traceable source for every factual claim in the output.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| SA-01 | The agent pipeline has produced a response containing factual claims | The response renders in the dashboard | Each claim that has a traceable source displays an inline citation marker (e.g., superscript number [1], [2], etc.) |
| SA-02 | A citation marker is present in the response | The user clicks the citation marker | A popover or side panel opens showing: (a) the source document name/title, (b) the relevant excerpt from the source, (c) a confidence indicator for how well the claim matches the source |
| SA-03 | A claim has no identifiable source | The response renders | The claim is displayed without a citation marker, and it is visually annotated (e.g., italic text or a subtle "unsourced" label) to indicate it could not be traced |
| SA-04 | The response contains 5 or more citations | The user scrolls to the bottom of the response card | A "Sources" section appears listing all cited sources in order, with titles and one-line summaries |
| SA-05 | The user wants to see all unsourced claims at a glance | The user clicks "Show unsourced claims" toggle | All unsourced claims are highlighted in the response body, and a count is displayed (e.g., "3 of 12 claims unsourced") |
| SA-06 | The source is a local file on disk | The user clicks through to the source | The relevant file path is displayed. No attempt is made to open the file automatically (security). The excerpt is shown inline. |
| SA-07 | The user wants to export citations for academic use | The user clicks "Export Citations" | Citations are exported in the user's chosen format: BibTeX (`.bib`) or JSON (`.json`). Each citation includes: title, source URL, excerpt, relevance score, and access date. |
| SA-08 | The user wants to search within cited sources | The user types in the citation search bar | A fuzzy search (Fuse.js, threshold 0.3) filters the citation list in real time. Matches are highlighted. Search covers source title, excerpt text, and claim text. |

#### Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| Source document has been deleted or moved since indexing | Citation displays "Source unavailable" with the last-known file path. The claim remains visible but the link is disabled. |
| A single claim maps to multiple sources | Display all sources in the popover, ranked by relevance. Show count: "Supported by 3 sources." |
| The response contains zero factual claims (e.g., a purely procedural answer) | No citation markers appear. A note reads: "This response contains no factual claims requiring source attribution." |
| Citation text is extremely long (500+ characters) | Truncate to 200 characters with "Show full excerpt" expander. |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Citation Coverage | 90%+ of verifiable factual claims have at least one citation | Automated claim-extraction test against labeled dataset |
| Click-Through Accuracy | Clicking a citation leads to the correct source excerpt 100% of the time | Manual QA on 50 test responses |
| Render Performance | Citations do not add more than 50ms to response card render time | Lighthouse performance profiling |
| Accessibility | All citation markers are keyboard-navigable and screen-reader-announced | axe-core + manual NVDA/VoiceOver test |

---

### 5.1.3 Correction History -- "What if the AI is wrong?"

| Attribute | Detail |
|---|---|
| **User Need** | "What if the AI is wrong?" |
| **Solution** | Correction history -- show what was fixed and why |
| **Component** | `CorrectionLog.tsx` |
| **Priority** | P0 -- Critical |

#### User Persona & Scenario

**Persona: Aisha, Senior ML Engineer (Primary)**
Aisha is debugging why a particular response was flagged and corrected. She needs to see the before/after diff of every correction the system made, along with the critic agent's reasoning for each change. This lets her tune the system and understand its failure modes.

**Persona: Jordan, End User (Secondary)**
Jordan received a corrected response and wants to understand what changed. Seeing the correction log builds trust -- the system is not hiding its mistakes, it is showing its work.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| CL-01 | The agent pipeline corrected one or more claims in a response | The response card renders | A "Corrections" badge appears on the response card showing the count (e.g., "2 corrections made") |
| CL-02 | The user clicks the "Corrections" badge | The correction log panel opens | For each correction, the log displays: (a) the original claim (struck through), (b) the corrected claim (highlighted), (c) the reason for correction from the critic agent, (d) the confidence score before and after correction |
| CL-03 | No corrections were made to the response | The response card renders | No "Corrections" badge appears. If the user navigates to the log manually, it reads: "No corrections were needed for this response." |
| CL-04 | The same claim was corrected multiple times across rounds | The correction log is open | Each correction round is shown in chronological order with round labels (Round 1, Round 2, etc.), forming a visible audit trail |
| CL-05 | The user wants to export the correction log | The user clicks "Export" in the log panel | A JSON file is downloaded containing the full correction history with timestamps, original text, corrected text, and reasoning |
| CL-06 | A correction worsened the confidence score (score went down after a correction round) | The correction log is open | The entry is flagged with a warning icon and text: "This correction reduced confidence. Review recommended." |

#### Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| Correction reasoning from critic agent is empty or null | Display: "Correction was applied but no reasoning was provided by the critic agent." Log the anomaly internally. |
| Correction involves a very long claim (1000+ characters) | Show first 150 characters with "Expand" toggle for both original and corrected versions. |
| 10+ corrections in a single response | Show the first 5 with a "Show all N corrections" expander to avoid overwhelming the UI. |
| Correction log data is corrupted or malformed | Display: "Correction log could not be loaded. Raw data available for debugging." Offer raw JSON download. |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Log Completeness | 100% of corrections made by the pipeline appear in the log | Integration test: run 100 queries with known hallucinations, verify all corrections are logged |
| Diff Accuracy | Before/after text matches exactly what the pipeline produced | Byte-level comparison test between `mother_agent.py` output and `CorrectionLog.tsx` display |
| User Trust Impact | Users who view correction logs report higher trust scores (4+/5) than those who do not | A/B survey during usability testing |
| Export Integrity | Exported JSON is valid, parseable, and contains all displayed fields | Automated schema validation test on 50 exports |

---

### 5.1.4 Live Trace -- "Is the system working?"

| Attribute | Detail |
|---|---|
| **User Need** | "Is the system working?" |
| **Solution** | Live Trace -- real-time agent execution visualization |
| **Component** | `LiveTrace.tsx` |
| **Priority** | P1 -- High |

#### User Persona & Scenario

**Persona: Kai, DevOps/MLOps Engineer (Primary)**
Kai is monitoring the system in production. When a query takes longer than expected, Kai needs to see exactly which agent is running, what it is doing, and whether it is stuck. The live trace is Kai's real-time debugger.

**Persona: Fatima, ML Engineer (Secondary)**
Fatima is developing a new critic prompt. She uses the live trace to watch how the critic agent processes claims in real time, so she can iterate on the prompt without waiting for the full pipeline to complete.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| LT-01 | A query has been submitted and the agent pipeline is running | The user views the dashboard | A live trace panel shows the currently active agent (e.g., "Critic Agent -- Evaluating claim 3 of 7") with a pulsing activity indicator |
| LT-02 | The agent pipeline transitions from one agent to another (e.g., inference -> critic -> correction) | The transition occurs | The trace panel updates in real time (within 500ms) to reflect the new agent, with the previous agent marked as completed (checkmark) or failed (X) |
| LT-03 | An agent has been running for longer than its expected duration | The timeout threshold is exceeded | The trace panel highlights the agent in amber with text: "Running longer than expected ([elapsed] / [expected] seconds)" |
| LT-04 | The full pipeline completes | All agents have finished | The trace panel shows a summary: total time, agents executed, corrections made, final confidence score. A "Replay" button allows the user to step through the trace. |
| LT-05 | The user clicks on a completed agent step in the trace | The detail view opens | The user sees: (a) input to that agent, (b) output from that agent, (c) duration, (d) token count consumed |
| LT-06 | The pipeline fails mid-execution | An agent throws an error | The trace shows the failed agent in red, the error message, and which agents were skipped. The fallback path (if any) is shown. |

#### Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| WebSocket/SSE connection drops during trace | Display "Connection lost -- reconnecting..." with a spinning indicator. Auto-reconnect within 5 seconds. If reconnection fails 3 times, show "Connection lost. Click to retry." with a manual retry button. |
| Pipeline executes faster than the UI can render updates | Batch rapid state changes and display the final state. The replay feature allows the user to review each step after the fact. |
| Two queries are running simultaneously | Each query gets its own trace panel, visually separated. A tab or dropdown lets the user switch between active traces. |
| Agent names or statuses contain unexpected characters | Sanitize all displayed text. Never render raw HTML from agent output. |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Update Latency | Trace reflects agent state changes within 500ms of occurrence | Timestamp comparison: agent log timestamp vs. UI render timestamp |
| State Accuracy | 100% of agent transitions are reflected in the trace | End-to-end test: run 50 queries, verify trace matches `mother_agent.py` execution log |
| Connection Resilience | Auto-reconnect succeeds within 5 seconds for 95%+ of disconnection events | Chaos test: simulate network interruptions during pipeline execution |
| Replay Fidelity | Replay shows identical sequence and timing ratios as the original execution | Replay output compared to original trace log |

---

## 5.2 Reliability & Safety

The system must be safe to run unattended. It must never incur unexpected costs, never get stuck in infinite loops, never leak data, and never lose work.

---

### 5.2.1 Cost Ceiling & Circuit Breaker -- "Will this cost me money?"

| Attribute | Detail |
|---|---|
| **User Need** | "Will this cost me money?" |
| **Solution** | $0.00 hard ceiling with circuit breaker |
| **Component** | `CircuitBreaker.tsx` |
| **Priority** | P0 -- Critical |

#### User Persona & Scenario

**Persona: Derek, Engineering Manager (Primary)**
Derek is evaluating this system for his team. His first question is cost. If the system accidentally calls a paid API, it could trigger an invoice. The hard $0.00 ceiling guarantees that the system cannot incur costs, and the circuit breaker provides the enforcement mechanism.

**Persona: Sam, Solo Developer (Secondary)**
Sam is running this on a personal machine. Sam has no budget for API calls. The system must guarantee that it will never make a network request to a paid service, even if a configuration error occurs.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| CB-01 | The system is initialized | The configuration is loaded | A cost ceiling of $0.00 is enforced. No configuration option exists to raise this ceiling. The ceiling is hardcoded, not configurable. |
| CB-02 | An agent attempts to make an outbound HTTP request to a known paid API endpoint (OpenAI, Anthropic, Cohere, etc.) | The request is intercepted | The circuit breaker blocks the request before it leaves the machine, logs the attempt with full stack trace, and returns an error to the calling agent |
| CB-03 | The token budget for a single query exceeds the configured maximum (e.g., 4096 tokens) | The budget threshold is reached | The circuit breaker halts the agent pipeline, returns partial results with a notification: "Token budget exceeded. Partial results returned." |
| CB-04 | The user views the dashboard | The CircuitBreaker status widget renders | A persistent status indicator shows: "All local -- $0.00 cost" in green, or "Circuit breaker tripped" in red if any violation was attempted |
| CB-05 | The circuit breaker has tripped in the current session | The user clicks the circuit breaker indicator | A detail panel shows: (a) what triggered the trip, (b) when it happened, (c) what was blocked, (d) what action was taken |
| CB-06 | The system has been running for 24+ hours | The user checks the cost dashboard | A cumulative cost display reads "$0.00" with a log of all blocked attempts (if any) |

#### Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| A dependency library makes an undocumented external call | The circuit breaker monitors all outbound network traffic at the application level. Any unrecognized external request is blocked and logged. |
| Local model file is missing, and the system might fall back to a remote API | The system fails safe: return an error ("Local model not found. Remote fallback is disabled by policy.") rather than attempting any remote call. |
| Token counting is inaccurate due to tokenizer mismatch | Use a conservative estimate (overcount by 10%). Better to halt early than to exceed the budget. |
| Circuit breaker state is corrupted | Default to the most restrictive state (all external calls blocked). Log the corruption for debugging. |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Cost Incurred | $0.00 across all test runs and production usage | Network traffic audit: capture all outbound requests over a 48-hour test period |
| Block Accuracy | 100% of paid API calls are blocked | Penetration test: attempt 20 different paid API endpoints programmatically |
| False Positive Rate | 0% of legitimate local requests are blocked | Run full pipeline 100 times, verify no local requests are incorrectly blocked |
| Trip Notification Latency | User is notified within 1 second of a circuit breaker trip | Automated UI event timing test |

---

### 5.2.2 Loop Detection & Fallback -- "What if it gets stuck?"

| Attribute | Detail |
|---|---|
| **User Need** | "What if it gets stuck?" |
| **Solution** | Loop detection + automatic fallback with partial results |
| **Component** | `FallbackView.tsx` |
| **Priority** | P0 -- Critical |

#### User Persona & Scenario

**Persona: Aisha, Senior ML Engineer (Primary)**
Aisha is running the system on a batch of 50 queries. If one query causes the pipeline to loop (e.g., critic rejects, correction is made, critic rejects again, indefinitely), it blocks the entire batch. Loop detection breaks the cycle and returns whatever partial results exist.

**Persona: Jordan, End User (Secondary)**
Jordan submitted a question and has been waiting 30 seconds with no response. The system should not silently spin forever. Jordan needs either an answer or a clear explanation of why no answer is available.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| LD-01 | The agent pipeline is executing a query | The same correction cycle repeats more than 3 times (configurable) | The loop detector halts the pipeline and triggers the fallback path |
| LD-02 | The loop detector has triggered | The FallbackView renders | The user sees: (a) the best partial result from the last completed round, (b) a notification: "The system detected a correction loop and returned the best available result", (c) the confidence score of the partial result |
| LD-03 | The pipeline has been running for longer than the maximum allowed duration (default: 30 seconds per query) | The timeout is reached | The system halts, returns partial results (if any), and displays: "Query timed out after [N] seconds. Partial results shown." |
| LD-04 | The loop was detected and partial results are available | The user views the partial results | The partial results are clearly labeled as partial (distinct visual treatment: dashed border, "Partial" badge) |
| LD-05 | The loop was detected and NO partial results are available | The FallbackView renders | The view displays: "The system could not produce a reliable answer for this query. No partial results are available." with a "Retry" button |
| LD-06 | The user clicks "Retry" on a failed query | The retry is submitted | The query is re-submitted with a fresh pipeline execution. The loop counter resets. The previous failed attempt is logged. |
| LD-07 | A batch of 50 queries is running and query #12 enters a correction loop | The loop detector triggers for query #12 | Query #12 is halted and returned with partial results. Queries #13–50 continue processing unaffected. The loop is isolated to a single query — no cross-query contamination. |

#### Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| Loop detection triggers on the very first correction round (round 1 of 1) | Still return partial results. The system should not require multiple rounds to produce output. |
| Two loops are detected in rapid succession (batch mode) | Each query is handled independently. One loop does not affect the processing of other queries. |
| The loop is caused by contradictory critic/correction logic (critic says fix X, correction fixes X, critic says revert X) | Log the contradiction pattern. Return the highest-confidence version from any round. |
| System runs out of memory during a loop | Graceful shutdown: persist the current state to disk, return an error, and do not corrupt any stored data. |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Detection Accuracy | 100% of infinite loops are detected within the configured round limit | Synthetic loop test: submit 20 queries known to cause loops |
| Fallback Latency | Partial results are returned within 2 seconds of loop detection | Timing test from loop-detection event to UI render |
| Partial Result Quality | Partial results have a confidence score within 20 points of what a full pipeline would produce | Compare partial results against manually-completed pipeline runs |
| Retry Success Rate | 60%+ of retries after loop detection produce a complete result | Statistical test over 100 retry attempts |

---

### 5.2.3 Local Inference -- "Is my data safe?"

| Attribute | Detail |
|---|---|
| **User Need** | "Is my data safe?" |
| **Solution** | 100% local inference -- nothing leaves the machine |
| **Component** | Architecture decision (enforced across all components) |
| **Priority** | P0 -- Critical |

#### User Persona & Scenario

**Persona: Marcus, Compliance Officer (Primary)**
Marcus works in a regulated industry. Any data that leaves the corporate network is a compliance violation. He needs an architecture guarantee -- not just a policy -- that all inference happens locally.

**Persona: Sam, Solo Developer (Secondary)**
Sam is processing proprietary code through the system. Sam needs assurance that the code never leaves the local machine, even temporarily.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| LI-01 | The system is installed and configured | The user runs the system for the first time | All model files are loaded from local disk. No download occurs at inference time. |
| LI-02 | The system is processing a query | Network monitoring is active | Zero outbound network requests are made during the entire pipeline execution (inference, critic evaluation, correction) |
| LI-03 | The user views the dashboard | The architecture status widget renders | A persistent indicator reads: "100% Local -- No data leaves this machine" |
| LI-04 | The system encounters a query it cannot handle with local models | The inference step fails | The system returns an error: "This query exceeds local model capabilities. No external fallback is available." It does NOT attempt a remote call. |
| LI-05 | A new version of the system is installed | The user reviews the changelog | Any new dependency is audited for outbound network calls. The changelog explicitly states: "No new external dependencies." |

#### Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| A Python dependency has a telemetry/analytics ping built in | The dependency must be patched or replaced. If patching is not possible, the dependency is run in a network-isolated context. |
| The local model file is corrupted | Return an error. Do not attempt to re-download the model. Prompt the user to re-install the model manually. |
| DNS resolution is attempted (even without data transfer) | Block DNS lookups during inference. The system should not resolve any external hostnames during pipeline execution. |
| User intentionally wants to use a remote API for testing | This is explicitly not supported. The architecture enforces local-only inference with no override mechanism. |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Outbound Requests During Inference | Exactly 0 | Network packet capture (tcpdump/Wireshark) during 100 query pipeline runs |
| Local Model Coverage | 100% of inference operations use local models | Code audit + runtime verification |
| Data Residency | No query data, response data, or intermediate data is written to any location outside the local filesystem | Filesystem audit during and after pipeline execution |
| Compliance Attestation | System passes a mock compliance audit for data residency | Manual audit by a second engineer following a compliance checklist |

---

### 5.2.4 State Persistence -- "What if the system crashes?"

| Attribute | Detail |
|---|---|
| **User Need** | "What if the system crashes?" |
| **Solution** | State persistence -- resume from last checkpoint |
| **Component** | `mother_agent.py` |
| **Priority** | P1 -- High |

#### User Persona & Scenario

**Persona: Kai, DevOps/MLOps Engineer (Primary)**
Kai's machine crashed during a long batch run. When the system restarts, Kai needs it to pick up where it left off -- not restart the entire batch from scratch. Checkpoint-based persistence ensures that completed work is not lost.

**Persona: Aisha, Senior ML Engineer (Secondary)**
Aisha is running an experimental pipeline configuration. If the system crashes during the critic evaluation phase, she needs the inference results to be preserved so she can re-run only the critic step.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| SP-01 | The agent pipeline is executing a multi-step query | Each agent step completes | The state (input, output, metadata) is checkpointed to local disk before proceeding to the next step |
| SP-02 | The system crashes or is forcefully terminated mid-pipeline | The system restarts | The user is prompted: "Previous session found. Resume from [agent step]? [Resume / Start Fresh]" |
| SP-03 | The user chooses "Resume" | The pipeline resumes | Execution begins from the last completed checkpoint. Already-completed steps are not re-executed. |
| SP-04 | The user chooses "Start Fresh" | The pipeline restarts | The previous checkpoint data is archived (not deleted) and a new execution begins from scratch |
| SP-05 | The checkpoint file is corrupted | The system attempts to resume | A validation check detects corruption, displays "Checkpoint corrupted -- starting fresh," and archives the corrupted file for debugging |
| SP-06 | A batch of 50 queries is running and the system crashes after query 37 | The system restarts and resumes | Queries 1-37 are marked complete. Execution resumes from query 38. |

#### Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| System crashes during the checkpoint write itself | Use atomic writes (write to temp file, then rename). A partially written checkpoint is detected and treated as corrupted. |
| Disk is full and checkpoint cannot be written | Log a warning: "Checkpoint failed -- disk full. Pipeline continues without persistence." The pipeline does not halt, but the user is warned. |
| Checkpoint is from an older version of the system | Version-stamp all checkpoints. If version mismatch is detected, prompt: "Checkpoint from version X. Current version is Y. Resume may be unreliable. [Resume Anyway / Start Fresh]" |
| Multiple crash-resume cycles on the same query | Each resume attempt is logged. After 3 failed resume attempts on the same query, skip it and proceed to the next query with a log entry. |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Checkpoint Write Reliability | 99.9% of checkpoints are written successfully (excluding disk-full scenarios) | Kill-test: terminate the process 100 times at random points, verify checkpoint integrity |
| Resume Accuracy | 100% of resumed pipelines produce the same output as an uninterrupted run | Compare resumed-run output to uninterrupted-run output for 50 queries |
| Resume Latency | Pipeline resumes within 2 seconds of restart | Timing test from process start to first resumed agent step |
| Data Integrity | Zero data loss or corruption across crash-resume cycles | Integrity hash verification on all checkpointed data |

---

## 5.3 Usability & Experience

The system must feel fast, look professional, and work on every screen size. If users struggle with the interface, the underlying technology is irrelevant.

---

### 5.3.1 Loading Feedback -- "I hate waiting with no feedback"

| Attribute | Detail |
|---|---|
| **User Need** | "I hate waiting with no feedback" |
| **Solution** | Skeleton cards + progress indicators + SSE streaming |
| **Component** | `SkeletonLoader.tsx` |
| **Priority** | P0 -- Critical |

#### User Persona & Scenario

**Persona: Jordan, End User (Primary)**
Jordan submits a query and stares at a blank screen. After 3 seconds of no feedback, Jordan assumes the system is broken and refreshes the page, losing the in-progress request. Skeleton loaders and progress indicators prevent this by showing immediate visual feedback.

**Persona: Fatima, ML Engineer (Secondary)**
Fatima is running the dashboard during a demo. A blank loading state looks unprofessional. Skeleton cards give the impression of a polished, production-ready system.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| SL-01 | The user submits a query | The request is sent to the backend | Within 100ms, a skeleton card appears in the results area with animated shimmer placeholders for: title, confidence gauge, response body, and source attribution |
| SL-02 | The agent pipeline is processing | SSE events are being received | The skeleton card progressively fills in with real content as each agent completes. The confidence gauge area shows "Calculating..." until the critic agent finishes. |
| SL-03 | The SSE stream delivers the first chunk of response text | The chunk is received | The skeleton for the response body is replaced with actual text. Remaining skeletons (confidence, sources) persist until their data arrives. |
| SL-04 | The pipeline completes | All SSE events have been received | All skeleton placeholders are replaced with real content. No shimmer animations remain. |
| SL-05 | The request fails before any content is returned | An error occurs | The skeleton card transitions to an error state: red border, error icon, and message: "Something went wrong. [Retry]" |
| SL-06 | Multiple queries are submitted simultaneously | All requests are in flight | Each query gets its own skeleton card. Cards appear in submission order. |
| SL-07 | The skeleton card transitions to real content | The crossfade animation occurs | Cumulative Layout Shift (CLS) during the skeleton-to-content transition is < 0.05 as measured by the Performance Observer API. Skeleton and content bounding boxes match within 2px tolerance. |

#### Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| SSE connection drops mid-stream | Skeleton areas that have not been filled revert to an error state for that section. Already-rendered content remains visible. A "Reconnecting..." indicator appears. |
| Pipeline completes so fast (<200ms) that the skeleton is barely visible | Skip the skeleton animation entirely. Render the final content directly. No flickering. |
| User navigates away and back during loading | If the pipeline is still running, show the skeleton at the current progress state. If it completed while the user was away, show the final result. |
| 20+ queries are loading simultaneously | Virtualize the list. Only render skeleton cards for queries visible in the viewport. |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Time to First Visual Feedback | < 100ms from query submission | Performance profiling with React DevTools |
| Perceived Performance Score | Users rate loading experience 4+/5 | Usability survey |
| Skeleton-to-Content Transition Smoothness | No layout shift (CLS < 0.1) during transition | Lighthouse CLS measurement |
| Error State Visibility | 100% of users notice the error state within 2 seconds | Eye-tracking or click-tracking in usability test |

---

### 5.3.2 4K Responsive Design -- "It looks broken on my screen"

| Attribute | Detail |
|---|---|
| **User Need** | "It looks broken on my screen" |
| **Solution** | 4K responsive design tested at 7 breakpoints |
| **Component** | `App_4K_Responsive.css` |
| **Priority** | P1 -- High |

#### User Persona & Scenario

**Persona: Kai, DevOps/MLOps Engineer (Primary)**
Kai uses a 4K monitor (3840x2160). On many dashboards, content is either tiny and unusable or does not scale to fill the available space. The dashboard must look intentional and information-dense on 4K, not just "zoomed in."

**Persona: Derek, Engineering Manager (Secondary)**
Derek presents the dashboard on a conference room projector (1024x768). The layout must not break at low resolutions.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| RD-01 | The user opens the dashboard | The viewport is any of the 7 supported breakpoints | The layout adapts correctly with no horizontal scrollbar, no overlapping elements, and no text truncation that hides critical information |
| RD-02 | The viewport is 3840x2160 (4K) | The dashboard renders | Content fills the available space. Grid layouts use the additional width for more columns. Font sizes are comfortable (minimum 14px equivalent at 4K). Charts and gauges scale proportionally. |
| RD-03 | The viewport is 1920x1080 (Full HD) | The dashboard renders | This is the primary design target. All components render at their designed size with optimal spacing. |
| RD-04 | The viewport is 1024x768 (XGA) | The dashboard renders | Layout collapses to single-column where needed. Non-critical elements are hidden behind "More" menus. All critical information remains visible. |
| RD-05 | The user resizes the browser window between breakpoints | The layout transitions | Transitions are smooth (CSS transitions, no jarring jumps). Content reflows correctly. No elements are orphaned or overlapping. |
| RD-06 | The user uses browser zoom (50% to 200%) | The zoom level changes | The layout remains functional at all zoom levels. No elements overflow their containers. Minimum touch/click target size of 44x44px is maintained. |

**Supported Breakpoints:**

| # | Name | Width | Primary Use Case |
|---|---|---|---|
| 1 | Mobile Small | 320px | Small smartphones |
| 2 | Mobile Large | 480px | Large smartphones |
| 3 | Tablet Portrait | 768px | Tablets in portrait |
| 4 | Tablet Landscape / Small Desktop | 1024px | Tablets in landscape, small laptops |
| 5 | Desktop | 1280px | Standard laptops |
| 6 | Full HD | 1920px | Full HD monitors (primary target) |
| 7 | 4K / Ultra-wide | 3840px | 4K monitors and ultra-wide displays |

#### Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| Ultra-wide monitor (5120x1440) | Content is max-width constrained (e.g., 3840px) and centered. The layout does not stretch to fill 5120px, which would create unreadable line lengths. |
| Very tall, narrow viewport (e.g., phone in split-screen: 320x900) | Vertical layout with stacked cards. Horizontal scrolling is never required. |
| User has OS-level DPI scaling at 150% | The layout accounts for effective resolution, not physical resolution. CSS media queries use logical pixels. |
| Custom browser font size (e.g., user set default to 24px) | Layouts use relative units (rem/em). Increasing base font size does not break layouts. |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Breakpoint Coverage | All 7 breakpoints pass visual regression testing | Automated screenshot comparison (Playwright/Puppeteer) at each breakpoint |
| Layout Integrity | Zero overflow, zero overlap at any breakpoint | Automated DOM inspection for overflow and z-index conflicts |
| Content Accessibility at 4K | All text readable without zooming on a 27" 4K monitor | Manual visual inspection from 60cm viewing distance |
| Transition Smoothness | No layout shift > 0.1 CLS during resize | Continuous CLS measurement during a smooth resize from 320px to 3840px |

---

### 5.3.3 Mobile-First Design -- "I can't use this on my phone"

| Attribute | Detail |
|---|---|
| **User Need** | "I can't use this on my phone" |
| **Solution** | Mobile-first responsive design with touch targets |
| **Component** | CSS + responsive components |
| **Priority** | P1 -- High |

#### User Persona & Scenario

**Persona: Jordan, End User (Primary)**
Jordan is checking pipeline results on a phone while commuting. The dashboard must be fully functional on a 375px-wide screen with touch input. Buttons must be large enough to tap, text must be readable without zooming, and critical information must not be hidden.

**Persona: Derek, Engineering Manager (Secondary)**
Derek checks the system status on his phone during meetings. He needs to see the top-level health indicators (cost, pipeline status, confidence scores) without navigating through multiple screens.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| MF-01 | The user opens the dashboard on a mobile device (viewport < 480px) | The page loads | The layout is single-column. Navigation collapses into a hamburger menu. All cards stack vertically. |
| MF-02 | The user taps a button or interactive element on mobile | The tap is registered | All interactive elements have a minimum touch target size of 44x44px (WCAG 2.1 guideline 2.5.5) |
| MF-03 | The user views a response card on mobile | The card renders | The confidence gauge, response text, and correction badge are all visible without horizontal scrolling. Source citations collapse into an expandable section. |
| MF-04 | The user swipes or scrolls on mobile | The gesture is performed | Scrolling is smooth (60fps). No elements interfere with native scroll behavior. No horizontal scroll is triggered by content overflow. |
| MF-05 | The user opens the live trace on mobile | The trace panel renders | The trace is displayed as a vertical timeline (not a horizontal flowchart). Each step is tappable for details. |
| MF-06 | The user is on a slow mobile connection (3G) | The page loads | Critical content (pipeline status, last confidence score) loads within 3 seconds. Non-critical assets (charts, animations) load progressively. |

#### Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| Device is in landscape orientation (e.g., 667x375) | Layout adapts to landscape. Two-column layout may be used if space permits. No content is clipped. |
| User has "Reduce Motion" accessibility setting enabled | All animations (shimmer, transitions, pulsing indicators) are disabled. Static alternatives are shown. |
| Virtual keyboard is open (effective viewport height is halved) | Input fields and their labels remain visible above the keyboard. The page scrolls to keep the active input in view. |
| Small phone (320px width, e.g., iPhone SE 1st gen) | All content remains accessible. Font size does not drop below 14px. Padding is reduced but touch targets maintain 44x44px minimum. |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Mobile Usability Score | 95+ on Google Lighthouse mobile audit | Lighthouse CI on each build |
| Touch Target Compliance | 100% of interactive elements meet 44x44px minimum | Automated DOM measurement script |
| Mobile Load Time (3G) | < 3 seconds for critical content | Lighthouse throttled 3G simulation |
| Mobile Task Completion Rate | 90%+ of users complete a "check pipeline status" task on mobile without errors | Usability test with 5+ participants on real devices |

---

### 5.3.4 Dashboard Clarity -- "I need to understand quickly"

| Attribute | Detail |
|---|---|
| **User Need** | "I need to understand quickly" |
| **Solution** | Clean dashboard with visual hierarchy and data density |
| **Component** | `Dashboard.tsx` |
| **Priority** | P0 -- Critical |

#### User Persona & Scenario

**Persona: Derek, Engineering Manager (Primary)**
Derek opens the dashboard for 30 seconds between meetings. He needs to see at a glance: Is the system healthy? What is the average confidence? Were there any issues? He does not have time to click through multiple screens.

**Persona: Fatima, ML Engineer (Secondary)**
Fatima uses the dashboard for extended analysis sessions. She needs the ability to drill down from the summary view into detailed per-query results without losing context.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| DC-01 | The user opens the dashboard | The main view renders | The top section (above the fold on 1920x1080) displays: (a) system status (healthy/degraded/down), (b) cost indicator ($0.00), (c) average confidence score, (d) total queries processed, (e) correction rate |
| DC-02 | The user scans the dashboard for anomalies | The dashboard is loaded | Any metric that is outside its normal range is visually highlighted (color change, icon, badge) without requiring the user to interpret raw numbers |
| DC-03 | The user wants to see individual query results | The user scrolls below the summary | A list of recent queries is displayed as cards with: query text (truncated), confidence score, correction count, and timestamp |
| DC-04 | The user clicks on a query card | The detail view opens | A full view shows: complete response, confidence gauge, source attributions, correction log, and live trace (if available) |
| DC-05 | The dashboard has no queries yet (empty state) | The user opens the dashboard for the first time | An instructive empty state is shown: "No queries yet. Submit your first query to see results here." with a visual guide on how to use the system |
| DC-06 | The user wants to filter or search past queries | The user interacts with the filter/search controls | Results can be filtered by: confidence range, correction status, date range, and keyword search in query text |

#### Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| 1000+ queries in history | Pagination or virtual scrolling. The dashboard does not attempt to render all 1000 cards at once. Default view shows the 20 most recent. |
| All queries have 100% confidence (nothing looks wrong) | The dashboard still displays normally. No anomaly highlights. Summary statistics are accurate. |
| All queries have <50% confidence (everything looks wrong) | The dashboard highlights the trend: "Average confidence is below 50%. Review pipeline configuration." |
| Dashboard is opened in two browser tabs simultaneously | Both tabs reflect the same data. No conflicts. Real-time updates (if any) reach both tabs. |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Time to Insight | Users answer "Is the system healthy?" within 5 seconds of opening the dashboard | Usability test with eye-tracking |
| Information Architecture Score | 80%+ of users find the correction log for a specific query within 3 clicks | Task-based usability test |
| Data Density | Summary section displays 5+ key metrics above the fold on 1920x1080 | Manual visual inspection |
| Render Performance | Dashboard renders completely in < 500ms with 100 queries loaded | Lighthouse performance profiling |

---

## 5.4 Performance

Performance is not optional. Slow responses erode trust, slow page loads drive users away, and batch processing delays block engineering workflows.

---

### 5.4.1 Inference Speed -- "It's too slow"

| Attribute | Detail |
|---|---|
| **User Need** | "It's too slow" |
| **Solution** | NF4 quantized local models + response caching |
| **Component** | `critic_agent.py` |
| **Priority** | P0 -- Critical |

#### User Persona & Scenario

**Persona: Aisha, Senior ML Engineer (Primary)**
Aisha is iterating on critic prompts and running the pipeline 50 times a day. Every second of inference latency multiplies across her workflow. Quantized models and caching turn a 10-second evaluation into a 3-second one, saving hours per week.

**Persona: Jordan, End User (Secondary)**
Jordan expects a response within a few seconds. If the system takes 10+ seconds, Jordan will abandon it. The performance threshold is not a technical curiosity -- it is a retention metric.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| IS-01 | A query is submitted for the first time (cold cache) | The full pipeline executes | The critic agent evaluation completes in < 3 seconds on consumer hardware (8GB+ VRAM GPU or Apple Silicon M1+) |
| IS-02 | An identical query is submitted again (warm cache) | The cache is checked | The cached result is returned in < 200ms. The pipeline is not re-executed. |
| IS-03 | A similar but not identical query is submitted | The cache is checked | A cache miss occurs, and the pipeline executes normally. Similarity-based cache hits are NOT implemented (too risky for correctness). |
| IS-04 | The local model is NF4 quantized | Inference runs | The output quality (measured by a held-out evaluation set) is within 5% of the full-precision model |
| IS-05 | The cache grows beyond its configured maximum size (e.g., 1000 entries) | A new cache entry is added | The least-recently-used entry is evicted. Cache eviction does not cause latency spikes (< 10ms overhead). |
| IS-06 | The system is running on a CPU-only machine (no GPU) | A query is submitted | The pipeline still completes, but within 10 seconds. A notification informs the user: "Running on CPU -- performance is reduced. GPU recommended." |

#### Performance Thresholds

| Metric | Target (GPU) | Target (CPU) | Maximum Acceptable |
|---|---|---|---|
| Critic Evaluation (cold) | < 3s | < 10s | 15s |
| Critic Evaluation (warm cache) | < 200ms | < 200ms | 500ms |
| Full Pipeline (cold) | < 8s | < 25s | 30s |
| Full Pipeline (warm cache) | < 1s | < 1s | 2s |
| Model Load Time (first query) | < 5s | < 10s | 15s |

#### Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| GPU runs out of VRAM during inference | Gracefully fall back to CPU inference with a warning. Do not crash. |
| Cache file is corrupted | Rebuild the cache from scratch. Log the corruption. Do not serve corrupted cached results. |
| Extremely long query (5000+ tokens) | Process in chunks if necessary. Warn the user if the query exceeds the model's context window. Truncate with notification rather than silently dropping tokens. |
| Two identical queries are submitted at the exact same time | Only one pipeline execution occurs. The second query waits for the first to complete and then reads from cache. (Cache stampede prevention.) |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| P50 Latency (cold) | < 3s (GPU) / < 10s (CPU) | Benchmark: 100 unique queries on reference hardware |
| P95 Latency (cold) | < 5s (GPU) / < 15s (CPU) | Same benchmark, 95th percentile |
| Cache Hit Rate | > 30% in typical usage patterns | Cache statistics logging over a 1-week simulated workload |
| Quantization Quality Loss | < 5% on held-out evaluation set | Automated eval: compare NF4 vs FP16 on 200 test queries |

---

### 5.4.2 Page Load Performance -- "The page takes forever to load"

| Attribute | Detail |
|---|---|
| **User Need** | "The page takes forever to load" |
| **Solution** | Code splitting + lazy loading + optimistic UI |
| **Component** | Next.js App Router configuration |
| **Priority** | P1 -- High |

#### User Persona & Scenario

**Persona: Jordan, End User (Primary)**
Jordan clicks a link to the dashboard and waits. If the page is not interactive within 2 seconds, Jordan assumes it is broken. Code splitting ensures that only the code needed for the initial view is loaded, with the rest fetched on demand.

**Persona: Sam, Solo Developer (Secondary)**
Sam is running the dashboard on a laptop with limited bandwidth (coffee shop WiFi). Large JavaScript bundles make the page unusable. Lazy loading keeps the initial payload small.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| PL-01 | The user navigates to the dashboard URL | The initial page load occurs | The page is interactive (Time to Interactive) within 2 seconds on a broadband connection |
| PL-02 | The initial bundle is loaded | The bundle size is measured | The main JavaScript bundle is < 200KB gzipped. Additional chunks are loaded on demand. |
| PL-03 | The user navigates to a detail view (e.g., query detail, correction log) | The route transition occurs | The detail view component is lazy-loaded. The route transition shows a loading indicator within 100ms. The detail view renders within 500ms. |
| PL-04 | The user opens the dashboard for the first time | The page loads | An optimistic UI renders immediately with cached/default data while fresh data is fetched in the background. The user is never shown a blank screen. |
| PL-05 | The user has visited before and returns | The page loads | Static assets are served from browser cache (Cache-Control headers). Only dynamic data is fetched fresh. |
| PL-06 | The frontend application is built for production | The build process runs | Turbopack is used as the build tool for Next.js, providing faster builds than Webpack. Build output is verified for tree-shaking completeness and bundle size compliance (< 200KB gzipped initial chunk). |

#### Performance Thresholds

| Metric | Target | Maximum Acceptable |
|---|---|---|
| Time to Interactive (TTI) | < 2s | 3s |
| First Contentful Paint (FCP) | < 1s | 1.5s |
| Largest Contentful Paint (LCP) | < 1.5s | 2.5s |
| Cumulative Layout Shift (CLS) | < 0.05 | 0.1 |
| Total Bundle Size (gzipped) | < 200KB initial | 300KB initial |

#### Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| User has JavaScript disabled | A noscript fallback message is displayed: "This application requires JavaScript. Please enable JavaScript to continue." |
| Slow 3G connection | Critical CSS is inlined. Above-the-fold content renders within 5 seconds. Non-critical resources are deferred. |
| Browser does not support code splitting (very old browser) | A single bundled fallback is served. Performance will be degraded but functionality is preserved. |
| CDN is unavailable (assets served locally) | Since this is a local-first application, all assets are served from the local machine. No CDN dependency exists. |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Lighthouse Performance Score | 90+ | Lighthouse CI on each build |
| TTI | < 2s on 4G throttled connection | Lighthouse performance audit |
| Bundle Size | < 200KB gzipped initial chunk | Webpack bundle analyzer |
| Cache Effectiveness | 80%+ of static assets served from cache on repeat visits | Network tab analysis in DevTools |

---

### 5.4.3 Streaming Results -- "Results appear all at once"

| Attribute | Detail |
|---|---|
| **User Need** | "Results appear all at once" |
| **Solution** | SSE streaming -- results appear as agents complete |
| **Component** | `api/stream.ts` |
| **Priority** | P0 -- Critical |

#### User Persona & Scenario

**Persona: Jordan, End User (Primary)**
Jordan submits a query and waits 8 seconds for a monolithic response. With SSE streaming, Jordan sees the inference result appear after 2 seconds, the confidence score after 4 seconds, and corrections (if any) after 6 seconds. The experience transforms from "waiting" to "watching the system work."

**Persona: Fatima, ML Engineer (Secondary)**
Fatima is debugging the pipeline. Streaming lets her see each agent's output as it completes, rather than waiting for the entire pipeline to finish. This reduces her debug cycle time.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| SR-01 | The user submits a query | The pipeline begins execution | An SSE connection is established between the client and server. The connection sends events as each agent step completes. |
| SR-02 | The inference agent completes | The SSE event is sent | The response text appears in the UI within 500ms of the agent completing. The skeleton placeholder for the response body is replaced. |
| SR-03 | The critic agent completes | The SSE event is sent | The confidence score appears in the UI. The "Calculating..." placeholder is replaced with the actual score and gauge. |
| SR-04 | The correction agent completes (if corrections were needed) | The SSE event is sent | The correction badge appears. The response text is updated with the corrected version. The original text is preserved in the correction log. |
| SR-05 | The pipeline completes | The final SSE event is sent | The SSE connection is closed cleanly. The response card is in its final state. No more updates will occur. |
| SR-06 | The user submits a new query while a previous query is still streaming | The second query begins | A second SSE connection is established (or the existing one is multiplexed). Both queries stream independently. |
| SR-07 | The SSE connection drops during active streaming | The client detects disconnection | The client automatically reconnects within 3 seconds using `Last-Event-ID` header. The server replays all events after the last received ID. No duplicate events are rendered (client deduplicates by sequence number). |
| SR-08 | The server sends a partial SSE chunk (network interruption mid-event) | The client receives an incomplete event | The client buffers partial chunks until a complete event boundary (`\n\n`) is received. Incomplete events are not processed. A 10-second buffer timeout triggers a reconnection. |
| SR-09 | SSE events arrive out of order due to network reordering | The client receives events with non-sequential `seq` values | The client maintains a reorder buffer (max 10 events). Events are held until all preceding sequence numbers have been received or a 5-second timeout expires, at which point buffered events are flushed in order. |

#### Performance Thresholds

| Metric | Target | Maximum Acceptable |
|---|---|---|
| SSE Event Delivery Latency | < 100ms from server emit to client receive | 500ms |
| Time to First Streamed Content | < 2s after query submission | 5s |
| Connection Establishment | < 200ms | 500ms |
| Reconnection After Disconnect | < 3s automatic | 5s |

#### Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| SSE connection is dropped by the browser (e.g., tab backgrounded for 30s) | Auto-reconnect when tab is foregrounded. Fetch any missed events via a catch-up endpoint. |
| Server sends events out of order (network reordering) | Each SSE event includes a sequence number. The client buffers and reorders if necessary. |
| Server crashes mid-stream | Client detects the broken connection within 5 seconds. Displays: "Connection lost during processing. Partial results shown. [Retry]" |
| User's browser does not support SSE (very rare) | Fall back to polling every 2 seconds. Functionality is preserved, but the experience is degraded. |
| The pipeline produces no output (empty response) | The SSE stream sends a completion event with an explicit "empty result" payload. The UI shows: "The system processed your query but produced no output." |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Event Delivery Reliability | 99.9%+ of SSE events are delivered to the client | End-to-end test: send 1000 events, verify all received |
| Perceived Responsiveness | Users report the system "feels fast" at 4+/5 | Usability survey comparing streaming vs. non-streaming |
| Reconnection Success Rate | 95%+ of disconnections result in successful automatic reconnection | Chaos test: drop connections 50 times during pipeline runs |
| Stream Ordering | 100% of events are displayed in correct order | Sequence number validation in automated test |

---

## 5.5 User Experience Enhancements

These features address user likability gaps identified in the QA audit. Each feature targets specific personas whose satisfaction scores would increase with its inclusion.

---

### 5.5.1 Multi-Turn Conversation Threading

| Attribute | Detail |
|---|---|
| **User Need** | "I want to ask follow-up questions without repeating context" |
| **Solution** | Multi-turn conversation threading with session management |
| **Component** | `ConversationThread.tsx` |
| **Priority** | P1 -- High |

#### User Persona & Scenario

**Persona: Jordan, End User (Primary)**
Jordan asks a question about a research paper. The system responds. Jordan wants to ask a follow-up without re-uploading the context. Conversation threading maintains the session context across turns.

**Persona: Fatima, ML Engineer (Secondary)**
Fatima is iterating on a prompt. She wants to refine her query across multiple turns, with each turn building on the previous response and critique.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| MT-01 | The user has received a response to a query | The user types a follow-up question | The follow-up is submitted with the full conversation history (previous query + response pairs) as context. The system processes it as a continuation, not a new standalone query. |
| MT-02 | A conversation has 3+ turns | The user views the conversation | All turns are displayed in chronological order with clear visual separation between user messages and system responses. Each response retains its confidence score and source citations. |
| MT-03 | The user wants to start a new conversation | The user clicks "New Conversation" | A new session is initialized with a fresh `session_id`. The previous conversation is saved to history. |
| MT-04 | The conversation context exceeds the model's token window | The user submits a turn | The system automatically summarizes earlier turns to fit within the token budget. A notification reads: "Earlier turns have been summarized to fit the context window." |
| MT-05 | The user navigates away and returns | The user reopens the dashboard | The most recent conversation is restored from localStorage. Older conversations are available in the Session History sidebar. |
| MT-06 | The system detects a topic change mid-conversation | The user asks an unrelated question | The system suggests: "This appears to be a new topic. Start a new conversation? [Yes / Continue in current thread]" |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Context Retention Accuracy | Follow-up responses reference prior turns correctly 90%+ of the time | Manual evaluation on 30 multi-turn test conversations |
| Session Restore Reliability | 100% of saved sessions restore correctly | Automated test: save and restore 50 sessions |

#### Edge Cases

| Edge Case | Expected Behavior |
|---|---|
| Conversation has 50+ turns | Only the last 10 turns are sent as context. Earlier turns are summarized. |
| User submits identical follow-up twice | Second submission is deduplicated; cached response is returned. |

---

### 5.5.2 Webhook / Slack Alert Integration

| Attribute | Detail |
|---|---|
| **User Need** | "I want to be notified when something important happens" |
| **Solution** | Configurable webhook endpoints with Slack-compatible payloads |
| **Component** | `WebhookManager.ts` |
| **Priority** | P2 -- Medium |

#### User Persona & Scenario

**Persona: Derek, Engineering Manager (Primary)**
Derek wants to receive a Slack notification when the circuit breaker trips or when confidence drops below 50% on any query.

**Persona: Kai, DevOps/MLOps Engineer (Secondary)**
Kai configures webhook endpoints to pipe guardrail events into their monitoring stack (PagerDuty, Datadog).

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| WH-01 | The user has configured a webhook URL in the settings panel | A configured trigger event occurs (e.g., circuit breaker trip, confidence < 0.5) | An HTTP POST is sent to the webhook URL with a JSON payload: `{ event_type, trace_id, timestamp, details, dashboard_url }` |
| WH-02 | The webhook URL is a Slack incoming webhook | The event fires | The payload includes Slack-compatible formatting: `{ text, blocks: [{ type: "section", text: { type: "mrkdwn", text } }] }` |
| WH-03 | The webhook endpoint is unreachable | The POST fails | The system retries 3 times with exponential backoff (1s, 2s, 4s). After 3 failures, the webhook is marked as "failing" in the settings panel. Pipeline processing is not affected. |
| WH-04 | The user wants to test their webhook configuration | The user clicks "Send Test" | A test payload is sent to the configured URL. The UI shows "Delivered" or "Failed" with the HTTP status code. |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Delivery Latency | Webhook fires within 2s of trigger event | Timestamp comparison |
| Delivery Reliability | 99%+ of webhooks delivered (excluding endpoint failures) | Automated test with mock endpoint |

---

### 5.5.3 Model Selector Dropdown

| Attribute | Detail |
|---|---|
| **User Need** | "I want to choose which model processes my query" |
| **Solution** | Model selector that auto-discovers available Ollama models |
| **Component** | `ModelSelector.tsx` |
| **Priority** | P2 -- Medium |

#### User Persona & Scenario

**Persona: Fatima, ML Engineer (Primary)**
Fatima wants to compare DeepSeek-R1 vs Llama 3.1 for a specific query type. The model selector lets her switch without editing configuration files.

**Persona: Aisha, Senior ML Engineer (Secondary)**
Aisha is testing a newly downloaded model. She selects it from the dropdown and runs her test suite against it.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| MS-01 | The dashboard loads | The model selector renders | A dropdown lists all models available in the local Ollama instance (queried via `GET http://localhost:11434/api/tags`). The currently active model is highlighted. |
| MS-02 | The user selects a different model | The selection is confirmed | The next query uses the selected model. A toast notification confirms: "Model switched to [model_name]." The model switch does not affect in-progress queries. |
| MS-03 | The selected model is not loaded in memory | The user submits a query | A loading indicator shows: "Loading [model_name]... This may take 5–15 seconds." The query is held until the model is ready. |
| MS-04 | No models are available in Ollama | The selector renders | The dropdown shows: "No models available. Run `ollama pull <model>` to get started." with a link to the Ollama model library. |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Model Discovery Latency | < 500ms to populate dropdown | Timing test of Ollama API call |
| Switch Reliability | 100% of model switches succeed (given model exists) | Automated test across 5 models |

---

### 5.5.4 Prompt Version Management

| Attribute | Detail |
|---|---|
| **User Need** | "I want to track and compare prompt changes" |
| **Solution** | Version-stamped prompts with diff view and A/B comparison |
| **Component** | `PromptVersionManager.tsx` |
| **Priority** | P2 -- Medium |

#### User Persona & Scenario

**Persona: Fatima, ML Engineer (Primary)**
Fatima iterates on system prompts daily. She needs to see what changed between v3 and v7 of her critic prompt, and compare their performance metrics side by side.

**Persona: Aisha, Senior ML Engineer (Secondary)**
Aisha discovers that last week's prompt produced better results. She wants to roll back to that version without manually copy-pasting.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| PV-01 | The user modifies a system prompt (inference, critic, or correction) | The prompt is saved | The system creates a new version with: version number (auto-incremented), timestamp, author (if configured), and a hash of the prompt content. Previous versions are retained. |
| PV-02 | The user wants to see what changed | The user selects two versions in the version list | A side-by-side diff view highlights additions (green), deletions (red), and unchanged text (grey). Line numbers are displayed. |
| PV-03 | The user wants to compare performance across versions | The user selects two versions for comparison | A comparison table shows: average confidence score, average latency, correction rate, and sample size for each version. Differences are highlighted. |
| PV-04 | The user wants to roll back to a previous version | The user clicks "Restore" on a historical version | The selected version becomes the active prompt. The current prompt is preserved as a new version (not overwritten). A toast confirms: "Restored prompt v[N]." |
| PV-05 | A prompt version has never been used in a query | The version list is displayed | The version is labeled "Untested" with no performance metrics. |
| PV-06 | The prompt storage exceeds 50 versions | A new version is saved | The oldest version beyond 50 is archived (not deleted). Archived versions are accessible via "Show archived." |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Version Save Latency | < 100ms | Timing test |
| Diff Render Time | < 200ms for prompts up to 5000 characters | Performance profiling |

---

### 5.5.5 Annotation / Comment System

| Attribute | Detail |
|---|---|
| **User Need** | "I want to annotate and comment on AI outputs" |
| **Solution** | Inline claim annotations with export and audit trail |
| **Component** | `AnnotationSystem.tsx` |
| **Priority** | P2 -- Medium |

#### User Persona & Scenario

**Persona: Priya, Data Scientist (Primary)**
Priya is reviewing a response and finds a claim that needs further investigation. She highlights it and adds an annotation: "Verify this statistic against the 2025 dataset." The annotation persists across sessions and is exportable.

**Persona: Marcus, Compliance Officer (Secondary)**
Marcus uses annotations to flag claims for compliance review. He needs an export of all annotations for the audit trail.

#### Acceptance Criteria

| ID | Given | When | Then |
|---|---|---|---|
| AN-01 | The user is viewing a response | The user selects text in the response body | A tooltip appears with options: "Add Annotation", "Flag for Review", "Mark as Verified." |
| AN-02 | The user adds an annotation | The annotation is saved | The annotated text is highlighted with a colored underline (yellow for notes, red for flags, green for verified). A sidebar shows all annotations for the current response. |
| AN-03 | The user wants to export annotations | The user clicks "Export Annotations" | Annotations are exported as JSON with: `{ trace_id, claim_text, annotation_text, annotation_type, author, timestamp, response_context }`. |
| AN-04 | The user returns to a previously annotated response | The response re-renders | All annotations are restored from localStorage. Highlighted text and sidebar entries appear exactly as they were saved. |

#### Measurement Criteria

| Metric | Target | Method |
|---|---|---|
| Annotation Persistence | 100% of annotations survive page reload | Automated save/reload test |
| Export Completeness | Exported JSON contains all displayed annotations | Schema validation on 20 exports |

---

## 5.6 Feature-to-Need Traceability Matrix

Every feature must map to a user need. Every user need must have at least one feature. No orphan features. No unmet needs.

### Complete Traceability Matrix

| # | User Need | Feature/Solution | Component(s) | Section | Status |
|---|---|---|---|---|---|
| N-01 | "Can I trust this answer?" | Confidence Score (0-100%) | `ConfidenceGauge.tsx` | 5.1.1 | Required |
| N-02 | "Where did this come from?" | Source Attribution with citations | `SourceAttribution.tsx` | 5.1.2 | Required |
| N-03 | "What if the AI is wrong?" | Correction history with diffs | `CorrectionLog.tsx` | 5.1.3 | Required |
| N-04 | "Is the system working?" | Live Trace visualization | `LiveTrace.tsx` | 5.1.4 | Required |
| N-05 | "Will this cost me money?" | $0.00 hard ceiling + circuit breaker | `CircuitBreaker.tsx` | 5.2.1 | Required |
| N-06 | "What if it gets stuck?" | Loop detection + fallback | `FallbackView.tsx` | 5.2.2 | Required |
| N-07 | "Is my data safe?" | 100% local inference | Architecture decision | 5.2.3 | Required |
| N-08 | "What if the system crashes?" | State persistence + checkpoints | `mother_agent.py` | 5.2.4 | Required |
| N-09 | "I hate waiting with no feedback" | Skeleton cards + progress + SSE | `SkeletonLoader.tsx` | 5.3.1 | Required |
| N-10 | "It looks broken on my screen" | 4K responsive (7 breakpoints) | `App_4K_Responsive.css` | 5.3.2 | Required |
| N-11 | "I can't use this on my phone" | Mobile-first responsive design | CSS + responsive components | 5.3.3 | Required |
| N-12 | "I need to understand quickly" | Dashboard with visual hierarchy | `Dashboard.tsx` | 5.3.4 | Required |
| N-13 | "It's too slow" | NF4 quantized models + caching | `critic_agent.py` | 5.4.1 | Required |
| N-14 | "The page takes forever to load" | Code splitting + lazy loading | Next.js App Router config | 5.4.2 | Required |
| N-15 | "Results appear all at once" | SSE streaming | `api/stream.ts` | 5.4.3 | Required |
| N-16 | "I want to ask follow-up questions" | Multi-turn conversation threading | `ConversationThread.tsx` | 5.5.1 | Required |
| N-17 | "I want to be notified when something happens" | Webhook/Slack alerts | `WebhookManager.ts` | 5.5.2 | Required |
| N-18 | "I want to choose which model to use" | Model selector dropdown | `ModelSelector.tsx` | 5.5.3 | Required |
| N-19 | "I want to track prompt changes" | Prompt version management | `PromptVersionManager.tsx` | 5.5.4 | Required |
| N-20 | "I want to annotate AI outputs" | Annotation/comment system | `AnnotationSystem.tsx` | 5.5.5 | Required |

### Reverse Traceability: Component-to-Need

This table verifies that no component exists without a user need justification.

| Component | Serves Need(s) | Orphan? |
|---|---|---|
| `ConfidenceGauge.tsx` | N-01 | No |
| `SourceAttribution.tsx` | N-02 | No |
| `CorrectionLog.tsx` | N-03 | No |
| `LiveTrace.tsx` | N-04 | No |
| `CircuitBreaker.tsx` | N-05 | No |
| `FallbackView.tsx` | N-06 | No |
| Architecture (local inference) | N-07 | No |
| `mother_agent.py` | N-08 | No |
| `SkeletonLoader.tsx` | N-09 | No |
| `App_4K_Responsive.css` | N-10, N-11 | No |
| CSS + responsive components | N-10, N-11 | No |
| `Dashboard.tsx` | N-12 | No |
| `critic_agent.py` | N-01, N-13 | No |
| Next.js App Router config | N-14 | No |
| `api/stream.ts` | N-09, N-15 | No |

### Cross-Cutting Concern Mapping

Some needs are served by multiple components working together. This table captures those relationships.

| Cross-Cutting Concern | Contributing Components | Needs Served |
|---|---|---|
| Trust signal display | `ConfidenceGauge.tsx`, `SourceAttribution.tsx`, `CorrectionLog.tsx` | N-01, N-02, N-03 |
| Real-time feedback | `LiveTrace.tsx`, `SkeletonLoader.tsx`, `api/stream.ts` | N-04, N-09, N-15 |
| Safety enforcement | `CircuitBreaker.tsx`, Architecture (local inference), `mother_agent.py` | N-05, N-07, N-08 |
| Responsive layout | `App_4K_Responsive.css`, CSS + responsive components, `Dashboard.tsx` | N-10, N-11, N-12 |
| Performance optimization | `critic_agent.py`, Next.js config, `api/stream.ts` | N-13, N-14, N-15 |

---

## 5.7 Quality Gates

No feature ships until it passes every quality gate. Each gate is a binary pass/fail. There are no exceptions and no waivers.

---

### Gate 1: Functional Completeness

| Attribute | Detail |
|---|---|
| **Gate** | Functional Completeness |
| **Criteria** | Every file from Sprint 3.1 exists, is complete, executes without errors |

#### Pass/Fail Criteria

| # | Criterion | Pass | Fail |
|---|---|---|---|
| FC-01 | All component files listed in the Sprint 3.1 manifest exist on disk | Every file present | Any file missing |
| FC-02 | All component files compile/transpile without errors | Zero compilation errors | Any compilation error |
| FC-03 | All component files render without runtime errors | Zero console errors during render | Any runtime error in console |
| FC-04 | All component files contain meaningful implementation (not stubs) | Every component renders its intended UI/logic | Any component is an empty stub, placeholder, or TODO-only |
| FC-05 | All Python modules import and execute without errors | `python -c "import module"` succeeds for all modules | Any import error |

#### Testing Methodology

| Method | Tool | Procedure |
|---|---|---|
| File existence check | Script + manifest file | Iterate through Sprint 3.1 file manifest. Verify each file exists at its expected path. |
| Compilation check | `tsc --noEmit` (TypeScript), `python -m py_compile` (Python) | Run compiler/linter on all source files. Zero errors required. |
| Runtime render check | React Testing Library + Jest | Mount each component in isolation. Verify no errors thrown during render. |
| Stub detection | Manual code review + automated LOC check | Any component with fewer than 10 lines of meaningful code (excluding imports/exports) is flagged for review. |

#### Required Evidence

- [ ] Sprint 3.1 file manifest checklist with all items checked
- [ ] CI build log showing zero compilation errors
- [ ] Test run output showing all components render without errors
- [ ] Code review sign-off confirming no stub components

---

### Gate 2: Agent Reliability

| Attribute | Detail |
|---|---|
| **Gate** | Agent Reliability |
| **Criteria** | Full pipeline runs end-to-end: query -> inference -> validation -> correction -> response |

#### Pass/Fail Criteria

| # | Criterion | Pass | Fail |
|---|---|---|---|
| AR-01 | A query enters the pipeline and a response exits the pipeline | Response is returned for 100% of test queries | Any query produces no response and no error |
| AR-02 | The inference agent produces output | Output text is non-empty for all test queries | Any query returns empty inference output |
| AR-03 | The critic agent evaluates the inference output | A confidence score (0-100) is returned for all test queries | Any query returns no confidence score |
| AR-04 | The correction agent modifies flagged claims | Corrections are applied when confidence < threshold | Flagged claims pass through uncorrected |
| AR-05 | The pipeline handles invalid/adversarial input | Graceful error message returned | Crash, hang, or unhandled exception |

#### Testing Methodology

| Method | Tool | Procedure |
|---|---|---|
| Happy-path end-to-end test | pytest + custom test harness | Submit 50 diverse test queries. Verify each produces a valid response with confidence score. |
| Adversarial input test | pytest | Submit 20 adversarial queries (empty string, 10000-token input, special characters, injection attempts). Verify graceful handling. |
| Pipeline step isolation test | pytest | Test each agent (inference, critic, correction) independently with known inputs. Verify expected outputs. |
| Regression test | pytest + snapshot testing | Compare current pipeline output to a baseline snapshot for 30 reference queries. Flag any unexpected changes. |

#### Required Evidence

- [ ] End-to-end test report: 50/50 queries produce valid responses
- [ ] Adversarial test report: 20/20 queries handled gracefully
- [ ] Agent isolation test report: all agents pass independently
- [ ] Regression test report: no unexpected output changes vs. baseline

---

### Gate 3: Circuit Breaker

| Attribute | Detail |
|---|---|
| **Gate** | Circuit Breaker |
| **Criteria** | Loop detection triggers correctly; token budget enforced; graceful degradation works |

#### Pass/Fail Criteria

| # | Criterion | Pass | Fail |
|---|---|---|---|
| CB-01 | Loop detection triggers after configured max rounds | Pipeline halts at round N+1 (where N is the configured max) | Pipeline runs beyond N+1 rounds |
| CB-02 | Token budget enforcement | Pipeline halts when token budget is exceeded | Pipeline continues after budget exceeded |
| CB-03 | Graceful degradation returns partial results | Partial results are returned with appropriate labeling | No results returned, or results returned without "partial" label |
| CB-04 | No external API calls are made | Zero outbound HTTP requests to paid services | Any outbound request to a paid API endpoint |
| CB-05 | Circuit breaker state is reported in the UI | Dashboard shows current circuit breaker status | Status indicator is missing or inaccurate |

#### Testing Methodology

| Method | Tool | Procedure |
|---|---|---|
| Loop injection test | pytest | Submit 10 queries designed to trigger correction loops. Verify loop detection triggers at the configured round limit. |
| Token budget test | pytest | Submit queries with known high token counts. Verify the pipeline halts at budget. Verify partial results. |
| Network audit | mitmproxy or tcpdump | Run 100 pipeline executions while capturing all network traffic. Verify zero outbound requests to paid API endpoints. |
| UI state test | Playwright | Trigger a circuit breaker event. Verify the dashboard updates within 1 second. |

#### Required Evidence

- [ ] Loop detection test report: 10/10 loops detected at correct round
- [ ] Token budget test report: budget enforced in all test cases
- [ ] Network capture log: zero paid API requests in 100 runs
- [ ] UI screenshot showing circuit breaker status after a trip event

---

### Gate 4: UI Responsiveness

| Attribute | Detail |
|---|---|
| **Gate** | UI Responsiveness |
| **Criteria** | All 7 breakpoints pass visual regression -- no overflow, no broken layouts |

#### Pass/Fail Criteria

| # | Criterion | Pass | Fail |
|---|---|---|---|
| UR-01 | Layout renders correctly at 320px | No overflow, no overlap, all content accessible | Any overflow, overlap, or inaccessible content |
| UR-02 | Layout renders correctly at 480px | No overflow, no overlap, all content accessible | Any overflow, overlap, or inaccessible content |
| UR-03 | Layout renders correctly at 768px | No overflow, no overlap, all content accessible | Any overflow, overlap, or inaccessible content |
| UR-04 | Layout renders correctly at 1024px | No overflow, no overlap, all content accessible | Any overflow, overlap, or inaccessible content |
| UR-05 | Layout renders correctly at 1280px | No overflow, no overlap, all content accessible | Any overflow, overlap, or inaccessible content |
| UR-06 | Layout renders correctly at 1920px | No overflow, no overlap, all content accessible | Any overflow, overlap, or inaccessible content |
| UR-07 | Layout renders correctly at 3840px | No overflow, no overlap, content fills space appropriately | Any overflow, overlap, or content too sparse |
| UR-08 | Layout transitions smoothly between breakpoints | No jarring jumps or flash of broken layout during resize | Visible layout breakage during transition |

#### Testing Methodology

| Method | Tool | Procedure |
|---|---|---|
| Automated screenshot comparison | Playwright + Percy or Chromatic | Capture screenshots at all 7 breakpoints. Compare against approved baselines. Flag pixel differences above threshold (0.1%). |
| Overflow detection | Playwright script | At each breakpoint, check every element for `scrollWidth > clientWidth` or `scrollHeight > clientHeight`. Any overflow is a failure. |
| Resize transition test | Playwright | Smoothly resize the viewport from 320px to 3840px over 10 seconds. Capture video. Review for layout breakage. |
| Cross-browser test | Playwright (Chromium, Firefox, WebKit) | Run the above tests in all three browser engines. |

#### Required Evidence

- [ ] Visual regression report with screenshots at all 7 breakpoints
- [ ] Overflow detection report: zero overflows detected
- [ ] Resize transition video: smooth transitions, no breakage
- [ ] Cross-browser test report: all tests pass in Chromium, Firefox, and WebKit

---

### Gate 5: Accessibility

| Attribute | Detail |
|---|---|
| **Gate** | Accessibility |
| **Criteria** | WCAG 2.1 AA audit passes -- screen reader, keyboard nav, focus management, contrast |

#### Pass/Fail Criteria

| # | Criterion | Pass | Fail |
|---|---|---|---|
| A11Y-01 | Automated WCAG 2.1 AA scan | Zero critical or serious violations | Any critical or serious violation |
| A11Y-02 | Keyboard navigation | Every interactive element is reachable via Tab/Shift+Tab. Focus order is logical. | Any interactive element is unreachable by keyboard. |

**Implementation Note:** A `focus-visible` polyfill is included for browsers that do not natively support the `:focus-visible` pseudo-class. The polyfill ensures that focus rings appear only on keyboard navigation, not on mouse/touch interaction, across all supported browsers.

| A11Y-03 | Focus management | Focus is trapped within modals when open. Focus returns to trigger element when modal closes. | Focus escapes modal or does not return to trigger. |
| A11Y-04 | Screen reader compatibility | All content is announced correctly. Dynamic updates (SSE events) are announced via ARIA live regions. | Any content is invisible to screen readers. |
| A11Y-05 | Color contrast | All text meets WCAG AA minimum contrast ratios (4.5:1 normal text, 3:1 large text) | Any text fails contrast ratio requirements. |
| A11Y-06 | Non-text indicators | Color is never the sole indicator of state (e.g., confidence score uses color + number + label) | Any state communicated by color alone. |

#### Testing Methodology

| Method | Tool | Procedure |
|---|---|---|
| Automated audit | axe-core (via Playwright or browser extension) | Run axe-core on every page/view of the dashboard. Zero critical/serious violations. |
| Keyboard walkthrough | Manual | Navigate the entire dashboard using only keyboard. Document the focus order. Verify all interactive elements are reachable. |
| Screen reader test | NVDA (Windows) / VoiceOver (macOS) | Navigate the dashboard with a screen reader. Verify all content is announced. Verify dynamic updates are announced. |
| Contrast check | WebAIM Contrast Checker or axe-core | Verify all text/background combinations meet WCAG AA ratios. |

#### Required Evidence

- [ ] axe-core report: zero critical/serious violations
- [ ] Keyboard navigation walkthrough document with focus order diagram
- [ ] Screen reader test recording or log with annotations
- [ ] Contrast ratio report for all color combinations used

---

### Gate 6: User Need Coverage

| Attribute | Detail |
|---|---|
| **Gate** | User Need Coverage |
| **Criteria** | Every row in Sprint 5 tables has a working feature in the dashboard |

#### Pass/Fail Criteria

| # | Criterion | Pass | Fail |
|---|---|---|---|
| UNC-01 | N-01: Confidence Score is displayed | Gauge renders with correct score, color, and tooltip | Gauge missing, score incorrect, or tooltip absent |
| UNC-02 | N-02: Source Attribution is functional | Citations are clickable and link to correct sources | Citations missing, non-clickable, or linking to wrong sources |
| UNC-03 | N-03: Correction History is accessible | Correction log shows before/after with reasoning | Log missing, incomplete, or inaccurate |
| UNC-04 | N-04: Live Trace is operational | Trace shows real-time agent execution with transitions | Trace missing, delayed > 500ms, or inaccurate |
| UNC-05 | N-05: Circuit Breaker enforces $0.00 ceiling | Zero external paid API calls; status indicator present | Any paid call detected; status indicator missing |
| UNC-06 | N-06: Loop Detection works | Loops detected and fallback renders partial results | Loop not detected or no fallback rendered |
| UNC-07 | N-07: Local Inference verified | Zero outbound data transfer during inference | Any outbound data transfer detected |
| UNC-08 | N-08: State Persistence works | Pipeline resumes from checkpoint after simulated crash | Pipeline restarts from scratch or loses data |
| UNC-09 | N-09: Loading Feedback appears | Skeleton cards appear within 100ms of query submission | No visual feedback for > 100ms |
| UNC-10 | N-10: 4K layout works | Dashboard renders correctly at 3840px | Layout broken at 4K |
| UNC-11 | N-11: Mobile layout works | Dashboard is fully functional at 320px | Layout broken or unusable on mobile |
| UNC-12 | N-12: Dashboard clarity achieved | Key metrics visible above fold on 1920x1080 | Key metrics require scrolling or navigation |
| UNC-13 | N-13: Inference is fast | Critic evaluation < 3s on GPU | Critic evaluation > 3s on GPU |
| UNC-14 | N-14: Page loads fast | TTI < 2s on broadband | TTI > 2s on broadband |
| UNC-15 | N-15: Streaming works | SSE events render incrementally | All results appear at once |

#### Testing Methodology

| Method | Tool | Procedure |
|---|---|---|
| Feature demonstration | Manual + screen recording | Walk through each of the 15 needs in sequence. Screen record the demonstration. Verify each feature functions as specified. |
| Automated smoke test | Playwright | Automated test script that submits a query, verifies skeleton, streaming, confidence gauge, citations, correction log, and trace are all rendered. |
| Coverage checklist | Sprint 5 acceptance criteria | Check each acceptance criterion (CS-01 through SR-06) against the running application. Mark pass/fail. |

#### Required Evidence

- [ ] Screen recording demonstrating all 15 user needs being met
- [ ] Automated smoke test report: all checks pass
- [ ] Signed-off acceptance criteria checklist with per-criterion pass/fail

---

### Gate 7: Zero-Cost Compliance

| Attribute | Detail |
|---|---|
| **Gate** | Zero-Cost Compliance |
| **Criteria** | No paid API calls, no paid services -- total cost remains $0.00 |

#### Pass/Fail Criteria

| # | Criterion | Pass | Fail |
|---|---|---|---|
| ZC-01 | No paid API endpoints are called | Zero requests to OpenAI, Anthropic, Cohere, Google AI, AWS Bedrock, Azure OpenAI, or any other paid inference API | Any request to a paid API endpoint |
| ZC-02 | No paid services are used | No paid databases, no paid hosting, no paid monitoring, no paid CDN | Any paid service dependency |
| ZC-03 | All models are local | All .gguf / .bin / .safetensors model files are loaded from local disk | Any model downloaded or accessed from a remote API at runtime |
| ZC-04 | Dependencies are free/open-source | All npm and pip dependencies are MIT, Apache 2.0, BSD, or equivalent free licenses | Any dependency with a paid license or usage-based pricing |
| ZC-05 | Runtime cost is $0.00 | Total cost after 1000 pipeline executions is $0.00 | Any non-zero cost |

#### Testing Methodology

| Method | Tool | Procedure |
|---|---|---|
| Network traffic capture | mitmproxy / Wireshark | Run 100 pipeline executions. Capture all outbound traffic. Verify zero requests to paid API endpoints. Generate a host-level traffic report. |
| Dependency license audit | `license-checker` (npm) / `pip-licenses` (Python) | Scan all installed dependencies. Flag any non-free license. |
| Model file audit | Manual + script | Verify all model files exist locally. Verify no download URLs are called during runtime. |
| Cost calculation | Manual | Sum all costs incurred: API calls ($0.00), hosting ($0.00), services ($0.00). Total must equal $0.00. |

#### Required Evidence

- [ ] Network traffic report: zero requests to paid endpoints in 100 runs
- [ ] Dependency license report: all dependencies are free/open-source
- [ ] Model file inventory: all files present locally with checksums
- [ ] Cost attestation: signed statement that total cost is $0.00

---

### Gate 8: Performance

| Attribute | Detail |
|---|---|
| **Gate** | Performance |
| **Criteria** | Critic evaluation < 3s; UI skeleton appears in < 100ms; SSE streaming functional |

#### Pass/Fail Criteria

| # | Criterion | Pass | Fail |
|---|---|---|---|
| P-01 | Critic evaluation latency (GPU, cold cache) | P50 < 3s, P95 < 5s | P50 >= 3s or P95 >= 5s |
| P-02 | Critic evaluation latency (GPU, warm cache) | < 200ms | >= 200ms |
| P-03 | Critic evaluation latency (CPU, cold cache) | P50 < 10s, P95 < 15s | P50 >= 10s or P95 >= 15s |
| P-04 | UI skeleton render time | < 100ms from query submission | >= 100ms |
| P-05 | SSE first event delivery | < 2s from query submission | >= 2s |
| P-06 | SSE event delivery reliability | 99.9%+ events delivered | < 99.9% events delivered |
| P-07 | Page Time to Interactive | < 2s on broadband | >= 2s |
| P-08 | Largest Contentful Paint | < 1.5s | >= 1.5s |

#### Testing Methodology

| Method | Tool | Procedure |
|---|---|---|
| Backend performance benchmark | pytest-benchmark | Run 100 queries on reference GPU hardware (NVIDIA RTX 3060 or Apple M1 8GB equivalent). Record P50, P95, P99 latencies. Repeat with warm cache. |
| CPU fallback benchmark | pytest-benchmark | Repeat the above on CPU-only. Record latencies. |
| UI render timing | React Profiler + Performance API | Instrument `SkeletonLoader.tsx` mount time. Measure from `onSubmit` event to first skeleton paint. |
| SSE delivery test | Custom test harness | Send 1000 SSE events. Verify delivery count and latency at the client. |
| Lighthouse audit | Lighthouse CI | Run Lighthouse on the dashboard. Verify TTI, LCP, and overall performance score. |

#### Required Evidence

- [ ] Backend benchmark report: P50/P95/P99 latencies for GPU and CPU
- [ ] Cache performance report: warm cache latency measurements
- [ ] UI timing report: skeleton render measurements across 50 page loads
- [ ] SSE delivery report: event count and latency statistics
- [ ] Lighthouse report: performance score 90+, TTI < 2s, LCP < 1.5s

---

## Appendix A: Persona Registry

| Persona | Role | Context | Primary Needs |
|---|---|---|---|
| **Fatima** | ML Engineer | Iterates on prompts, runs pipeline 50x/day, needs speed and debuggability | N-01, N-04, N-09, N-13 |
| **Derek** | Engineering Manager | Evaluates system for team, checks status between meetings, presents to stakeholders | N-01, N-05, N-12 |
| **Priya** | Data Scientist | Verifies claims against source material, needs citation accuracy | N-02 |
| **Marcus** | Compliance Officer | Needs audit trail, data residency guarantees, source traceability | N-02, N-07 |
| **Aisha** | Senior ML Engineer | Debugs pipeline, tunes critic, runs batch evaluations | N-03, N-06, N-13 |
| **Jordan** | End User | Submits queries, expects fast and clear responses, non-technical | N-01, N-09, N-12, N-15 |
| **Kai** | DevOps/MLOps Engineer | Monitors production, investigates latency, manages infrastructure | N-04, N-08, N-10 |
| **Sam** | Solo Developer | Runs locally, zero budget, processes proprietary code | N-05, N-07 |

## Appendix B: Acceptance Criteria ID Index

| ID Range | Section | Topic |
|---|---|---|
| CS-01 to CS-09 | 5.1.1 | Confidence Score |
| SA-01 to SA-08 | 5.1.2 | Source Attribution |
| CL-01 to CL-06 | 5.1.3 | Correction History |
| LT-01 to LT-06 | 5.1.4 | Live Trace |
| CB-01 to CB-06 | 5.2.1 | Circuit Breaker |
| LD-01 to LD-07 | 5.2.2 | Loop Detection |
| LI-01 to LI-05 | 5.2.3 | Local Inference |
| SP-01 to SP-06 | 5.2.4 | State Persistence |
| SL-01 to SL-07 | 5.3.1 | Skeleton Loader |
| RD-01 to RD-06 | 5.3.2 | Responsive Design |
| MF-01 to MF-06 | 5.3.3 | Mobile-First |
| DC-01 to DC-06 | 5.3.4 | Dashboard Clarity |
| IS-01 to IS-06 | 5.4.1 | Inference Speed |
| PL-01 to PL-06 | 5.4.2 | Page Load |
| SR-01 to SR-09 | 5.4.3 | Streaming Results |
| MT-01 to MT-06 | 5.5.1 | Multi-Turn Threading |
| WH-01 to WH-04 | 5.5.2 | Webhooks |
| MS-01 to MS-04 | 5.5.3 | Model Selector |
| PV-01 to PV-06 | 5.5.4 | Prompt Versions |
| AN-01 to AN-04 | 5.5.5 | Annotations |

**Total Acceptance Criteria: 119**
**Total User Needs: 20**
**Total Quality Gates: 8**
**Total Edge Cases: 68**

---

*This document is the source of truth for Sprint 5. If a feature is not mapped to a need in this document, it does not ship.*
