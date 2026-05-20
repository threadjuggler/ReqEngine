# ReqEngine Backend

FastAPI + SQLAlchemy 2 async backend for the ReqEngine requirements management system.

## Quick start (dev)

```bash
cd backend
uv sync
uv run ruff check .
uv run python -c "from app.main import app"
DATABASE_URL=postgresql+asyncpg://appuser:pw@localhost:5432/reqengine uv run alembic upgrade head
```

See `tasks.md` at the repo root for the full plan.
