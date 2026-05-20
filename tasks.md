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

---

# Step 2 — Project view + Document view (multi-project)

Adds: `Project` table, `Document` table, full multi-project routing, TipTap-based document editor with 8 heading levels and inline requirement nodes.

## Phase 0 (Step 2) — Decisions — RESOLVED 2026-05-20

- D1 **Editor library:** TipTap (`@tiptap/react` + `@tiptap/starter-kit`, plus a custom Heading extension extended to levels 1–8 and a custom Requirement node).
- D2 **Project scope:** Full multi-project. Project table is real, FK-linked from Requirement/Testcase/Link/Document. Start route becomes the Project view.
- D3 **Inline requirement (+ button in document):** Creates a real Requirement row via `POST /api/requirements` using a reserve-id call. The document JSON stores a `requirement-ref` node `{ requirement_id, project_id }`. Title and Description fields inside the boxed UI edit the actual Requirement via `PUT /api/requirements/{id}`.
- D4 **Chapter numbering:** Auto-computed at render time by walking heading nodes in document order. Numbers are NOT stored in the JSON. Editing/inserting/deleting a heading reflows all downstream numbers.
- D5 **Start route:** `/` is the Project view (project list). No separate "Document view" link from the main page — documents are reached only through a project.
- D6 **Existing data migration:** Wipe and reseed. Drop existing Requirement/Testcase/Link tables; recreate with `project_id_number` FK NOT NULL. Reseed 2 projects (Project1, Project2), each with its own ProjectCounter row and 3 lorem-ipsum testcases.
- D7 **`Project.document_ids`:** Derived (computed from `Document` query by `project_id_number`), not stored — same pattern as Step 1's `list_of_links`. Spec line "self growing list of int" is satisfied by the derived list.
- D8 **`Project.user_ids`:** Stored as a JSON column (Postgres `JSONB`), default `[10, 20]`.
- D9 **DIN A4 page:** Rendered as a fixed-width white surface (210mm equivalent, ~794px at 96dpi) on a light gray background, with shadow. Vertical extent grows with content.
- D10 **Save semantics:** Document save is explicit (Save button in the toolbar). The Requirement rows inside the document persist independently the moment they are added/edited (so the document JSON ref is never dangling).

## Phase 1 (Step 2) — Backend models & migration

1. New SQLAlchemy model `Project`:
   - `id` int PK
   - `project_name` String(120) UNIQUE NOT NULL
   - `user_ids` JSONB, default `[10, 20]`
   - `created_on` timestamp
   - (No stored `document_ids` — derive via relationship/query)
2. New SQLAlchemy model `Document`:
   - `id` int PK
   - `project_id` String(100) UNIQUE — uses the existing shared per-project counter via `format_project_id(project_name, n)` + `reserve_project_number`
   - `project_id_number` int FK → `project.id` NOT NULL, indexed
   - `created_on` timestamp
   - `last_edit_on` timestamp
   - `author` String(100) — `User1` for step
   - `last_change_by` String(100)
   - `document_content` JSONB — the TipTap doc JSON
3. Add `project_id_number` FK column to `Requirement`, `Testcase`, `Link` (NOT NULL, indexed).
4. New Alembic migration `0002_multi_project.py`:
   - Drop `requirement`, `testcase`, `link`, `project_counter` tables (wipe + reseed per D6).
   - Create `project` table.
   - Recreate `project_counter` (key `project_name`).
   - Recreate `requirement`, `testcase`, `link` with `project_id_number` FK column NOT NULL.
   - Create `document` table.
5. Update seed (`app/services/seed.py`) to be idempotent:
   - Insert `Project(id=1, project_name='Project1')`, `Project(id=2, project_name='Project2')`.
   - Insert `ProjectCounter('Project1', 1)` and `ProjectCounter('Project2', 1)`.
   - Insert 3 lorem testcases per project, each drawing its project_id from its project's counter.

