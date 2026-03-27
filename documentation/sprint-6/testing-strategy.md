# Sprint 6 -- Testing Strategy

| Field          | Value                                      |
| -------------- | ------------------------------------------ |
| **Sprint**     | 6                                          |
| **Document**   | Testing Strategy                           |
| **Status**     | Roadmap Only -- no implementation yet      |
| **Created**    | 2026-03-26                                 |
| **Audience**   | LLMOps Engineers, QA, Portfolio Reviewers  |
| **Depends on** | Sprint 3 (file manifest), Sprint 5 (perf) |

---

## Table of Contents

1. [6.1 Golden Test Set (100 Examples)](#61-golden-test-set-100-examples)
2. [6.2 pytest Integration](#62-pytest-integration)
3. [6.3 Coverage Targets](#63-coverage-targets)
4. [6.4 Test Categories](#64-test-categories)
5. [6.5 Performance Regression](#65-performance-regression)
6. [6.6 Cross-References](#66-cross-references)

---

## 6.1 Golden Test Set (100 Examples)

Every evaluation and regression test draws from a curated golden set of 100
query--response pairs, split evenly across four categories.

| Category       | Count | Description                                                                 | Source                              | Example                                                                 |
| -------------- | ----- | --------------------------------------------------------------------------- | ----------------------------------- | ----------------------------------------------------------------------- |
| Happy-path     | 25    | Well-formed queries with available context; expect high-confidence validated responses | Hand-authored from product FAQ corpus | "What is the refund policy?" with matching context chunk in the store   |
| Hallucination  | 25    | Queries designed to elicit fabricated claims; tests the Validator/Corrector loop       | Synthetically generated via GPT-4o  | "Who founded the company in 1987?" when no founding date exists in context |
| Adversarial    | 25    | Edge cases: empty strings, 10K-token inputs, injection attempts, special characters, Unicode | OWASP LLM Top-10 + custom fuzzing  | `""; DROP TABLE users; --"`, 10K-token padding, `\u0000` null bytes     |
| Edge-case      | 25    | Boundary conditions: exact threshold scores (0.7), timeout-inducing queries, model-switching triggers | Derived from Sprint 5 threshold tuning | Query that produces a validator confidence of exactly 0.700             |

The golden set is stored as `tests/fixtures/golden_100.json` and versioned
alongside the source code. Each entry carries a unique ID (`G-001` through
`G-100`), the expected outcome label, and the minimum acceptable confidence
band.

---

## 6.2 pytest Integration

### Naming Convention

All test files follow the pattern `test_<module>_<behavior>.py`:

- `test_graph_engine_retry_loop.py`
- `test_mother_agent_budget_enforcement.py`
- `test_critic_agent_confidence_thresholds.py`
- `test_evaluator_metric_computation.py`

### Fixtures

Shared fixtures are declared in `conftest.py` and injected via
`@pytest.fixture`:

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_ollama():
    """Return a patched httpx client that serves canned Ollama responses."""
    with patch("httpx.AsyncClient.post") as mocked:
        mocked.return_value = AsyncMock(
            status_code=200,
            json=lambda: {
                "model": "mistral:7b",
                "response": "Canned validated answer.",
                "done": True,
            },
        )
        # Configurable latency via side_effect when needed
        yield mocked

@pytest.fixture
def sample_state():
    """Provide a baseline AgentState dict for graph engine tests."""
    return {
        "query": "What is the refund policy?",
        "context": ["Refunds are available within 30 days."],
        "confidence": 0.0,
        "iteration": 0,
        "budget_remaining": 5,
    }

@pytest.fixture
def golden_test_set():
    """Load the full 100-example golden set from JSON fixture."""
    import json, pathlib
    path = pathlib.Path(__file__).parent / "fixtures" / "golden_100.json"
    return json.loads(path.read_text())

@pytest.fixture
def compiled_graph(mock_ollama):
    """Return a LangGraph CompiledGraph wired to the mock Ollama backend."""
    from app.graph_engine import build_graph
    return build_graph()
```

### Ollama Mock Strategy

All LLM calls route through `httpx.AsyncClient.post`. The mock factory in
`conftest.py` supports configurable latency and error injection:

```python
def ollama_mock_factory(latency_ms=0, status=200, body=None):
    """Build a mock post callable with tuneable latency and response."""
    import asyncio
    async def _post(*args, **kwargs):
        if latency_ms:
            await asyncio.sleep(latency_ms / 1000)
        resp = AsyncMock(status_code=status)
        resp.json.return_value = body or {"response": "mock", "done": True}
        return resp
    return _post
```

### Markers

```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
markers = [
    "slow: full pipeline tests (deselect with -m 'not slow')",
    "gpu: requires GPU-accelerated Ollama instance",
    "latency(max_ms): performance regression gate",
]
```

Usage in tests:

```python
@pytest.mark.slow
@pytest.mark.latency(max_ms=3000)
def test_full_pipeline_gpu_cold(compiled_graph, sample_state):
    ...
```

---

## 6.3 Coverage Targets

| Module              | Target | Rationale                                                        |
| ------------------- | ------ | ---------------------------------------------------------------- |
| **Overall backend** | 80%    | Baseline floor for production-grade LLMOps service               |
| `graph_engine.py`   | 90%    | Core state machine -- every branch matters for correctness       |
| `mother_agent.py`   | 90%    | Orchestrator -- budget enforcement paths must be fully tested    |
| `critic_agent.py`   | 85%    | LLM interface layer -- mock-heavy but all error paths covered    |
| `evaluator.py`      | 85%    | Metric computation paths -- rounding and threshold logic is critical |
| **Frontend overall**| 70%    | UI snapshot tests plus integration; lower bar reflects visual layer |

Coverage is enforced in CI via `pytest-cov` with `--cov-fail-under` flags per
module. The frontend uses Vitest's built-in `--coverage` reporter against the
same thresholds.

---

## 6.4 Test Categories

| Category              | Tool                          | Scope                                  | Count Target |
| --------------------- | ----------------------------- | -------------------------------------- | ------------ |
| Unit tests            | pytest                        | Individual functions and methods        | ~150 tests   |
| Integration tests     | pytest + real SQLite           | Agent-to-agent flows, DB round-trips   | ~40 tests    |
| Evaluation regression | pytest + golden set            | Compare scores across code changes     | ~100 tests   |
| UI snapshot           | Vitest + React Testing Library | Component render verification          | ~30 tests    |
| E2E smoke             | Playwright                    | Full query-to-response flow in browser | ~10 tests    |

**Total target: ~330 tests across all categories.**

- **Unit tests** run on every push and complete in under 60 seconds.
- **Integration tests** require a SQLite database fixture seeded by
  `conftest.py`; run on every PR.
- **Evaluation regression** loads `golden_100.json` and asserts that no metric
  degrades beyond the tolerance window (see Section 6.5).
- **UI snapshot** tests use `toMatchSnapshot()` to catch unintended render
  changes; reviewed on PR diff.
- **E2E smoke** tests launch the full stack via Docker Compose and exercise the
  critical path through a real browser; run nightly and on release branches.

---

## 6.5 Performance Regression

Latency targets are carried forward from the Sprint 5 acceptance criteria and
encoded as pytest markers so regressions fail the build automatically.

| Benchmark                  | Target    | Marker                          | Sprint 5 Ref |
| -------------------------- | --------- | ------------------------------- | ------------ |
| Critic evaluation (GPU cold) | < 3000 ms | `@pytest.mark.latency(max_ms=3000)` | IS-03        |
| Full pipeline (GPU cold)   | < 8000 ms | `@pytest.mark.latency(max_ms=8000)` | IS-01        |
| Full pipeline (warm cache) | < 1000 ms | `@pytest.mark.latency(max_ms=1000)` | IS-02        |
| SSE first event            | < 2000 ms | `@pytest.mark.latency(max_ms=2000)` | IS-05        |
| UI skeleton render         | < 100 ms  | `@pytest.mark.latency(max_ms=100)`  | IS-06        |

### Tracking and Thresholds

- Results are collected via `pytest-benchmark` with JSON output saved per
  commit under `.benchmarks/`.
- Each CI run compares the current benchmark JSON against the stored baseline.
- **Regression threshold:** a 15% degradation from baseline on any benchmark
  triggers a hard failure and blocks the merge.
- Baselines are updated explicitly via a manual `make benchmark-update` target;
  they never drift automatically.

---

## 6.6 Cross-References

This testing strategy ties into the following Sprint artifacts:

| Reference                     | Artifact                  | Relevant IDs / Sections                              |
| ----------------------------- | ------------------------- | ---------------------------------------------------- |
| Sprint 5 acceptance criteria  | `sprint-5/acceptance.md`  | IS-01 through IS-06 (latency), P-01 through P-08 (performance gates) |
| Sprint 3 file manifest        | `sprint-3/manifest.md`    | Test files map 1:1 to source files in the manifest   |
| CI/CD specification           | `ci-cd-spec.md`           | Test commands referenced in pipeline stages           |

### Mapping: Test Files to Source Files (Sprint 3 Manifest)

| Source File          | Test File(s)                                                        |
| -------------------- | ------------------------------------------------------------------- |
| `graph_engine.py`    | `test_graph_engine_retry_loop.py`, `test_graph_engine_state_transitions.py` |
| `mother_agent.py`    | `test_mother_agent_budget_enforcement.py`, `test_mother_agent_delegation.py` |
| `critic_agent.py`    | `test_critic_agent_confidence_thresholds.py`                        |
| `evaluator.py`       | `test_evaluator_metric_computation.py`                              |

### CI Pipeline Test Commands (from ci-cd-spec.md)

```bash
# Unit + Integration (runs on every push)
pytest tests/ -m "not slow and not gpu" --cov --cov-fail-under=80

# Full suite including slow + GPU (runs nightly)
pytest tests/ --cov --cov-fail-under=80 --benchmark-json=.benchmarks/latest.json

# Frontend snapshot + coverage
npx vitest run --coverage

# E2E smoke (runs on release branches)
npx playwright test tests/e2e/smoke.spec.ts
```

---

*End of Sprint 6 Testing Strategy. This document is a roadmap specification
only; no implementation artifacts exist yet.*
