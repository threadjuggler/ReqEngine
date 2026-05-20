# ReqEngine — Tasks (Step 1)

This file logs the planned tasks for the first incremental step of the project, per `projekt_neu.md` and `implementation_rules.md`. The Opus agent maintains this file; Sonnet 4.6 implementer agents do the actual file creation, with review afterwards.

Hardcoded values for step 1:
- `project_name = "Project1"`
- `user_name = "User1"` (used for `author` / `last_edited_by`)

## Phase 0 — Open questions — RESOLVED 2026-05-20
- Q1 ID allocation: **Reserve at form-open** via `POST /api/requirements/reserve-id`.
- Q2 list_of_links storage: **Derived** from `Link` table; not a stored column.
- Q3 Sanitization: **Strip all HTML — plain text only**. Use `bleach.clean(..., tags=[], strip=True)` plus length/UTF-8 checks.
- Q4 Frontend serving: **Vite dev server with hot reload** in Docker.
- Q5 Workers: env var `UVICORN_WORKERS`, **default 4**.
- Q6 Link input ID: **Human `project_id`** like `Project1_00000007`; backend resolves to numeric id.
- Q7 Revision: **free-text editable field, default `'0.1'`**.
- Q8 Default status: **`'draft'`**.

## Phase 1 — Repository scaffolding
1. Create top-level layout: `backend/`, `frontend/`, `docker/`, `tests/` (Robot Framework).
2. Add `pyproject.toml` under `backend/` managed by **uv**, with deps: fastapi, uvicorn[standard], sqlalchemy, asyncpg, alembic, redis, pydantic, pydantic-settings, bleach, python-dotenv.
3. Add `ruff` config (in `backend/pyproject.toml`) — line length 100, target py3.12.
4. Add `tests/` group deps: robotframework, robotframework-requests.
5. Update `.env.example` for Postgres (port 5432) + Redis + backend settings; keep MySQL block removed.

## Phase 2 — Backend models & migrations
1. SQLAlchemy models:
   - `Requirement` — all attributes per spec, plus `requirement_number` (int, indexed) for the per-project counter.
   - `Link` — per spec, with FK to `Requirement` for `link_start` and `link_destination` (CHECK constraint `link_start <> link_destination`).
   - `Testcase` — per spec.
   - `ProjectCounter` — `(project_name PK, next_number int)` for atomic `requirement_number` allocation.
2. Alembic init + first migration creating all four tables.
3. Seed script (run on container start, idempotent): inserts `ProjectCounter("Project1", 1)` and three Testcases with short lorem-ipsum text.