## Phase 2 (Step 2) — Backend API

New routes:
- `GET /api/projects` → list `[{id, project_name, user_ids, document_count}]`.
- `POST /api/projects` → create `{project_name}`; auto-creates a `ProjectCounter(project_name, 1)`.
- `GET /api/projects/{id}` → detail incl. derived `document_ids` and `user_ids`.
- `GET /api/projects/{id}/documents` → list documents `[{id, project_id, author, last_edit_on}]`.
- `POST /api/documents` body `{project_id_number}` → creates a blank document with empty content `{type:'doc', content:[]}`, allocates a `project_id` from the project's counter, sets `author='User1'`, returns full document.
- `GET /api/documents/{id}` → full document including `document_content`.
- `PUT /api/documents/{id}` body `{document_content}` → save; updates `last_change_by`, `last_edit_on`.
- `DELETE /api/documents/{id}` → delete.

Updated routes:
- `POST /api/requirements/reserve-id` now accepts `?project_name=` (defaults `Project1`).
- `POST /api/requirements` requires `project_id_number` in body.
- `POST /api/links` requires `project_id_number` in body (validates both endpoints belong to that project).
- `GET /api/requirements` and `GET /api/testcases` accept optional `?project_id_number=` filter.

Sanitization helper unchanged (already strips HTML to plain text). For document_content JSON: validate it is a dict with `type:'doc'`; recursively sanitize all text node values via the same `bleach` helper; reject any node `type` not in the allowlist `[doc, paragraph, heading, requirement-ref, text]`.

## Phase 3 (Step 2) — Frontend routing + Project view

1. Install `@tiptap/react`, `@tiptap/starter-kit`, `@tiptap/pm` (pin versions compatible with React 18 / Vite 5 / Node 18).
2. New route table:
   - `/` → `ProjectListPage` (replaces current RequirementList as home)
   - `/projects/:projectId` → `ProjectDetailPage` (documents list + "Requirements" sub-link)
   - `/projects/:projectId/documents/new` → `DocumentEditorPage` (creates blank doc on mount)
   - `/documents/:documentId` → `DocumentEditorPage` (loads existing)
   - `/projects/:projectId/requirements` → `RequirementListPage` (project-scoped list with "New Requirement" button)
   - `/requirements/:id` → `RequirementEdit` (existing, unchanged UI; project_id_number derived from loaded requirement)
   - `/projects/:projectId/requirements/new` → `RequirementEdit` (new form, passes project_id_number to reserve-id + create)
3. `ProjectListPage`:
   - Top button bar with "Create New Project" button (modal for project_name).
   - Table of projects (id, project_name, document_count) — each row clickable to detail.
4. `ProjectDetailPage`:
   - Top button bar with "Create New Document" button.
   - Two sub-tabs/sections: Documents (table) and Requirements (link to `/projects/:projectId/requirements`).
5. API client (`src/api/client.ts`) extended with `listProjects`, `createProject`, `getProject`, `listProjectDocuments`, `createDocument`, `getDocument`, `updateDocument`, `deleteDocument`, plus project-filter params on existing list endpoints.

## Phase 4 (Step 2) — Frontend document editor (TipTap)

1. `DocumentEditorPage`:
   - DIN A4 page surface (`.document-page` CSS class, ~794px wide white box, shadow, light-gray surrounding background, grows vertically).
   - Top toolbar: style dropdown (`Standard`, `Heading 1`..`Heading 8`), font family dropdown (Arial default), font-size dropdown (default 10), bold/italic/underline buttons, `+ Add Requirement` button with type dropdown (the 4 requirement_types), Save button.
2. Custom TipTap extensions:
   - `HeadingExt` — copies starter-kit `Heading` config but extends `levels: [1,2,3,4,5,6,7,8]`.
   - `RequirementRef` — atomic block node with attrs `{ requirement_id, project_id }`. Renders the black-framed box with project_name label, Title input (single line, debounced PUT), Description textarea (multi-line, debounced PUT), and a small "type" badge. NodeView in React.
