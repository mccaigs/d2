# Bidworx v2 - Product and Architecture Brief

## Working Title
Bidworx v2 - Deterministic Bid Intelligence Platform

## One-Line Summary
Bidworx v2 analyses tender requirements, maps them to approved organisational evidence, scores bid readiness, identifies risk, and assembles compliant responses without relying on an LLM to invent content.

## Product Positioning
Bidworx should not be positioned as an AI bid writer.

It should be positioned as:

> A deterministic bid intelligence and evidence orchestration platform for organisations that need trustworthy, auditable, and compliant proposal responses.

The system should feel like an operational bid command centre, not a generic document generator.

---

## Core Philosophy
Most AI bid tools ask the model to write first and verify later.

Bidworx v2 should do the opposite:

1. Extract the tender requirements.
2. Identify what the buyer is actually asking for.
3. Match requirements against approved evidence.
4. Score confidence and coverage.
5. Flag missing evidence and risk.
6. Build an answer plan.
7. Compose only from verified claims.
8. Optionally let an LLM polish the final wording.

The system must always prefer truthful incompleteness over fluent invention.

---

## Product Principles

### 1. Evidence Before Prose
No final answer should be generated until the system has identified the evidence that supports it.

### 2. Deterministic First
Rules, schemas, scoring, templates, and structured data should perform the critical work.

### 3. LLM Optional
The product should function without an LLM. If an LLM is used, it should only rewrite approved claim sets.

### 4. Explain Every Score
A bid readiness score is only useful if the user can see why the score exists.

### 5. Refuse Unsupported Claims
The system should explicitly block claims that cannot be proven by the evidence library.

### 6. Build for Regulated Buyers
The tone, workflow, and audit trail should feel credible to finance, government, healthcare, infrastructure, and enterprise clients.

---

## Core User

### Primary User
Bid manager, proposal lead, sales lead, consultancy partner, or founder responding to tenders.

### Secondary Users
- Delivery leads
- Technical architects
- Compliance teams
- Commercial teams
- Senior executives reviewing bid/no-bid decisions

---

## Main Use Cases

### 1. Bid / No-Bid Decision
User uploads or pastes a tender. Bidworx analyses the requirements and gives a readiness score with risks and missing evidence.

### 2. Compliance Matrix
Bidworx maps every requirement to evidence, owner, status, and risk.

### 3. Response Planning
Bidworx creates structured answer plans for each scored question.

### 4. Deterministic Drafting
Bidworx assembles draft responses from approved claims, templates, and case studies.

### 5. Evidence Gap Detection
Bidworx tells the organisation what evidence it needs before submission.

### 6. Claim Governance
Bidworx prevents unsupported claims from entering the proposal.

---

## System Architecture

```txt
Tender Input
   ↓
Tender Parser
   ↓
Requirement Extractor
   ↓
Requirement Classifier
   ↓
Evidence Matcher
   ↓
Coverage Scorer
   ↓
Risk Register
   ↓
Bid Readiness Engine
   ↓
Compliance Matrix
   ↓
Answer Plan Builder
   ↓
Template Composer
   ↓
Optional LLM Rewrite
   ↓
Claim Drift Check
   ↓
Export
```

---

## Main Modules

### Tender Parser
Converts uploaded or pasted tender content into structured sections.

Outputs:
- title
- buyer
- deadline
- sections
- questions
- word limits
- evaluation weightings
- mandatory requirements

### Requirement Extractor
Identifies the real asks hidden inside tender documents.

Example categories:
- security
- governance
- delivery methodology
- AI capability
- project management
- financial stability
- public-sector experience
- technical architecture
- support and maintenance
- implementation plan

### Evidence Library
A structured repository of approved organisational knowledge.

Evidence types:
- case studies
- capability statements
- team CVs
- policies
- certifications
- accreditations
- previous bid responses
- delivery methods
- client references
- security controls

### Evidence Matcher
Matches extracted requirements against approved evidence.

Scoring inputs:
- tag overlap
- category match
- sector relevance
- confidence level
- approval status
- recency
- mandatory requirement importance

### Coverage Scorer
Calculates how well the organisation can answer the tender.

Subscores:
- requirement coverage
- mandatory compliance
- evidence strength
- delivery credibility
- sector fit
- commercial readiness
- risk exposure
- deadline feasibility

### Risk Register
Flags bid risks before drafting starts.

Examples:
- missing certification
- weak sector evidence
- unsupported claim
- no named case study
- no owner assigned
- low confidence evidence
- mandatory requirement not covered

