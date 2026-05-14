# Bidworx v2 - Deterministic Rebuild Tasklist

## Product Goal
Rebuild Bidworx as a deterministic bid intelligence and evidence orchestration platform.

The system must not behave like a generic AI bid writer. It should inspect tender requirements, map them to approved organisational evidence, score coverage, identify risk, and only generate responses from verified source material.

Core positioning:

> Bidworx does not invent bid content. It proves what the organisation can safely claim, then assembles compliant responses from approved evidence.

---

## Phase 0 - Repo Setup

### Tasks
- [ ] Create a new `bidworx/` folder or branch from the existing `davidrobertson.pro` deterministic CV system.
- [ ] Preserve the working chat UI, streaming behaviour, deterministic retrieval pattern, and refusal logic.
- [ ] Rename CV/job language to bid/tender language.
- [ ] Add `/docs`, `/data`, `/core`, and `/reports` folders if not already present.
- [ ] Add sample tender and sample company evidence JSON files.

### Suggested Structure

```txt
bidworx/
  apps/
    web/
    api/
  packages/
    core/
      schemas/
      scoring/
      evidence/
      templates/
      parsers/
      reports/
  data/
    sample-company/
      capabilities.json
      case-studies.json
      policies.json
      certifications.json
      team-cvs.json
      past-bids.json
    sample-tenders/
      tender-001.json
  docs/
    bidworx.md
    tasklist.md
    task.md
  .rules
```

---

## Phase 1 - Domain Model Conversion

### Replace Existing Concepts

| Current CV System | Bidworx v2 Equivalent |
|---|---|
| Candidate profile | Organisation evidence library |
| Job description | Tender / RFP / bid document |
| Fit score | Bid readiness score |
| Skills match | Requirement coverage |
| Recruiter questions | Bid team questions |
| Interview talking points | Response strategy |
| Evidence snippets | Approved claims and proof points |
| Out-of-scope refusal | Evidence-missing refusal |

### Tasks
- [ ] Create typed schemas for tender documents.
- [ ] Create typed schemas for company evidence.
- [ ] Create typed schemas for requirement classification.
- [ ] Create typed schemas for coverage scoring.
- [ ] Create typed schemas for risk flags.
- [ ] Create typed schemas for answer plans.

---

## Phase 2 - Tender Requirement Extraction

### Goal
Turn raw tender text into structured bid requirements.

### Required Outputs
Each requirement should include:

```json
{
  "id": "REQ-001",
  "text": "Describe your approach to secure delivery in regulated environments.",
  "category": "security_governance",
  "type": "scored_question",
  "mandatory": true,
  "weighting": 20,
  "word_limit": 750,
  "deadline_relevance": false,
  "detected_keywords": ["secure delivery", "regulated", "governance"]
}
```

### Tasks
- [ ] Build `requirement_extractor`.
- [ ] Detect mandatory requirements.
- [ ] Detect scored questions.
- [ ] Detect admin/compliance requirements.
- [ ] Detect deadlines.
- [ ] Detect word limits.
- [ ] Detect evaluation weighting.
- [ ] Output structured JSON.
- [ ] Add unit tests using sample tender text.

---

## Phase 3 - Evidence Library

### Goal
Create a structured company knowledge base that can be queried deterministically.

### Evidence Types
- Capabilities
- Case studies
- Policies
- Certifications
- Accreditations
- Team CVs
- Delivery methods
- Security statements
- Governance processes
- Previous bid answers
- Client references
- Pricing assumptions

### Example Evidence Item

```json
{
  "id": "EV-001",
  "type": "case_study",
  "title": "AI Systems Delivery for Regulated Client",
  "summary": "Delivered a deterministic AI workflow with audit logging and controlled model usage.",
  "claims_supported": [
    "AI systems engineering",
    "regulated delivery",
    "auditability",
    "deterministic orchestration"
  ],
  "industries": ["financial_services", "public_sector"],
  "confidence": 0.88,
  "source": "approved_case_study_pack",
  "approved_for_bid_use": true
}
```

### Tasks
- [ ] Create sample evidence files.
- [ ] Add `approved_for_bid_use` flag.
- [ ] Add confidence per evidence item.
- [ ] Add claim support tags.
- [ ] Add sector tags.
- [ ] Add source attribution.
- [ ] Prevent unapproved evidence from being used in generated answers.

---

## Phase 4 - Evidence Matching Engine

### Goal
Match tender requirements to approved evidence.

### Matching Logic
The first version can use:
- keyword matching
- category matching
- weighted tag overlap
- sector relevance
- confidence thresholds
- mandatory requirement boost

Later versions can add embeddings, but deterministic matching should come first.

### Required Output

```json
{
  "requirement_id": "REQ-001",
  "coverage_score": 84,
  "confidence": "high",
  "matched_evidence": ["EV-001", "EV-004", "EV-009"],
  "missing_evidence": ["ISO 27001 certification not found"],
  "risk_flags": ["No named public-sector AI deployment found"],
  "recommendation": "Proceed with caution"
}
```

