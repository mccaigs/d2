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

## Local Commands

```bash
pnpm install
pnpm test
pnpm build
```
