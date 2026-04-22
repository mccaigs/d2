# MVP Tasks

## Phase 1 - Foundations

### 1. Repository setup
- Initialise monorepo structure
- Create `apps/web`
- Create `apps/api`
- Add root README
- Add `docs/`
- Add workspace config
- Add formatting and linting config

### 2. Web app setup
- Scaffold Next.js 16.2 app
- Install Tailwind
- Install shadcn/ui
- Add typography setup
- Create global layout
- Create base route structure

### 3. API setup
- Scaffold FastAPI app
- Add Pydantic models
- Add route modules
- Add service layer structure
- Add local config management
- Add test setup

## Phase 2 - Knowledge layer

### 4. Structure profile data
- Create `profile.json`
- Create `skills.json`
- Create `projects.json`
- Create `experience.json`
- Create `achievements.json`
- Create `faqs.json`
- Create `job_titles.json`

### 5. Define schema
- Define typed data models for all JSON records
- Validate knowledge files at app startup
- Add fallback error handling for malformed data

## Phase 3 - Deterministic chat engine

### 6. Intent classifier
- Define supported intents
- Build keyword map
- Add fuzzy matching support
- Allow multi-intent questions
- Add confidence score

### 7. Retriever
- Match user query against structured data
- Rank results by intent relevance
- Support top-k retrieval
- Return source metadata for UI chips

### 8. Answer builder
- Build response templates by intent
- Create scoped refusal template
- Create low-confidence template
- Create follow-up prompt generator
- Ensure answer formatting remains deterministic

### 9. Streaming layer
- Implement chat stream endpoint
- Stream answer chunk-by-chunk
- Add final metadata event for sources and follow-ups
- Handle cancelled requests cleanly

## Phase 4 - Frontend chat UX

### 10. Chat page shell
- Build empty state layout
- Add header and back link
- Add recruiter intro copy
- Add prompt cards
- Add sticky input

### 11. Chat interaction
- Post messages to API
- Read stream response
- Render progressive assistant output
- Render user messages
- Handle loading and error states

### 12. Message components
- Build assistant message component
- Build user message component
- Build source chips
- Build follow-up card row
- Build typing indicator

## Phase 5 - Marketing/profile pages

### 13. Homepage
- Build hero section
- Add key strengths section
- Add featured projects
- Add CTA into chat
- Add contact section

### 14. Supporting pages
- Build profile page
- Build projects page
- Build contact page

## Phase 6 - QA and hardening

### 15. Backend tests
- Classifier tests
- Retriever tests
- Answer builder tests
- Chat endpoint tests
- Scope refusal tests

### 16. Frontend QA
- Mobile responsiveness
- Empty state review
- Chat streaming review
- Accessibility pass
- Copy consistency pass

### 17. Deployment
- Deploy web app
- Deploy API
- Configure environment variables
- Point domain and subpaths
- Add health check monitoring

## Phase 7 - v1.1 follow-on
- Add job description paste mode
- Add deterministic fit analyser
- Add evidence-backed fit scoring
- Add recruiter conversion CTAs
- Add analytics