### Tasks
- [ ] Build `evidence_matcher`.
- [ ] Build weighted scoring model.
- [ ] Add hard refusal when no evidence exists.
- [ ] Add confidence labels: Low, Medium, High.
- [ ] Add missing evidence output.
- [ ] Add risk flags.
- [ ] Add tests for strong, partial, and weak matches.

---

## Phase 5 - Bid Readiness Score

### Goal
Produce an explainable bid/no-bid score.

### Suggested Subscores
- Requirement coverage
- Mandatory compliance
- Evidence strength
- Sector fit
- Delivery credibility
- Risk exposure
- Commercial readiness
- Deadline feasibility

### Score Output

```json
{
  "overall_score": 79,
  "decision": "Bid with mitigations",
  "subscores": {
    "requirement_coverage": 86,
    "mandatory_compliance": 92,
    "evidence_strength": 81,
    "sector_fit": 72,
    "delivery_credibility": 88,
    "risk_exposure": 64,
    "commercial_readiness": 70,
    "deadline_feasibility": 78
  },
  "summary": "The organisation has strong delivery evidence and good requirement coverage, but should address certification and public-sector proof gaps before submission."
}
```

### Tasks
- [ ] Build `coverage_scorer`.
- [ ] Build `bid_no_bid_engine`.
- [ ] Add explainable scoring rationale.
- [ ] Add thresholds:
  - 85+ Strong bid
  - 70-84 Bid with mitigations
  - 55-69 Weak bid
  - below 55 Do not bid unless strategic
- [ ] Add score calibration tests.

---

## Phase 6 - Compliance Matrix

### Goal
Generate a table mapping every tender requirement to evidence and status.

### Columns
- Requirement ID
- Requirement text
- Mandatory / scored / admin
- Evidence matched
- Coverage score
- Owner
- Status
- Risk
- Next action

### Tasks
- [ ] Build `compliance_matrix_builder`.
- [ ] Export as Markdown.
- [ ] Export as JSON.
- [ ] Optional: export as CSV.
- [ ] Highlight missing mandatory evidence.

---

## Phase 7 - Answer Plan Builder

### Goal
Generate structured answer plans before drafting prose.

### Important Rule
The system should generate an answer plan before generating final text.

### Answer Plan Format

```json
{
  "requirement_id": "REQ-001",
  "recommended_structure": [
    "Opening capability statement",
    "Relevant evidence",
    "Delivery methodology",
    "Governance and risk controls",
    "Outcome and proof points",
    "Closing reassurance"
  ],
  "evidence_to_include": ["EV-001", "EV-004"],
  "claims_allowed": [
    "We use deterministic orchestration before LLM generation",
    "We maintain audit logs for generated outputs"
  ],
  "claims_blocked": [
    "We are ISO 27001 certified"
  ],
  "notes": "Do not claim certification unless evidence is added."
}
```

### Tasks
- [ ] Build `answer_plan_builder`.
- [ ] Include allowed claims.
- [ ] Include blocked claims.
- [ ] Include suggested structure.
- [ ] Include evidence references.
- [ ] Include warnings.

---

## Phase 8 - Template Composer

### Goal
Generate bid responses without requiring an LLM.

### Method
Use deterministic templates such as:

```txt
[Capability statement]
[Evidence paragraph]
[Delivery method paragraph]
[Governance paragraph]
[Outcome paragraph]
[Risk mitigation paragraph]
```

### Tasks
- [ ] Create reusable response templates.
- [ ] Create section-level templates.
- [ ] Add tone options:
  - formal enterprise
  - concise executive
  - technical assurance
  - public-sector compliant
- [ ] Insert approved evidence only.
- [ ] Add word-count trimming logic.
- [ ] Add refusal text when evidence is insufficient.

---

## Phase 9 - Optional LLM Layer

### Goal
Allow LLM use only after the deterministic evidence layer has validated the claim set.

### Rules
- [ ] LLM must never access raw unsupported claims.
- [ ] LLM must only rewrite approved answer plans.
- [ ] LLM output must be checked against allowed claims.
- [ ] LLM must not introduce new clients, certifications, figures, or capabilities.
- [ ] Add claim-drift checker after LLM generation.

### Positioning
The LLM is a presentation layer, not the intelligence layer.

---

## Phase 10 - Demo Experience

### Demo Flow
1. Upload or paste tender text.
2. System extracts requirements.
3. System maps requirements to approved evidence.
4. System generates bid readiness score.
5. System produces compliance matrix.
6. System builds answer plans.
7. System optionally composes deterministic draft responses.
8. System refuses unsupported claims.

### Tasks
- [ ] Build demo tender input screen.
- [ ] Build bid readiness screen.
- [ ] Build requirement coverage screen.
- [ ] Build compliance matrix screen.
- [ ] Build answer plan screen.
- [ ] Build deterministic response preview.
- [ ] Build export buttons.

---

## Phase 11 - Pitch Notes for Exception

### What This Proves
- Production AI thinking
- Deterministic-first architecture
- Enterprise governance awareness
- Bid workflow understanding
- Product leadership
- Ability to turn a simple AI tool into a defensible platform

### Killer Demo Line
> This is not a chatbot for bids. It is a deterministic evidence engine that stops unsupported claims before they reach the proposal.

### Another Strong Line
> The safest AI bid system is the one that knows when not to write.