## Phase 3 — Backend API
Routes under `/api`:
- `POST /api/requirements/reserve-id` → atomically increments `ProjectCounter`, returns `{ project_id, requirement_number }` reserved for a new requirement. Used when frontend opens the "new" form.
- `GET /api/requirements` → list (id, project_id, title, status, requirement_type, last_edited_on).
- `GET /api/requirements/{id}` → full requirement including resolved `list_of_links` (each item shows link_id, the other side's requirement id + project_id, link_type).
- `POST /api/requirements` → create using a reserved `requirement_number` + `project_id`. Validates sanitization; sets `author`, `last_edited_by`, timestamps.
- `PUT /api/requirements/{id}` → edit. Updates `last_edited_by`, `last_edited_on`.
- `DELETE /api/requirements/{id}` → deletes the requirement and any links referencing it.
- `POST /api/links` → create link `{link_type, link_start, link_destination}`; validates start≠destination; appended to the start requirement's link list.
- `DELETE /api/links/{link_id}` → removes the link row.
- `GET /api/testcases` → list (read-only for step 1).

Input sanitization: a single helper validates strings are UTF-8, length-bounded, and HTML-sanitized via `bleach` (policy chosen in Phase 0 Q3).

## Phase 4 — Frontend (React)
1. Vite + React + TypeScript app under `frontend/`.
2. Routes:
   - `/` → list view of all requirements with columns (project_id, title, status, type, last_edited_on) and a "New Requirement" button.
   - `/requirements/:id` → edit form.
   - `/requirements/new` → new form (calls reserve-id on mount).
3. Edit form fields per spec (project_id shown as non-editable label). Buttons: Save / Clear Form / Discard.
4. Links section: scrollable container (horizontal+vertical scroll) listing each link with a `-` button (deletes the link). Below it: "Create Link" button opening a modal with link_type dropdown, link_start input, link_destination input, Save / Discard.
5. Each link line is a clickable hyperlink to the requirement on the "other side" of the link. If the form has unsaved edits, a confirm dialog appears before navigating away.
6. Display of `author`, `last_edited_by`, `created_on`, `last_edited_on`, `revision` as read-only.

## Phase 5 — Docker
1. `docker/Dockerfile.backend` — uv-based image, runs alembic upgrade + seed + uvicorn (workers count from env).
2. `docker/Dockerfile.frontend` — Vite build + nginx serve (or Vite dev server, see Phase 0 Q4).
3. `docker-compose.yml` at repo root with services: `postgres`, `redis`, `backend`, `frontend`. `backend` depends_on healthy `postgres` + `redis`. Single `docker compose up` brings everything up after `git clone`.

## Phase 6 — Tests (Robot Framework)
1. Suite: requirement CRUD happy path.
2. Suite: link create/delete + cascade rules.
3. Suite: project_id allocation under concurrent reserve calls (sanity, not stress).
4. Suite: input sanitization (script tags rejected/escaped).
5. Add `make test` / uv script that boots the stack via docker compose and runs `robot tests/`.

## Phase 7 — Ruff + CI checks (local)
Add `uv run ruff check` script; document in README.

## Phase 8 — Wrap-up
1. Update `README.md` with run instructions.
2. Final review of all code by Opus agent before declaring step 1 done.

---

## Progress log

- 2026-05-20: tasks.md drafted; Phase 0 questions raised.
- 2026-05-20: Phase 0 resolved (see top of file).
- 2026-05-20: Spawning Sonnet 4.6 implementer for Phase 1 (scaffolding) + Phase 2 (models, alembic, seed) + Phase 3 (API).
- 2026-05-20: Phases 1–3 implemented by Sonnet 4.6. See report below.
- 2026-05-20: Opus review — fixed missing `Link.project_id`. **Design decision:** the `ProjectCounter` is now a *shared* sequence across Requirements, Links, and Testcases — every object that belongs to a project draws its `project_id` from the same counter. The seed of 3 testcases consumes counter values 1–3, so the first user-created requirement gets `Project1_00000004`. Renamed `reserve_requirement_number` → `reserve_project_number`; added `format_project_id(project_name, n)` helper; Link gets a unique `project_id` allocated on insert; Testcase seed deduplicates by title (since project_id is no longer hardcoded).
- 2026-05-20: Phase 4 (frontend) implemented by Sonnet 4.6. `npm run build` clean, TypeScript strict, Vite 5.4 / React 18.3 / React Router 6.30 (downgraded from latest because host runs Node 18.19). See report below.
- 2026-05-20: Opus spot-check — `npm run build` re-verified locally; `links-box` CSS confirmed `overflow: auto` for the spec'd horizontal+vertical scrolling. Proceeding to Phase 5 (Docker).
- 2026-05-20: Phase 5 (Docker) implemented by Sonnet 4.6. `docker compose config` passes; frontend rebuild clean after vite.config.ts changes. Entrypoint is inlined into the backend Dockerfile because the build context (`./backend`) cannot reach `../docker/`. Bind mounts on `backend/app` + `backend/alembic` give partial dev convenience (full reload requires `docker compose restart backend` since workers=4). Frontend hot reload works via bind-mount + `usePolling`.
- 2026-05-20: Phase 6 (Robot Framework tests) implemented by Sonnet 4.6. 23 tests across 5 suites; `robot --dryrun tests/` passes all 23. Suites cover requirement CRUD, links + cascade, project_id allocation/format, sanitization, and seeded testcases.
- 2026-05-20: Phase 7 (ruff) — already satisfied during Phase 1 (`uv run ruff check .` in backend/); README documents it.
- 2026-05-20: Phase 8 wrap-up — root `README.md` finalized with Docker + local-dev + ruff + Robot sections; `.gitignore` extended to cover `node_modules/`, `.venv/`, and Robot run artifacts (`output.xml`, `log.html`, `report.html`).

---

## Step 1 status: COMPLETE (pending live run)

All planned phases done and statically verified:

| Phase | Verification | Status |
|------|-------------|-------|
| 1 Scaffolding | `uv sync`, `ruff check` clean | ✓ |
| 2 Models + migrations | `alembic history` parses; models import | ✓ |
| 3 API | App imports; all routes registered | ✓ |
| 4 Frontend | `npm run build` clean (TS strict) | ✓ |
| 5 Docker | `docker compose config` parses | ✓ |
| 6 Robot tests | `robot --dryrun tests/` → 23/23 pass | ✓ |
| 7 Ruff | `uv run ruff check .` clean | ✓ |
| 8 README + gitignore | both updated | ✓ |

Remaining (optional but strongest validation): `docker compose up --build` to confirm the live stack actually serves and Robot tests pass against it end-to-end.

### Live end-to-end verification — 2026-05-20

- `docker compose up --build -d` brought up all four services; Postgres + Redis became healthy, backend + frontend started.
- `curl http://localhost:8000/health` → `{"status":"ok"}`.
- `curl http://localhost:5173/` → 200 OK with `<title>ReqEngine</title>`.
- `curl http://localhost:8000/api/testcases` → 3 seeded testcases with project_ids `Project1_00000001`, `Project1_00000002`, `Project1_00000003` (confirms the shared per-project counter is feeding the seed correctly).
- `robot tests/` against the live stack → **23 tests, 23 passed, 0 failed**. Results in `tests/robot_results/`.

**Step 1 is complete and live-verified.**

---

### Implementer report (backend, 2026-05-20)

**Files created** (all under `/home/bov/python/ReqEngine/`):

- `backend/pyproject.toml` — uv project with pinned deps; ruff config; tests dep-group
- `backend/uv.lock` — generated lockfile
- `backend/README.md` — short dev quickstart
- `backend/Dockerfile` — placeholder for Phase 5
- `backend/alembic.ini` — Alembic config pointing to asyncpg URL
- `backend/alembic/env.py` — async Alembic env
- `backend/alembic/versions/0001_initial.py` — creates all 4 tables with indexes and CHECK constraint
- `backend/app/__init__.py`, `app/main.py`, `app/config.py`, `app/db.py`, `app/deps.py`, `app/sanitize.py`
- `backend/app/models/__init__.py`, `requirement.py`, `link.py`, `testcase.py`, `project_counter.py`
- `backend/app/schemas/__init__.py`, `requirement.py`, `link.py`, `testcase.py`
- `backend/app/routers/__init__.py`, `requirements.py`, `links.py`, `testcases.py`
- `backend/app/services/__init__.py`, `counter.py`, `seed.py`
- `.env.example` — updated (MySQL block removed; Postgres + Redis vars added)

**Deviations / notes:**
- Enums use `StrEnum` (Python 3.11+) per ruff UP042; Pydantic v2 accepts StrEnum fine.
- `ruff` added to `[dependency-groups] dev` (uv 0.11 deprecated `tool.uv.dev-dependencies`).
- The `VIRTUAL_ENV` warning in output is an unrelated pre-existing venv in the repo root; it does not affect `backend/.venv`.
- `alembic check` fails (no Postgres), but `alembic history` parses correctly.

**Skipped / left for Opus review:**
- No tests written (Phase 6).
- No docker-compose (Phase 5).
- Frontend untouched (Phase 4).
- `alembic upgrade head` requires a live Postgres; migration syntax is valid.

**Verification commands:**
```bash
cd backend
uv sync
uv run ruff check .
uv run python -c "from app.main import app"
uv run alembic history
# With Postgres available:
DATABASE_URL=postgresql+asyncpg://user:pw@localhost:5432/reqengine uv run alembic upgrade head
```

---

### Implementer report (frontend, 2026-05-20)

**Files created** (all under `/home/bov/python/ReqEngine/frontend/`):

- `package.json`, `package-lock.json` — npm project manifest
- `vite.config.ts` — Vite config with React plugin, dev server on port 5173
- `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json` — TypeScript strict mode
- `index.html` — Vite entry HTML
- `.env.example` — `VITE_API_BASE_URL=http://localhost:8000/api`
- `README.md` — short dev/build quickstart
- `src/vite-env.d.ts` — Vite client type reference for `import.meta.env`
- `src/main.tsx` — React root with BrowserRouter
- `src/App.tsx` — route definitions (`/`, `/requirements/new`, `/requirements/:id`)
- `src/api/types.ts` — TS interfaces and union types mirroring all backend schemas
- `src/api/client.ts` — typed fetch wrapper with a method per API endpoint
- `src/hooks/useDirtyForm.ts` — isDirty tracking + beforeunload handler
- `src/styles/global.css` — single global stylesheet (no CSS framework)
- `src/pages/RequirementList.tsx` — list view with delete-per-row and New button
- `src/pages/RequirementEdit.tsx` — create+edit form (handles both /new and /:id)
- `src/components/LinksBox.tsx` — scrollable links table with delete and Create Link button
- `src/components/CreateLinkDialog.tsx` — modal form for POST /api/links

**Versions chosen** (downgraded from latest to support Node 18.19 on the host):
- `vite` 5.4.21 (latest v5; v8 requires Node >=20)
- `react` / `react-dom` 18.3.1
- `react-router-dom` 6.30.3 (v7 requires Node >=20)
- `@vitejs/plugin-react` 4.7.0
- `typescript` 5.9.3

**Deviations from brief:**
- Downgraded Vite/React Router from latest to Node-18-compatible versions (see above).
- Added `tsconfig.app.json` (Vite's standard split-tsconfig pattern) alongside `tsconfig.node.json`; the brief only mentioned `tsconfig.node.json` but both are required for `tsc -b`.

**Verification commands:**
```bash
cd frontend
npm install
npm run build       # must exit 0
npm run dev         # dev server starts on http://localhost:5173
```

---

### Implementer report (docker, 2026-05-20)

**Files created:**
- `docker/Dockerfile.backend` — uv-based image; entrypoint baked inline via RUN printf (build context is `./backend`, so `../docker/` is inaccessible via COPY)
- `docker/backend-entrypoint.sh` — standalone copy of the entrypoint for reference/documentation
- `docker/Dockerfile.frontend` — node:20-alpine, `npm ci`, Vite dev server on 0.0.0.0:5173
- `docker-compose.yml` — version-less Compose v2; postgres:16-alpine + redis:7-alpine + backend + frontend
- `README.md` — Run it / Local dev without Docker / Ruff sections

**Files modified:**
- `frontend/vite.config.ts` — added `strictPort: true`, `watch: { usePolling: true }`, explicit `host: '0.0.0.0'`
- `.env.example` — replaced with local-dev-only Postgres+Redis defaults (no MySQL, no POSTGRES_* vars)
- `.dockerignore` — added `node_modules`, `dist`, `.venv`, `*.log`

**Deviations:**
- Entrypoint script cannot be COPYed from `../docker/` (outside build context); baked into Dockerfile inline. `docker/backend-entrypoint.sh` exists as the canonical readable reference.
- `docker compose config` ran successfully and validated all paths and syntax.

**Run instructions:**
```
git clone <repo-url> ReqEngine && cd ReqEngine
docker compose up --build
# Frontend: http://localhost:5173
# Backend docs: http://localhost:8000/docs
```

---

### Implementer report (tests, 2026-05-20)

**Suites created** (all under `/home/bov/python/ReqEngine/tests/`):

- `__resources/variables.resource` — `${API_BASE_URL}` variable (env-overridable)
- `__resources/api.resource` — session setup + 8 reusable keywords (Reserve New ID, Create/Get/List/Update/Delete Requirement, Create/Delete Link)
- `01_requirements_crud.robot` — 6 tests: reserve, create, get, list, update, delete + 404 check
- `02_links.robot` — 7 tests: create link, both-side GET, self-link 422, 404 for missing req, delete link, cascade on req delete
- `03_id_allocation.robot` — 3 tests: uniqueness, strict monotonic increase, format regex
- `04_sanitization.robot` — 3 tests: script tag stripped to plain text, 201-char title → 422, img onerror stripped
- `05_testcases.robot` — 4 tests: ≥3 entries, valid project_id format, seed titles present, required fields
- `README.md` — install + run instructions (local and docker compose)

**Dry-run result:** `robot --dryrun tests/` → **23 tests, 23 passed, 0 failed**, 0 warnings (RF 7.4.2).

**Deviations:**
- `To Json` keyword is deprecated in RF7/robotframework-requests 0.9.7; replaced with `${resp.json()}` throughout.
- Added explicit `Library Collections` to suites 03 and 05 (dry-run did not resolve Collections keywords through the resource-level import alone).
- `Create Link` returns `resp.json()` even for non-201 statuses; callers that expect error responses still get the error body dict.
