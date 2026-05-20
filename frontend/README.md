# ReqEngine Frontend

React + Vite + TypeScript frontend for the ReqEngine requirements management tool.

## Development

```bash
cp .env.example .env
npm install
npm run dev        # starts Vite dev server on http://localhost:5173
```

## Build

```bash
npm run build      # type-checks and bundles into dist/
npm run preview    # preview the production build locally
```

## Environment

| Variable            | Default                        | Description              |
|---------------------|--------------------------------|--------------------------|
| `VITE_API_BASE_URL` | `http://localhost:8000/api`    | Backend API base URL     |
