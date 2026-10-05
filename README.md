# editalmind-ai

[![ci](https://github.com/For-Davi/editalmind-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/For-Davi/editalmind-ai/actions/workflows/ci.yml)

AI service of [EditalMind](https://github.com/For-Davi/editalmind): exam notice PDF pipeline, structured extraction with LLMs, RAG, AI agents (Tutor, Coach, question bank, Monitor), ML models and an MCP server.

**Stack:** Python 3.12, FastAPI, Celery with Redis, pydantic-settings, uv, Ruff, mypy (strict), pytest, Testcontainers.

## Architecture

Same Clean Architecture layers as the core API ([ADR-003](https://github.com/For-Davi/editalmind/blob/main/docs/adr/003-clean-architecture.md)), with two entry points sharing one image: the internal HTTP API and the Celery workers. Where agents are used and where fixed workflows are used is recorded in [ADR-007](https://github.com/For-Davi/editalmind/blob/main/docs/adr/007-agents-vs-workflows.md).

```text
src/editalmind_ai/
├── domain/                 # ports: LLM provider, agent contracts, memory, tracing
├── application/
│   └── agents/             # agent runtime, tools, Tutor, Coach, question bank, Monitor
├── infrastructure/         # adapters: LLM providers, databases, tracing, settings
├── presentation/
│   ├── http/               # internal API (FastAPI)
│   └── tasks/              # Celery tasks
├── prompts/                # versioned Jinja2 prompt templates
├── main.py                 # HTTP composition root (create_app)
└── worker.py               # Celery composition root
evals/                      # LLM and agent evaluations (real LLM, run separately)
tests/
├── unit/                   # fakes only: no broker, database, network or LLM
└── integration/            # real Redis and databases via Testcontainers
```

## Running

```bash
make install   # uv sync + pre-commit hooks
make run       # internal API on http://localhost:8001
make worker    # Celery worker (needs Redis from editalmind-infra)
```

Configuration comes from environment variables prefixed with `AI_` (see `.env.example`).

## Quality

```bash
make lint               # ruff check + ruff format --check + mypy strict
make test-unit
make test-integration   # starts a Redis container and a real Celery worker
make test               # both, with coverage (fails under 80%)
make evals              # real LLM, costs tokens
```

## Docker

The same image runs every process; the command selects which one:

```bash
docker build -t editalmind-ai .
docker run --rm -p 8001:8001 editalmind-ai                                   # internal API
docker run --rm editalmind-ai celery -A editalmind_ai.worker worker -l INFO  # worker
```
