# davidrobertson.pro API

FastAPI backend for the recruiter-facing profile assistant.

## Features

- **Streaming chat endpoint** — deterministic, templated answers from structured CV data
- **Intent classification** — keyword-based routing to appropriate data sources
- **Profile API** — structured profile data endpoint
- **Suggestions API** — suggested prompts for recruiters
- **Health check** — service status endpoint

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app
```

## API Endpoints

- `GET /api/health` — health check
- `GET /api/profile` — profile summary
- `GET /api/suggestions` — suggested prompts
- `POST /api/chat/stream` — streaming chat (SSE)

## Architecture

- **`app/main.py`** — FastAPI app, CORS, route registration
- **`app/core/`** — config, logging
- **`app/api/routes/`** — route handlers
- **`app/services/`** — business logic (classifier, retriever, answer builder, streaming)
- **`app/models/`** — Pydantic models
- **`app/data/`** — structured JSON knowledge base
- **`app/tests/`** — pytest test suite

## Data Sources

All answers are generated from structured JSON files in `app/data/`:

- `profile.json` — name, headline, positioning, strengths, preferred roles
- `skills.json` — technical skills, working style
- `projects.json` — featured builds and products
- `experience.json` — current positioning, capabilities, domains
- `achievements.json` — key accomplishments
- `faqs.json` — common recruiter questions
- `job_titles.json` — relevant role titles

## Design Principles

- **Truth over fluency** — all answers sourced from approved data
- **Deterministic** — no LLM dependency in MVP
- **Scoped** — strict refusal for out-of-scope questions
- **Fast** — keyword classification, template-based answers
- **Production-minded** — typed models, structured logging, testable
