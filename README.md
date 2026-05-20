# ReqEngine

A lightweight requirements and test-case management tool (Polarion-lite).

---

## Run it (Docker)

**Prerequisites:** Docker and Docker Compose v2.

```bash
git clone <repo-url> ReqEngine
cd ReqEngine
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs

**Hot reload notes:**
- Frontend edits under `frontend/src/` hot-reload automatically (Vite polling watcher).
- Backend edits under `backend/app/` or `backend/alembic/` take effect after a container restart (`docker compose restart backend`). The backend runs 4 workers and does not use `--reload`.

---

## Local dev without Docker

**Backend:**

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Requires a local PostgreSQL and Redis instance. Copy `.env.example` to `.env` and adjust `DATABASE_URL` and `REDIS_URL` to point at your local services.

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Opens on http://localhost:5173. Set `VITE_API_BASE_URL=http://localhost:8000/api` in `frontend/.env.local` if needed.

---

## Ruff (backend linting)

```bash
cd backend
uv run ruff check .
```

---

## Tests (Robot Framework)

Tests live under `tests/` and target the running backend over HTTP.

```bash
# Install the tests dependency group once
uv --project backend sync --group tests

# Start the backend (either docker compose up -d, or locally)

# Dry-run (syntax + keyword resolution check, no live server needed):
uv --project backend run robot --dryrun tests/

# Full run against a running backend:
uv --project backend run robot tests/
```

Override the API base URL with:

```bash
API_BASE_URL=http://my-host:8000/api uv --project backend run robot tests/
```
