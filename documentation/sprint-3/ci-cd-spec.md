# CI/CD Pipeline Specification

| Field          | Value                                      |
| -------------- | ------------------------------------------ |
| **Sprint**     | Sprint 3                                   |
| **Status**     | Roadmap Only                               |
| **Type**       | Specification Document                     |
| **System**     | Agentic Hallucination Guardrail (LLMOps)   |
| **Last Updated** | 2026-03-26                               |

![CI](https://github.com/{owner}/{repo}/actions/workflows/ci.yml/badge.svg)

---

## Table of Contents

1. [GitHub Actions Workflow](#github-actions-workflow)
2. [Branch Protection Rules](#branch-protection-rules)
3. [Caching Strategy](#caching-strategy)
4. [Cross-References](#cross-references)

---

## GitHub Actions Workflow

The pipeline triggers on every push to `main` and on pull requests targeting `main`. Jobs run in strict sequence: **lint --> type-check --> test --> build**. A matrix strategy covers Python 3.11 + 3.12 and Node.js 20 + 22.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
        node-version: [20, 22]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: pip-${{ hashFiles('requirements.txt') }}
      - uses: actions/cache@v4
        with:
          path: $(pnpm store path)
          key: pnpm-${{ hashFiles('pnpm-lock.yaml') }}
      - run: pip install ruff
      - run: ruff check src/backend/ --select E,W,F,I
      - run: pnpm install --frozen-lockfile
      - run: pnpm eslint src/frontend/ --ext .ts,.tsx
      - run: markdownlint docs/**/*.md || true  # optional, non-blocking

  type-check:
    needs: lint
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
        node-version: [20, 22]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: pip-${{ hashFiles('requirements.txt') }}
      - uses: actions/cache@v4
        with:
          path: $(pnpm store path)
          key: pnpm-${{ hashFiles('pnpm-lock.yaml') }}
      - run: pip install mypy
      - run: mypy src/backend/ --strict
      - run: pnpm install --frozen-lockfile
      - run: pnpm tsc --noEmit

  test:
    needs: type-check
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
        node-version: [20, 22]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: pip-${{ hashFiles('requirements.txt') }}
      - uses: actions/cache@v4
        with:
          path: $(pnpm store path)
          key: pnpm-${{ hashFiles('pnpm-lock.yaml') }}
      - run: pip install pytest pytest-cov
      - run: pytest src/backend/tests/ -v --cov=src/backend --cov-report=xml
      - run: pnpm install --frozen-lockfile
      - run: pnpm vitest run --coverage
    # Coverage thresholds (enforced via config):
    #   - Backend overall: 80%
    #   - graph_engine.py: 90%
    #   - mother_agent.py: 90%

  build:
    needs: test
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [20, 22]
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t guardrail-backend ./src/backend
      - uses: pnpm/action-setup@v3
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - uses: actions/cache@v4
        with:
          path: $(pnpm store path)
          key: pnpm-${{ hashFiles('pnpm-lock.yaml') }}
      - run: pnpm install --frozen-lockfile
      - run: pnpm build  # Next.js production build
```

### Coverage Thresholds

| Scope                | Minimum Coverage |
| -------------------- | ---------------- |
| Backend overall      | 80%              |
| `graph_engine.py`    | 90%              |
| `mother_agent.py`    | 90%              |
| Frontend (vitest)    | Per vitest config |

---

## Branch Protection Rules

The following rules are applied to the `main` branch:

| Rule                          | Setting   |
| ----------------------------- | --------- |
| Require passing CI            | Enabled   |
| Required approving reviews    | 1         |
| Dismiss stale reviews         | Enabled   |
| Require up-to-date branches   | Enabled   |
| Allow force pushes            | Disabled  |
| Allow deletions               | Disabled  |

---

## Caching Strategy

| Cache Target      | Path               | Key                                    |
| ------------------ | ------------------ | -------------------------------------- |
| pip dependencies   | `~/.cache/pip`     | `pip-${{ hashFiles('requirements.txt') }}` |
| pnpm store         | pnpm store path    | `pnpm-${{ hashFiles('pnpm-lock.yaml') }}` |

Both caches use `actions/cache@v4`. Restoring from cache avoids redundant network fetches and keeps pipeline duration low across the matrix of Python 3.11/3.12 and Node.js 20/22 runners.

---

## Cross-References

- **[testing-strategy.md](testing-strategy.md)** -- authoritative source for all test commands, fixtures, and coverage configuration.
- **[containerization.md](containerization.md)** -- defines the Dockerfile and build context consumed by the `build` job.
