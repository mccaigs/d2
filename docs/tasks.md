# MVP Tasks

## Phase 1 - Migration Foundations
- Audit repo structure
- Replace legacy assistant language with procurement/bid terminology
- Preserve deterministic architecture
- Update docs for Bidworx positioning

## Phase 2 - Procurement Knowledge Layer
- Replace `profile.json` with `product.json`
- Replace `skills.json` with `capabilities.json`
- Replace `projects.json` with `workflows.json`
- Replace `experience.json` with `procurement_examples.json`
- Replace `job_titles.json` with `buyer_roles.json`
- Replace `achievements.json` with `proof_points.json`
- Keep `faqs.json`
- Add placeholders:
  - `tenders.json`
  - `frameworks.json`
  - `compliance_rules.json`
  - `scoring_rules.json`
  - `evidence_categories.json`

## Phase 3 - Deterministic Engine
- Update intent classifier for tender, evidence, scoring, and compliance intents
- Update retriever to read procurement data
- Update answer builder to produce evidence-backed procurement responses
- Preserve source chips and scoped refusal behaviour
- Preserve streaming response endpoint

## Phase 4 - Frontend UX
- Update homepage sections for procurement intelligence
- Update chat page to "Ask Bidworx"
- Add tender prompt cards
- Update bid readiness analysis panel
- Apply dark operational SaaS design

## Phase 5 - QA
- Run backend tests
- Run frontend lint/build
- Identify broken tests from renamed domain concepts
- Add new Bidworx-specific tests
