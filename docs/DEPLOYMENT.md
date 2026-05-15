# Bidworx Deployment

Bidworx v0.1 deploys as two services:

- `apps/web` on Vercel
- `apps/api` on Railway

The MVP has no authentication, uploads, payments, dashboards, PDF parsing, or live LLM calls. The API answers from structured local data and deterministic rules.

## Required Environment Variables

### Web, Vercel

Set these in the Vercel project for Production and Preview:

```bash
NEXT_PUBLIC_SITE_URL=https://bidworx.example
API_BASE_URL=https://your-api.up.railway.app
GOOGLE_APPS_SCRIPT_URL=https://script.google.com/macros/s/REPLACE_WITH_YOUR_DEPLOYMENT_ID/exec
```

`NEXT_PUBLIC_API_BASE_URL` is optional. If unset, the web app calls `/api/...` and Next.js rewrites to `API_BASE_URL`. If set, use the Railway API URL including `/api`:

```bash
NEXT_PUBLIC_API_BASE_URL=https://your-api.up.railway.app/api
```

### API, Railway

Set these in the Railway service:

```bash
APP_NAME=Bidworx API
APP_VERSION=1.0.0
DEBUG=false
CORS_ORIGINS=https://bidworx.example,https://www.bidworx.example,http://localhost:3000,http://127.0.0.1:3000
CORS_ORIGIN_REGEX=^https://.*\.vercel\.app$
```

Railway supplies `PORT`. The local `HOST` and `PORT` values in `.env.example` are reference values only.

## CORS Policy

The API allows:

- Local development origins on `localhost` and `127.0.0.1`
- Vercel preview deployments matching `^https://.*\.vercel\.app$`
- Production placeholders `https://bidworx.example` and `https://www.bidworx.example`

Replace the placeholder production domains before launch.

## Local Development

Install dependencies:

```bash
pnpm install
```

Run the API:

```bash
cd apps/api
..\\..\\.venv\\Scripts\\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Run the web app:

```bash
pnpm --dir apps/web run dev -- --hostname 127.0.0.1 --port 3100
```

Open:

```bash
http://127.0.0.1:3100/chat
```

Health check:

```bash
http://127.0.0.1:8000/api/health
```

## Railway API Deployment

1. Create a Railway service from the repository.
2. Set the service root to `apps/api` if Railway does not detect it automatically.
3. Configure the environment variables above.
4. Start command, already captured in `apps/api/Procfile`:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. Confirm the health route:

```bash
https://your-api.up.railway.app/api/health
```

The API validates required JSON and sample tender files at startup. Missing or malformed data fails the service before it accepts traffic.

## Vercel Web Deployment

1. Create a Vercel project from the repository.
2. Set the project root directory to `apps/web`.
3. Set the environment variables above.
4. Use the default Next.js build command:

```bash
pnpm run build
```

5. Verify `/chat`, select a sample tender, and confirm streamed analysis output.

## Production Smoke Test Checklist

After deployment, verify the following:

- [ ] **Frontend Load**: The landing page loads without errors.
- [ ] **Health Check**: The backend health endpoint (`https://your-api.up.railway.app/api/health`) returns `{"status": "ok"}`.
- [ ] **API Connectivity**: The "Tender Analysis" or "Chat" features work (verifies frontend can call backend).
- [ ] **End-to-End Workflow**: The chat/analysis workflow completes successfully from prompt to response.
- [ ] **No Localhost**: Inspect the browser console; ensure no errors reference `localhost` or `127.0.0.1`.
- [ ] **CORS**: Verify no CORS errors appear in the console when using the application.
- [ ] **Streaming UX**: Ensure the chat response streams correctly (proves SSE/Streaming is functional).

## Verification Commands

Run these before deploying:

```bash
pnpm run lint
pnpm run test
pnpm run build
```