3. Chapter numbering: a TipTap decoration plugin that scans the document on every transaction, computes the `X.Y.Z` prefix per heading (per D4 rules), and renders it as a non-editable prefix span. Pseudocode:
   - Maintain `counters = [0,0,0,0,0,0,0,0]`.
   - For each heading in doc order at level L (1-indexed):
     - Increment `counters[L-1]`.
     - Zero out `counters[L..7]`.
     - Number string = join non-zero counters with `.` (up to and including L).
   - Render prefix before heading text content.
4. Default styling (in `global.css`):
   - `.document-page p` → Arial, 10pt, black.
   - `.document-page h1..h8` → dark gray (`#555`), bold; sizes scale roughly from 24pt down to 10pt.
5. Add Requirement flow:
   - On `+ Add Requirement` (type chosen from dropdown), call `POST /api/requirements/reserve-id?project_name=...` then `POST /api/requirements` with default title="", description="", chosen type, status="draft", revision="0.1", author="User1", project_id_number=this project. Insert a `RequirementRef` node at cursor referencing the new id.
   - Editing title/description in the box triggers a debounced (500ms) `PUT /api/requirements/{id}`.
   - On `Save` button: `PUT /api/documents/{id}` with the full JSON.
6. Hyperlink semantics inside the document: clicking a `RequirementRef` box header navigates to `/requirements/:id` (with dirty-check confirm dialog if document has unsaved changes).

## Phase 5 (Step 2) — Robot tests

1. New suite `06_projects.robot` — create/list/detail/delete; uniqueness of project_name.
2. New suite `07_documents.robot` — create blank doc, save content, reload roundtrip, delete cascades.
3. New suite `08_document_inline_requirement.robot` — flow that reserves id, creates a Requirement, embeds ref in document_content, saves, reloads, ref still points at the right requirement.
4. New suite `09_chapter_numbering.robot` — pure unit-style: POST a document JSON with mixed heading levels, GET it back, run a Python keyword that re-derives numbers and asserts the expected `X.Y.Z` sequence.
5. Update existing suites 01–05 to pass `project_id_number` where required by the new request bodies; update `03_id_allocation` to assert per-project independence (Project1 and Project2 increment independently).
6. Refresh `__resources/api.resource` with `Create Project`, `Create Document`, `Update Document`, etc.

## Phase 6 (Step 2) — Wrap-up

1. Update root `README.md` with the new routes and the multi-project model.
2. Update `.env.example` if any new env vars needed (none expected).
3. Run `uv run ruff check .`, `npm run build`, `docker compose up --build`, `robot tests/`.
4. Opus final review.

---

## Progress log (Step 2)

