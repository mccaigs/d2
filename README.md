# David's AI CV Assistant & Recruiter Evaluation System

A deterministic, recruiter-facing AI CV assistant and evaluation system.

## Overview
This product serves as an interactive, intelligent CV. Instead of a generic LLM chatbot that might hallucinate, it uses a deterministic intent-based engine to answer recruiter questions based *strictly* on structured data about David's experience, skills, and projects. 

It provides grounded answers, technical fit evaluations, and an editorial-style interface designed to quickly convey product, engineering, and architectural capability.

## Core Idea
- **Deterministic:** No live LLM generation for answers. Responses are mapped from structured data.
- **No Hallucinations:** Strict scope control. If it's not in the knowledge base, the assistant refuses to answer.
- **Recruiter Evaluation:** Built-in "Fit Analysis" provides a recruiter-grade evaluation of technical, applied AI, product/architecture, domain, and seniority fit.

## Tech Stack
### Frontend
- **Next.js 16.2** (React, TypeScript)
- **Tailwind CSS** & **shadcn/ui** for premium editorial design
- Streaming UI for assistant responses

### Backend
- **Python** & **FastAPI**
- **Pydantic** for strict data modeling
- Intent classification and structured JSON knowledge base retrieval

## How to Run Locally

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- pnpm

### Setup
1. Clone the repository.
2. Setup environment variables:
   - Copy `apps/api/.env.example` to `apps/api/.env`
   - Copy `apps/web/.env.example` to `apps/web/.env`

### Run Backend (FastAPI)
```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Run Frontend (Next.js)
```bash
cd apps/web
pnpm install
pnpm dev
```
Open `http://localhost:3000` in your browser.