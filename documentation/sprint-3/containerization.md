# Containerization Specification

| Field          | Value                                      |
| -------------- | ------------------------------------------ |
| **Document**   | Containerization & Docker Compose Spec     |
| **Sprint**     | Sprint 3                                   |
| **Status**     | Roadmap Only                               |
| **Author**     | Platform Engineering                       |
| **Created**    | 2026-03-26                                 |
| **References** | architecture.md, api-spec.md, file-manifest.md |

---

## Table of Contents

1. [Overview](#overview)
2. [Docker Compose Service Definitions](#docker-compose-service-definitions)
3. [GPU Passthrough Setup](#gpu-passthrough-setup)
4. [Dev vs Prod Compose Profiles](#dev-vs-prod-compose-profiles)
5. [Environment Variables](#environment-variables)
6. [One-Command Startup](#one-command-startup)
7. [Cross-References](#cross-references)

---

## 1. Overview

The Agentic Hallucination Guardrail system is containerized as three services orchestrated through Docker Compose. This spec defines the complete `docker-compose.yml`, GPU passthrough requirements, environment configuration, and profile-based workflows for development and production. The architecture relies on Docker as noted in **architecture.md** (tech stack) and exposes the health endpoint defined in **api-spec.md** (`GET /api/health`).

---

## 2. Docker Compose Service Definitions

The following `docker-compose.yml` defines the full stack. A single `docker compose up` command provisions the Ollama inference server (with automatic model pull), the FastAPI backend, and the Next.js frontend.

```yaml
version: "3.9"

services:
  # ── Ollama Inference Server ───────────────────────────────────────
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:11434/api/tags || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 3
    entrypoint: >
      /bin/sh -c "ollama serve & sleep 5 && ollama pull deepseek-r1:latest && wait"

  # ── FastAPI Backend ───────────────────────────────────────────────
  fastapi:
    build:
      context: ./src/backend
    ports:
      - "8000:8000"
    depends_on:
      ollama:
        condition: service_healthy
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - DATABASE_URL=sqlite:///data/traces.db
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/api/health || exit 1"]
      interval: 15s
      timeout: 5s
      retries: 3
    command: uvicorn api:app --host 0.0.0.0 --port 8000

  # ── Next.js Frontend ─────────────────────────────────────────────
  nextjs:
    build:
      context: ./src/frontend
    ports:
      - "3000:3000"
    depends_on:
      fastapi:
        condition: service_healthy
    environment:
      - NEXT_PUBLIC_API_URL=http://fastapi:8000
    command: pnpm start

volumes:
  ollama_data:
```

---

## 3. GPU Passthrough Setup

GPU inference through Ollama requires the NVIDIA Container Toolkit installed on the Docker host. Without it the `ollama` service will fail to reserve GPU devices.

### Prerequisites

1. **NVIDIA Driver** -- A compatible host driver (>=525.x) must already be installed.
2. **NVIDIA Container Toolkit** -- Install following the official guide:

```bash
# Add the package repository (Ubuntu/Debian)
distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
  | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L "https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list" \
  | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
  | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

3. **Verification** -- Confirm GPU visibility inside containers:

```bash
docker run --rm --gpus all nvidia/cuda:12.2.0-base-ubuntu22.04 nvidia-smi
```

> **Note:** On systems without a discrete NVIDIA GPU, remove the `deploy.resources.reservations` block from the `ollama` service. Ollama will fall back to CPU-only inference.

---

## 4. Dev vs Prod Compose Profiles

Compose profiles separate development conveniences (hot-reload, source mounts) from production-optimized builds.

### Development Profile

Create a `docker-compose.override.yml` or use the `dev` profile inline:

```yaml
# docker-compose.override.yml  (loaded automatically in dev)
services:
  fastapi:
    profiles: ["dev"]
    volumes:
      - ./src/backend:/app        # hot-reload source mount
      - ./data:/app/data
    command: uvicorn api:app --host 0.0.0.0 --port 8000 --reload
    environment:
      - LOG_LEVEL=debug

  nextjs:
    profiles: ["dev"]
    volumes:
      - ./src/frontend:/app       # hot-reload source mount
      - /app/node_modules          # anonymous volume to preserve deps
    command: pnpm dev
    environment:
      - NODE_ENV=development
```

Start with:

```bash
docker compose --profile dev up --build
```

### Production Profile

Production builds use multi-stage Dockerfiles with no source mounts and optimized settings:

```bash
docker compose --profile prod up -d --build
```

In production the FastAPI service runs without `--reload`, and the Next.js service uses `pnpm start` against a pre-built `.next` output directory.

---

## 5. Environment Variables

| Variable                | Service   | Default                        | Description                                      |
| ----------------------- | --------- | ------------------------------ | ------------------------------------------------ |
| `OLLAMA_HOST`           | fastapi   | `http://ollama:11434`          | Internal URL for the Ollama inference server      |
| `DATABASE_URL`          | fastapi   | `sqlite:///data/traces.db`     | SQLite connection string for hallucination traces |
| `LOG_LEVEL`             | fastapi   | `info`                         | Python logging level (debug, info, warning, error)|
| `NEXT_PUBLIC_API_URL`   | nextjs    | `http://fastapi:8000`          | Backend API base URL exposed to the browser       |
| `NODE_ENV`              | nextjs    | `production`                   | Node environment; `development` enables HMR       |

All variables can be overridden via a `.env` file placed at the repository root. Docker Compose loads `.env` automatically.

---

## 6. One-Command Startup

The entire stack -- including GPU provisioning and model download -- is designed around a single command:

```bash
docker compose up --build
```

### Startup Sequence

1. **ollama** starts first. Its entrypoint launches the Ollama server, waits 5 seconds for readiness, then pulls `deepseek-r1:latest` into the `ollama_data` volume. The health check confirms the `/api/tags` endpoint responds.
2. **fastapi** starts only after `ollama` reports healthy (`service_healthy`). It connects to Ollama over the internal Docker network at `http://ollama:11434` and exposes the `GET /api/health` endpoint (see **api-spec.md**).
3. **nextjs** starts only after `fastapi` reports healthy. The frontend is then available at `http://localhost:3000`.

Subsequent runs skip the model pull if `deepseek-r1:latest` already exists in the named volume, making restarts fast.

---

## 7. Cross-References

| Document              | Relevant Section                                                        |
| --------------------- | ----------------------------------------------------------------------- |
| **architecture.md**   | Tech stack -- Docker listed as the containerization platform            |
| **api-spec.md**       | `GET /api/health` -- endpoint used by the fastapi service health check  |
| **file-manifest.md**  | Project directory layout including `docker-compose.yml` and Dockerfiles |
