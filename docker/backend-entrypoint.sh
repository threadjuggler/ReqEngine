#!/usr/bin/env sh
# Runs Alembic migrations then starts the uvicorn server for the ReqEngine backend.
set -e

echo "Running alembic upgrade…"
uv run alembic upgrade head

echo "Starting uvicorn (${UVICORN_WORKERS:-4} workers)…"
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers "${UVICORN_WORKERS:-4}"
