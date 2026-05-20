# ReqEngine — Robot Framework API Tests

Robot Framework tests that exercise the backend HTTP API end-to-end.

## Prerequisites

The tests depend on the `tests` dependency group declared in `backend/pyproject.toml`.
Install it once from the `backend/` directory:

```bash
cd backend
uv sync --group tests
cd ..
```

## Running the tests

### Option A — Local backend

Start the backend in one shell:

```bash
cd backend
uv run uvicorn app.main:app --reload
```

Then run the tests from the repo root in another shell:

```bash
uv --project backend run robot tests/
```

Or with a custom base URL:

```bash
uv --project backend run robot --variable API_BASE_URL:http://localhost:8000/api tests/
```

### Option B — Docker Compose stack

```bash
docker compose up -d
uv --project backend run robot tests/
```

### Dry-run (syntax check — no live server needed)

```bash
uv --project backend run robot --dryrun tests/
```

## Test suites

| File | Description |
|------|-------------|
| `01_requirements_crud.robot` | Requirement CRUD happy path (reserve, create, get, list, update, delete) |
| `02_links.robot` | Link create/delete, validation, and cascade on requirement delete |
| `03_id_allocation.robot` | project_id uniqueness, monotonic increase, and format check |
| `04_sanitization.robot` | HTML script/img tag stripping and oversized title rejection |
| `05_testcases.robot` | GET /testcases: at least 3 seeded rows with expected titles |

## Shared resources

| File | Description |
|------|-------------|
| `__resources/variables.resource` | `${API_BASE_URL}` variable (overridable via env `API_BASE_URL`) |
| `__resources/api.resource` | Session setup and reusable request helper keywords |

## Overriding the base URL

Set the environment variable before running:

```bash
export API_BASE_URL=http://myserver:8000/api
uv --project backend run robot tests/
```

Or pass it on the command line:

```bash
uv --project backend run robot --variable API_BASE_URL:http://myserver:8000/api tests/
```
