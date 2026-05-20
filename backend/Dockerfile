# Placeholder — full Docker integration is Phase 5.
# Build with: docker build -t reqengine-backend .
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

# Run migrations then start the server
CMD ["sh", "-c", "uv run alembic upgrade head && uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers ${UVICORN_WORKERS:-4}"]
