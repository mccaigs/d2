# AGENTS.md

## Product Purpose

Bidworx is evidence-backed bid intelligence for teams that cannot afford unsupported claims.

The product helps procurement, bid, proposal, and capture teams analyse tender opportunities, buyer requirements, compliance risks, scoring signals, and evidence gaps before response drafting begins.

## Architecture Principles

Bidworx is deterministic-first. Preserve the existing architecture wherever possible:

- Structured JSON knowledge
- FastAPI backend
- Pydantic models
- Deterministic classifier
- Deterministic retriever
- Deterministic answer builder
- Deterministic bid readiness scoring
- Streaming response UX
- Evidence/source chips
- Scoped refusal behaviour

Use structured data before generated text. The system should retrieve, score, map, and explain from approved records before any prose is assembled.

## Evidence Rules

Do not create unsupported AI, procurement, bid, compliance, certification, policy, delivery, or sector claims.

Keep outputs evidence-backed. If the structured data does not support a claim, flag the evidence gap clearly or refuse within scope.

Never imply that Bidworx has live integrations, document parsing, certifications, customer proof, production deployments, or LLM capabilities unless those facts exist in the repo data or the user explicitly provides them.

## LLM Policy

Do not add LLM calls, model SDKs, prompt-generation layers, or AI rewriting services unless the user explicitly requests them.

If an LLM layer is requested later, it must be optional polish after deterministic retrieval, scoring, evidence mapping, and compliance checks. It must not become the source of truth.

## Language And Tone

Use British English throughout.

Do not use em dashes. Use commas, semicolons, colons, or parentheses instead.

Write in a precise, operational procurement tone. Avoid generic chatbot, legacy personal-site, or hype language.

## Implementation Guidance

Do not rewrite the app from scratch. Work with the existing monorepo shape and preserve established patterns.

Prefer small, reviewable changes. Keep edits scoped to the request.

When changing user-facing terminology, check both backend responses and frontend copy.

When changing procurement knowledge, update structured JSON first, then adapt deterministic services and UI copy.

## Verification

After changes, run the most relevant checks available:

```powershell
.\.venv\Scripts\python -m pytest apps\api\app\tests
cd apps\web
npm run build
```

Also run lint when the project lint configuration is working. If a lint/build/test command is broken because of project tooling, report the exact failure and do not hide it.

## Git Practice

Prefer small, reviewable commits.

Do not revert unrelated user changes. If the working tree is dirty, inspect carefully and only touch files needed for the task.