### Compliance Matrix Builder
Creates an auditable requirement-by-requirement view.

### Answer Plan Builder
Creates the response skeleton for each tender question.

### Template Composer
Generates prose from deterministic templates and approved evidence.

### Optional LLM Layer
Only rewrites approved text. It must not create new claims.

### Claim Drift Checker
Compares LLM output against allowed claims and blocks unauthorised additions.

---

## Data Model Sketch

### Tender Requirement

```json
{
  "id": "REQ-001",
  "text": "Describe your approach to secure AI delivery in regulated environments.",
  "category": "security_governance",
  "type": "scored_question",
  "mandatory": true,
  "weighting": 20,
  "word_limit": 750,
  "detected_keywords": ["secure", "AI", "regulated", "governance"]
}
```

### Evidence Item

```json
{
  "id": "EV-001",
  "type": "case_study",
  "title": "Deterministic AI Workflow Delivery",
  "summary": "Delivered a deterministic AI system with validated evidence retrieval, audit logging, and controlled model use.",
  "claims_supported": [
    "deterministic AI orchestration",
    "audit logging",
    "controlled LLM usage",
    "enterprise workflow automation"
  ],
  "industries": ["financial_services", "consultancy", "public_sector"],
  "confidence": 0.9,
  "approved_for_bid_use": true,
  "source": "approved_case_study_library"
}
```

### Bid Readiness Result

```json
{
  "overall_score": 82,
  "decision": "Bid with mitigations",
  "confidence": "High",
  "summary": "Strong technical and delivery evidence, but public-sector references and certification evidence should be strengthened before submission.",
  "top_strengths": [
    "Strong AI delivery evidence",
    "Clear governance methodology",
    "Relevant technical architecture experience"
  ],
  "top_risks": [
    "No explicit ISO 27001 certification found",
    "Limited named public-sector case studies"
  ]
}
```

---

## Scoring Bands

| Score | Decision | Meaning |
|---:|---|---|
| 85-100 | Strong bid | Good evidence coverage and low material risk |
| 70-84 | Bid with mitigations | Viable, but gaps should be addressed |
| 55-69 | Weak bid | Significant evidence or compliance gaps |
| 0-54 | Do not bid unless strategic | Risk too high or evidence too weak |

---

## MVP Scope

### Must Have
- Paste tender text
- Extract requirements
- Use sample evidence library
- Match evidence to requirements
- Generate bid readiness score
- Produce compliance matrix
- Generate answer plans
- Compose deterministic draft answer
- Refuse unsupported claims
- Export Markdown report

### Should Have
- Upload PDF or DOCX later
- CSV export
- Word export
- Evidence editor
- Owner assignment
- Risk register view

### Not Required for First Demo
- Full authentication
- Multi-tenant workspace
- Payment integration
- Live collaboration
- Complex embeddings
- Full LLM workflow

---

## First Demo Scenario

### Tender Question
Describe your approach to delivering secure, auditable AI systems in regulated environments.

### Evidence Available
- Deterministic AI architecture
- Audit logs
- Evaluation harness
- Human review checkpoints
- Controlled LLM usage

### Evidence Missing
- Formal ISO 27001 certification
- Named banking deployment

### Expected Output
- Good score, but not perfect
- Clear evidence matches
- Clear risk warning
- Answer plan generated
- Draft answer avoids unsupported claims
- System refuses to claim ISO certification

---

## Design Tone
The interface should feel:
- precise
- calm
- operational
- enterprise-grade
- trustworthy
- evidence-led

Avoid:
- gimmicky chatbot language
- fake AI magic
- overconfident claims
- cartoonish colours
- vague productivity wording

Preferred language:
- evidence coverage
- bid readiness
- claim confidence
- requirement mapping
- compliance matrix
- risk register
- approved evidence
- unsupported claim blocked

---

## Pitch to Exception
This is the product-level argument:

> I took the deterministic fit-analysis architecture from my interactive CV and applied it to Bidworx. Instead of using AI to write unsupported bid prose, the system now extracts tender requirements, maps them to approved evidence, scores readiness, identifies risk, and only then assembles responses. The LLM becomes optional polish, not the core product.

What this demonstrates:
- product judgement
- enterprise AI architecture
- practical governance
- commercially useful workflow design
- ability to improve an existing AI product direction
- deterministic-first thinking

## Strongest Line
The safest AI bid system is the one that knows when not to write.
