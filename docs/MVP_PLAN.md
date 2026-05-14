# Bidworx MVP Plan

## Version
v0.1

## Goal
Build the first usable Bidworx MVP around pasted tender text.

The MVP should let a user paste tender content, receive deterministic extraction, see an opportunity summary, review compliance risks, and inspect evidence/source chips. Responses must stream progressively and refuse unsupported requests within scope.

## Scope

### In Scope
- Paste tender text
- Deterministic extraction
- Opportunity summary
- Compliance risk list
- Evidence/source chips
- Scoped refusal
- Streaming response

### Out Of Scope
- File upload
- OCR
- Auth
- Workspace storage
- Multi-user review
- LLM rewriting
- Bid response drafting
- CRM/procurement integrations
- Admin evidence CRUD

## User Journey

1. User opens `/chat`.
2. User chooses "Analyse this tender opportunity" or pastes tender text into the bid readiness panel.
3. Bidworx sends the pasted tender text to the FastAPI backend.
4. Backend normalises the text and runs deterministic extraction.
5. Backend returns streamed output:
   - opportunity summary
   - buyer requirements
   - compliance risks
   - missing evidence
   - confidence notes
   - source/evidence chips
6. User can ask follow-up questions such as:
   - "What are the likely compliance risks?"
   - "What evidence do we need to support this claim?"
   - "Identify missing submission requirements"
7. If the user asks for unsupported claims, Bidworx refuses and explains what evidence is missing.

## Routes

### Web Routes
- `GET /`
  - Bidworx product homepage.
- `GET /chat`
  - Main Ask Bidworx interface.
- `GET /profile`
  - Platform overview, kept as compatibility route for now.
- `GET /projects`
  - Workflow overview, kept as compatibility route for now.

### API Routes
- `GET /api/health`
  - Health check.
- `GET /api/suggestions`
  - Tender prompt cards.
- `GET /api/profile`
  - Product summary, kept as compatibility route for now.
- `POST /api/chat/stream`
  - Streaming deterministic chat response.
- `POST /api/fit/analyse`
  - Bid readiness scoring, kept as compatibility route for now.

## Data Models

### Existing Compatibility Models
- `ChatRequest`
  - `message: str`
- `ChatMetadata`
  - `sources: list[SourceChip]`
  - `follow_ups: list[str]`
  - `intent: str`
  - `cta`
  - `show_contact_form`
  - `contact_reason`
- `SourceChip`
  - `label: str`
  - `category: str`
- `FitRequest`
  - `job_description: str`
  - v0.1 uses this field for tender text until the route is renamed.
- `FitResponse`
  - Reused for bid readiness output until compatibility naming is removed.

### v0.1 Target Domain Models
Add or evolve towards these names without breaking existing routes:

```python
class TenderAnalysisRequest(BaseModel):
    tender_text: str


class ExtractedRequirement(BaseModel):
    id: str
    text: str
    requirement_type: str  # mandatory | scored | informational | submission
    confidence: str        # high | medium | low


class ComplianceRisk(BaseModel):
    area: str
    note: str
    severity: str          # blocker | risk | review
    evidence_needed: list[str]


class EvidenceChip(BaseModel):
    label: str
    category: str


class OpportunitySummary(BaseModel):
    buyer: str | None
    opportunity_type: str | None
    summary: str
    requirements: list[ExtractedRequirement]
    compliance_risks: list[ComplianceRisk]
    evidence_chips: list[EvidenceChip]
```

## Structured Data

v0.1 should use the existing structured records first:

- `product.json`
- `capabilities.json`
- `workflows.json`
- `procurement_examples.json`
- `buyer_roles.json`
- `proof_points.json`
- `faqs.json`
- `compliance_rules.json`
- `scoring_rules.json`
- `evidence_categories.json`
- `tenders.json`
- `frameworks.json`

No generated answer should claim evidence that is not supported by these files or by the tender text supplied by the user.

## Backend Services

### `classifier.py`
Responsibilities:
- Classify user intent into procurement categories:
  - tender analysis
  - buyer requirements
  - compliance risk
  - evidence mapping
  - bid readiness scoring
  - unsupported/out-of-scope

### `question_intent.py`
Responsibilities:
- Classify question shape:
  - overview
  - capability
  - yes/no readiness
  - risk/compliance
  - working style/process

### `tender_extractor.py`
New v0.1 service.

Responsibilities:
- Normalise pasted tender text.
- Extract:
  - buyer or contracting authority where visible
  - opportunity type
  - mandatory requirements
  - scored requirements
  - submission requirements
  - compliance signals
  - evidence asks
- Use deterministic regex, keyword maps, and phrase rules.

