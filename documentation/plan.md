Plan to implement │
│ │
│ Plan: Achieve 9.8+ Combined Score (from 9.16) │
│ │
│ Context │
│ │
│ The Agentic Hallucination Guardrail project has been fully specified across 6 sprints, │
│ critiqued (v2.1.0), and audited (QA backend + frontend reports). Current combined score is │
│ 9.16/10 (top 5%). The goal is to reach 9.8/10 (top 1%) by closing every documented gap. │
│ │
│ The single biggest drag is User Likability at 7.3/10 — fixing this alone accounts for 40% of │
│ the total improvement needed. The second biggest drag is 4 missing "production instinct" │
│ documents (testing, Docker, CI, API spec) that cap the backend at 8.97. │
│ │
│ All changes are markdown documentation edits — no code. │
│ │
│ --- │
│ Phase 1: Create 4 New Production Documents (Backend 8.97→9.35, Likability 7.3→8.8) │
│ │
│ These 4 files represent the "production instincts" that hiring managers look for. Their │
│ absence is the #1 backend score blocker. │
│ │
│ 1A. sprint-6/testing-strategy.md (NEW) │
│ │
│ - Golden test set: 100 examples (25 happy-path, 25 hallucination, 25 adversarial, 25 │
│ edge-case) │
│ - pytest integration: naming conventions, fixtures, Ollama mock strategy │
│ - Coverage targets: 80% backend, 90% for graph_engine.py + mother_agent.py │
│ - Test categories: unit, integration, evaluation regression, UI snapshot │
│ - Performance regression: Sprint 5 latency targets as pytest markers │
│ │
│ 1B. sprint-3/containerization.md (NEW) │
│ │
│ - docker-compose.yml spec: 3 services (Ollama, FastAPI, Next.js) │
│ - docker compose up one-command start with model auto-pull │
│ - Volume mounts, GPU passthrough, health checks, env vars │
│ - Dev vs prod compose profiles │
│ - Score impact: +1.5 likability for Sam and Kai │
│ │
│ 1C. sprint-3/ci-cd-spec.md (NEW) │
│ │
│ - GitHub Actions workflow: lint (ruff+eslint) → type-check (mypy+tsc) → test (pytest+vitest) → │
│ build │
│ - Branch protection, caching, CI badge │
│ │
│ 1D. sprint-3/api-spec.md (NEW) │
│ │
│ - Endpoints: POST /api/query, GET /api/stream/{trace_id}, GET /api/health, GET /api/config, │
│ GET /api/traces/{trace_id} │
│ - Request/response JSON schemas, SSE event format, error format │
│ │
│ --- │
│ Phase 2: Add 5 User Likability Specs to Sprint 5 (Likability 8.8→9.3) │
│ │
│ File: sprint-5/acceptance-criteria.md — add 5 new sections (5.5.1–5.5.5) │
│ │
│ ┌─────────┬────────────────────────────────────────────────────────┬─────────────┬─────────┐ │
│ │ Section │ Feature │ Personas │ Impact │ │
│ ├─────────┼────────────────────────────────────────────────────────┼─────────────┼─────────┤ │
│ │ 5.5.1 │ Multi-turn conversation threading │ Jordan, │ +1.0 │ │
│ │ │ │ Fatima │ each │ │
│ ├─────────┼────────────────────────────────────────────────────────┼─────────────┼─────────┤ │
│ │ 5.5.2 │ Webhook/Slack alert integration │ Derek, Kai │ +1.0 │ │
│ │ │ │ │ each │ │
│ ├─────────┼────────────────────────────────────────────────────────┼─────────────┼─────────┤ │
│ │ 5.5.3 │ Model selector dropdown (auto-discovers Ollama models) │ Fatima, │ +1.0 │ │
│ │ │ │ Aisha │ each │ │
│ ├─────────┼────────────────────────────────────────────────────────┼─────────────┼─────────┤ │
│ │ 5.5.4 │ Prompt version management (version-stamped prompts, │ Fatima, │ +1.5 │ │
│ │ │ diff view, A/B comparison) │ Aisha │ each │ │
│ ├─────────┼────────────────────────────────────────────────────────┼─────────────┼─────────┤ │
│ │ 5.5.5 │ Annotation/comment system (inline claim annotations, │ Priya, │ +1.0 │ │
│ │ │ export, audit trail) │ Marcus │ each │ │
│ └─────────┴────────────────────────────────────────────────────────┴─────────────┴─────────┘ │
│ │
│ --- │
│ Phase 3: Fix Backend Component Gaps (~21 edits across 4 files) │
│ │
│ sprint-0/research.md (3 edits) │
│ │
│ - Add citation sources for prevalence percentages (Section 0.2 Root Causes) │
│ - Add Mistral 7B + Gemma 2 to model table + fallback priority column │
│ - Add subsection 0.1.5a "Alternative Inference Engines" (vLLM, SGLang, Haystack — │
│ acknowledged, rationale for Ollama) │
│ │
│ sprint-1/architecture.md (6 edits) │
│ │
│ - Replace hardcoded timeouts with config references (config.inference_timeout) │
│ - Add jitter spec to retry loop (+/- 10% random) │
│ - Add schema_version: int to State Schema │
│ - Add note about parallel evaluation (RAGAS + DeepEval run via asyncio.gather) │
│ - Add per-metric kill switches (disable individual metrics via validation_rules.json) │
│ - Add Docker to technology stack table │
│ │
│ sprint-2/agent-design.md (9 edits) │
│ │
│ - Cross-reference heartbeat interval to config │
│ - Specify token ceiling configuration method (default 8192, configurable, API overridable) │
│ - Add concrete conflict scenario walkthrough │
│ - Explain Corrector→Critic data flow through Mother Agent (~5ms snapshot latency) │
│ - Add Agent Name Mapping Table (Sprint 1 → Sprint 2 → LangGraph node names) │
│ - Add DLQ size limit (1000 global, FIFO eviction) │
│ - Map health check to GET /api/health │
│ - Define graceful shutdown steps (5 explicit steps) │
│ - Add probability/impact numeric scores to risk register │
│ │
│ sprint-3/file-manifest.md (3 edits) │
│ │
│ - Add "Est. LOC" column to master file index │
│ - Add circular import resolution note (dependency injection breaks cycle) │
│ - Add sprint timeline mapping (Sprint 6: P0+P1, Sprint 7: P2, Sprint 8: P3, Sprint 9: P4) │
│ │
│ --- │
│ Phase 4: Fix Frontend Component Gaps (~16 edits across 2 files) │
│ │
│ skeleton-diagrams.md (12 edits) │
│ │
│ - Add clamp formulas for all 11 typography elements (not just 3) │
│ - Add fluid spacing formula with example │
│ - Specify PDF export engine: html2pdf.js (client-side, zero server) │
│ - Specify fuzzy search: Fuse.js with threshold 0.3 │
│ - Add max localStorage history: 500 items, 5MB budget │
│ - Specify notification click: navigate + close panel │
│ - Describe onboarding illustration (magnifying glass + checkmark + shield SVG) │
│ - Specify dark mode transition (200ms ease-out on CSS custom properties) │
│ - Add reduced-motion for indeterminate progress bar (static dashed pattern) │
│ - Add nested modal policy (not supported — close parent first) │
│ - Specify virtualization threshold: 100 trace entries → react-window │
│ - Add GPU acceleration hints (will-change, translateZ(0)) │
│ │
│ sprint-4/ux-standards.md (4 edits) │
│ │
│ - Add updated wireframes cross-reference for 768px, 2560px, 3840px │
│ - Add browser shortcut collision analysis table (Ctrl+K vs address bar, etc.) │
│ - Add stylus input testing note to touch targets │
│ - Add dark mode contrast verification ratios table │
│ │
│ --- │
│ Phase 5: Add Sprint 5 Acceptance Criteria (~14 edits) │
│ │
│ File: sprint-5/acceptance-criteria.md │
│ │
│ - CS-09: Confidence score persistence across page reload (localStorage) │
│ - SA-07/SA-08: Citation export (BibTeX/JSON) + citation search │
│ - LD-07: Batch loop isolation (query #12 loop doesn't block #13-50) │
│ - SL-07: CLS < 0.05 during skeleton-to-content transition │
│ - SR-07/SR-08/SR-09: SSE reconnection with catch-up, partial chunk buffering, out-of-order │
│ reordering │
│ - LT-07/LT-08: Trace comparison (side-by-side) + trace search │
│ - PL-06: Turbopack as build tool │
│ - Add focus-visible polyfill note to keyboard navigation │
│ │
│ --- │
│ Score Projection │
│ │
│ ┌────────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────┐ │
│ │ Dimension │ Current │ Phase 1 │ Phase 2 │ Phase 3 │ Phase 4 │ Phase 5 │ │
│ ├────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤ │
│ │ Backend │ 8.97 │ 9.35 │ 9.35 │ 9.65 │ 9.65 │ 9.80 │ │
│ ├────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤ │
│ │ Frontend │ 9.10 │ 9.10 │ 9.20 │ 9.20 │ 9.55 │ 9.75 │ │
│ ├────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤ │
│ │ Market │ 9.40 │ 9.50 │ 9.60 │ 9.60 │ 9.60 │ 9.60 │ │
│ ├────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤ │
│ │ Likability │ 7.30 │ 8.80 │ 9.30 │ 9.30 │ 9.50 │ 9.60 │ │
│ ├────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤ │
│ │ Combined │ 9.16 │ 9.40 │ 9.52 │ 9.62 │ 9.72 │ 9.82 │ │
│ └────────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────┘ │
│ │
│ --- │
│ Files Summary │
│ │
│ ┌────────┬─────────────────────────────────┬───────┬────────────┐ │
│ │ Action │ Path │ Phase │ Est. Lines │ │
│ ├────────┼─────────────────────────────────┼───────┼────────────┤ │
│ │ CREATE │ sprint-6/testing-strategy.md │ 1 │ ~120 │ │
│ ├────────┼─────────────────────────────────┼───────┼────────────┤ │
│ │ CREATE │ sprint-3/containerization.md │ 1 │ ~100 │ │
│ ├────────┼─────────────────────────────────┼───────┼────────────┤ │
│ │ CREATE │ sprint-3/ci-cd-spec.md │ 1 │ ~80 │ │
│ ├────────┼─────────────────────────────────┼───────┼────────────┤ │
│ │ CREATE │ sprint-3/api-spec.md │ 1 │ ~100 │ │
│ ├────────┼─────────────────────────────────┼───────┼────────────┤ │
│ │ EDIT │ sprint-5/acceptance-criteria.md │ 2,5 │ ~280 added │ │
│ ├────────┼─────────────────────────────────┼───────┼────────────┤ │
│ │ EDIT │ sprint-0/research.md │ 3 │ ~60 added │ │
│ ├────────┼─────────────────────────────────┼───────┼────────────┤ │
│ │ EDIT │ sprint-1/architecture.md │ 3 │ ~50 added │ │
│ ├────────┼─────────────────────────────────┼───────┼────────────┤ │
│ │ EDIT │ sprint-2/agent-design.md │ 3 │ ~100 added │ │
│ ├────────┼─────────────────────────────────┼───────┼────────────┤ │
│ │ EDIT │ sprint-3/file-manifest.md │ 3 │ ~30 added │ │
│ ├────────┼─────────────────────────────────┼───────┼────────────┤ │
│ │ EDIT │ skeleton-diagrams.md │ 4 │ ~60 added │ │
│ ├────────┼─────────────────────────────────┼───────┼────────────┤ │
│ │ EDIT │ sprint-4/ux-standards.md │ 4 │ ~40 added │ │
│ └────────┴─────────────────────────────────┴───────┴────────────┘ │
│ │
│ Total: 4 new files + 7 edited files = ~60 edits, ~930 lines added │
│ │
│ --- │
│ Verification │
│ │
│ After all phases complete: │
│ 1. Re-run component scoring against each audit criterion │
│ 2. Verify no cross-document conflicts introduced │
│ 3. Confirm all 8 backend gaps from qa-audit Section 4 are resolved │
│ 4. Confirm all 6 likability enhancements from qa-audit-frontend Section 4.2 are addressed │
│ 5. Confirm agent naming is reconciled across Sprint 1, 2, and 3 │
│ 6. Grep for any remaining "TODO", "TBD", or "unspecified" in all documents