- 2026-05-20: Step 2 tasks.md drafted. Decisions D1–D10 resolved. Spawning Sonnet 4.6 implementer for Phase 1 (models + migration + seed) + Phase 2 (API routes). Frontend (Phases 3–4) and tests (Phase 5) deferred to follow-up implementer spawns after review.
- 2026-05-20: Phases 1–2 (Step 2) implemented by Sonnet 4.6. Migration is `0003_multi_project.py` chaining onto a pre-existing `0002_polymorphic_links.py` (a Step 1 follow-on not previously logged — links can now point at either requirements or testcases). Backend verified: ruff clean, app imports, `alembic history` parses (chain 0001→0002→0003), all 8 new routes (`/api/projects` × 4, `/api/documents` × 4) registered alongside the updated requirement/link/testcase routes which now require `project_id_number`. Sanitizer wired via Pydantic `field_validator`. `documents` and `projects` table names plural-consistent with raw SQL in `create_project`. Spawning Sonnet 4.6 implementer for Phases 3–4 (frontend).
- 2026-05-20: Phases 3–4 (Step 2 frontend) implemented by Sonnet 4.6. TipTap 3.23.5 pinned (compatible with React 18.3 / Vite 5.4 / Node 18.19). New routes: `/` → ProjectListPage (new home), `/projects/:id` → ProjectDetailPage, `/documents/:id` → DocumentEditorPage with DIN A4 surface + toolbar (Standard / Heading 1–8 / font / size / B / I / U / + Requirement / Save), custom HeadingExt extends levels to 1–8 (h7/h8 render as `<div class="heading-N">`), ChapterNumbering implemented as a TipTap Extension wrapping a ProseMirror plugin (widget decorations, non-stored), RequirementRef atomic node + NodeView with debounced PUT on title/description edits. `npm run build` exits 0; TS strict; one expected 581KB bundle-size warning (TipTap). Spawning Sonnet 4.6 implementer for Phase 5 (Robot tests).
- 2026-05-20: Phase 5 (Step 2 Robot tests) implemented by Sonnet 4.6. 4 new suites (06_projects, 07_documents, 08_document_inline_requirement, 09_chapter_numbering) + updates to 01–05 to pass `project_id_number`. New Python library `tests/lib/chapter_numbering.py` reimplements the chapter-numbering algorithm to data-test it independently from the frontend. `uv --project backend run robot --dryrun tests/` → **45 tests, 45 passed, 0 failed** (was 23 after Step 1).

---

## Step 2 status: COMPLETE (static verification only — live run pending)

| Phase | Verification | Status |
|------|-------------|-------|
| 1 Models + migration | `alembic history` parses chain 0001→0002→0003 | ✓ |
| 2 API | App imports; 8 new routes registered | ✓ |
| 3–4 Frontend | `npm run build` exits 0; TS strict | ✓ |
| 5 Robot tests | `robot --dryrun tests/` → 45/45 | ✓ |
| Ruff | clean | ✓ |

**Recommended next:** `docker compose up --build` to run `alembic upgrade head` (apply 0003) against live Postgres, then `uv --project backend run robot tests/` end-to-end. This mirrors Step 1's "Live end-to-end verification" pass.

### Live end-to-end fixes — 2026-05-20

Two issues surfaced after the user ran `docker compose up --build`:

1. **Frontend stale node_modules.** Vite errored: `Failed to resolve import "@tiptap/react"`. Root cause: `docker-compose.yml` declared a named volume `frontend_node_modules:/app/node_modules` to defend against host shadowing, but no host bind-mount of `./frontend` exists to defend against. The named volume persisted across `docker compose up --build` and shadowed the freshly built image layer (which DID contain the new TipTap packages via `npm ci`). Fix: removed the named volume + its `volumes:` declaration from `docker-compose.yml`. Now `/app/node_modules` from the image is used directly. Users updating the project must run `docker compose down && docker compose up --build` once to drop the old container that mounts the stale volume.

2. **Robot URL parsing.** 22 of 23 failures shared `TypeError: ...missing 1 required positional argument: 'url'` with the warning `You might have an = symbol in url. You better place 'url=' before`. RF interprets `?param=value` in a URL string as a kwarg. Fix: added `url=` prefix to the three call sites with query strings (`/requirements/reserve-id?project_name=`, `/requirements?project_id_number=`, `/testcases?project_id_number=`).

3. **One residual test failure.** `Project Name HTML Is Sanitized` in `06_projects.robot` used a fixed name `<b>SanitizedProj</b>` and 409'd on the second run because there is no DELETE for projects. Fix: appended a uuid suffix so repeated runs don't collide.

After all three fixes:
- `docker compose ps` → all 4 services up; postgres + redis healthy.
- Vite serves `main.tsx` and `DocumentEditorPage.tsx` with HTTP 200 and zero pre-transform errors in frontend logs.
- `uv --project backend run robot tests/` → **45 tests, 45 passed, 0 failed** (live).
