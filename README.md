# Bidworx

Evidence-backed bid intelligence for teams that cannot afford unsupported claims.

Bidworx is a deterministic procurement intelligence platform. It analyses tender material, buyer requirements, compliance risk, scoring signals, and evidence gaps using structured data rather than open-ended generation.

## Architecture

- FastAPI backend
- Pydantic request/response models
- Structured JSON knowledge records
- Deterministic classifier
- Deterministic retriever
- Deterministic answer builder
- Streaming response UX
- Evidence/source chips
- Scoped refusal behaviour for unsupported claims

## Apps

- `apps/api` - FastAPI procurement intelligence API
- `apps/web` - Next.js operational SaaS interface

## Local Development

Install workspace dependencies:

```bash
pnpm install
```

Run the API locally:

```bash
cd apps/api
..\\..\\.venv\\Scripts\\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Run the web app locally:

```bash
pnpm --dir apps/web run dev -- --hostname 127.0.0.1 --port 3100
```

Open `http://127.0.0.1:3100/chat`.

## Test And Build

```bash
pnpm run lint
pnpm run test
pnpm run build
```

## Deployment

- Deploy `apps/web` to Vercel.
- Deploy `apps/api` to Railway.
- Set `API_BASE_URL` in Vercel to the Railway service URL without `/api`.
- Set `CORS_ORIGINS` and `CORS_ORIGIN_REGEX` in Railway for local, Vercel preview, and production web origins.
- The API exposes `GET /api/health` and validates required data files on startup.

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for the full first deployment checklist.