### `compliance_checker.py`
New v0.1 service.

Responsibilities:
- Compare extracted text against `compliance_rules.json`.
- Produce risk list:
  - missing mandatory documents
  - pass/fail criteria
  - unsupported claims
  - unclear submission instructions
  - certification or policy evidence needs

### `retriever.py`
Responsibilities:
- Retrieve relevant structured data records.
- Return source chips for:
  - capabilities
  - workflows
  - compliance rules
  - scoring rules
  - proof points
  - evidence categories

### `fit_analyser.py`
Current compatibility service.

v0.1 responsibilities:
- Score bid readiness from pasted tender text.
- Keep existing response shape until the route/model is renamed.
- Output:
  - score
  - label
  - readiness summary
  - risks
  - relevant workflows
  - next checks

### `answer_builder.py`
Responsibilities:
- Build deterministic streamed answers.
- Never invent missing proof.
- Include concise opportunity summary and risk list.
- Add scoped refusal when a user asks for unsupported bid claims.

### `stream_writer.py`
Responsibilities:
- Preserve streaming SSE behaviour.
- Emit final metadata event with sources and follow-ups.

## Frontend Components

### Existing Components
- `ChatShell`
  - Main Ask Bidworx interface.
- `ChatInput`
  - User text input.
- `SuggestionCards`
  - v0.1 tender prompts.
- `ChatMessage`
  - Streams assistant output.
- `SourceChips`
  - Evidence/source chip display.
- `FitAnalysisPanel`
  - Compatibility component for pasted tender readiness scoring.

### v0.1 Component Responsibilities

#### `ChatShell`
- Show "Ask Bidworx".
- Present v0.1 prompts:
  - Analyse this tender opportunity
  - What are the likely compliance risks?
  - What evidence do we need to support this claim?
  - Summarise the buyer requirements
  - Score this opportunity
  - Identify missing submission requirements

#### `FitAnalysisPanel`
- Rename in UI only to bid readiness language.
- Accept pasted tender text.
- Show:
  - score
  - summary
  - compliance risks
  - evidence-positive signals
  - relevant workflows
  - next checks

#### `SourceChips`
- Display source categories clearly:
  - Capabilities
  - Workflows
  - Compliance Rules
  - Scoring Rules
  - Proof Points
  - Evidence Categories

## Tests

### Backend Unit Tests
- Classifier:
  - tender analysis prompt maps to readiness/scoring intent.
  - compliance question maps to compliance intent.
  - evidence question maps to evidence/capability intent.
- Tender extractor:
  - extracts mandatory requirements.
  - extracts submission requirements.
  - extracts evidence asks.
  - handles empty input.
- Compliance checker:
  - flags pass/fail requirements.
  - flags missing evidence.
  - flags certification/policy requirements.
- Retriever:
  - returns procurement source chips.
  - does not reference legacy data files.
- Answer builder:
  - builds opportunity summary from extracted facts.
  - refuses unsupported claims.
  - includes evidence/source context.
- Streaming:
  - emits chunks.
  - emits metadata.
  - emits done event.
- Bid readiness analyser:
  - scores tender text deterministically.
  - returns risks and relevant workflows.
  - handles empty input.

### Frontend Tests
- `/chat` renders Ask Bidworx.
- Prompt cards render v0.1 prompts.
- Pasted tender panel accepts text.
- Source chips render returned metadata.
- Empty/error states remain readable.

### Smoke Tests
- `GET /api/health`
- `GET /api/suggestions`
- `POST /api/chat/stream`
- `POST /api/fit/analyse`
- `pnpm run build`
- `pnpm run lint`
- `pnpm run test`

## Scoped Refusal Behaviour

Bidworx should refuse when:
- User asks it to invent evidence.
- User asks it to confirm certifications not present in structured data.
- User asks it to write unsupported bid claims.
- User asks outside procurement/bid intelligence scope.

Refusal should:
- Be brief.
- Explain the missing evidence.
- Suggest the structured data needed to answer.

Example:

```text
I cannot support that claim from the approved evidence currently available. Add a case study, certification record, policy, or delivery example that proves it, then I can map it into the tender response.
```

## Definition Of Done

v0.1 is done when:

- User can paste tender text.
- Backend extracts requirements deterministically.
- Backend returns an opportunity summary.
- Backend returns compliance risks.
- Backend returns evidence/source chips.
- Unsupported claims trigger scoped refusal.
- Responses stream progressively.
- `/chat` uses Bidworx tender prompts.
- Build, lint, and tests pass.
- No active user-facing copy refers to the legacy assistant.
- No LLM calls are introduced.
