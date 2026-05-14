# Bidworx v2 - Build Task for AI Coding Agent

## Objective
Create a working MVP of Bidworx v2 by adapting the deterministic architecture from `davidrobertson.pro` into a bid intelligence platform.

The MVP should prove the core product idea:

> Tender requirements are extracted, mapped to approved evidence, scored for bid readiness, and converted into answer plans or deterministic draft responses without unsupported claims.

---

## Important Constraints
- Use British English.
- Do not use em dashes.
- Do not make the app feel like a generic chatbot.
- Do not build a prompt-wrapper product.
- Do not allow unsupported claims into generated responses.
- Prefer deterministic logic before LLM usage.
- The MVP must work without an LLM.
- Any optional LLM layer must only rewrite approved claims.

---

## Source System to Reuse
Reuse the existing deterministic CV assistant patterns from `davidrobertson.pro`:

- streaming chat-style UI
- deterministic retrieval
- bounded knowledge base
- refusal outside scope
- fit scoring pattern
- evidence-backed rationale
- clean explanation style
- structured JSON data
- typed schemas where possible

Rename and adapt the concepts:

```txt
candidate -> organisation
job description -> tender
fit analysis -> bid readiness analysis
skills -> capabilities
career evidence -> bid evidence
interview talking points -> response strategy
out-of-scope refusal -> unsupported claim refusal
```

---

## Build the Following MVP Modules

### 1. Tender Input
Create a page or component where the user can paste tender/RFP text.

Include a sample tender button using this text:

```txt
Question 1: Describe your approach to delivering secure, auditable AI systems in regulated environments. Your response should include your delivery methodology, governance controls, testing approach, and how you prevent unsupported or inaccurate AI-generated outputs. Maximum 750 words. Weighting: 25%.

Mandatory requirement: Supplier must demonstrate experience delivering software systems for enterprise or regulated clients.

Question 2: Explain how you manage project delivery, stakeholder communication, risk, and reporting throughout implementation. Maximum 500 words. Weighting: 15%.

Question 3: Provide evidence of relevant previous work, including case studies, outcomes, and measurable impact. Maximum 600 words. Weighting: 20%.
```

---

### 2. Requirement Extractor
Create deterministic extraction logic that identifies:
- questions
- mandatory requirements
- word limits
- weighting
- categories
- keywords

Return structured requirements.

Example output:

```json
{
  "id": "REQ-001",
  "text": "Describe your approach to delivering secure, auditable AI systems in regulated environments.",
  "type": "scored_question",
  "category": "ai_governance",
  "mandatory": false,
  "word_limit": 750,
  "weighting": 25,
  "keywords": ["secure", "auditable", "AI", "regulated", "governance", "testing"]
}
```

---

### 3. Sample Evidence Library
Create a local sample evidence file.

Example evidence items:

```json
[
  {
    "id": "EV-001",
    "type": "case_study",
    "title": "Deterministic AI Fit Analysis Platform",
    "summary": "Built a deterministic interactive CV platform that scores role fit using structured evidence, calibrated subscores, and refusal behaviour for out-of-scope queries.",
    "claims_supported": [
      "deterministic AI orchestration",
      "evidence-backed scoring",
      "bounded AI-like interaction",
      "refusal outside approved scope"
    ],
    "categories": ["ai_governance", "software_engineering", "product_architecture"],
    "industries": ["recruitment", "enterprise", "consultancy"],
    "confidence": 0.92,
    "approved_for_bid_use": true
  },
  {
    "id": "EV-002",
    "type": "methodology",
    "title": "Deterministic First AI Delivery Methodology",
    "summary": "Use structured data, typed schemas, deterministic rules, tests, logging, and human review before applying LLMs for interpretation or final wording.",
    "claims_supported": [
      "deterministic-first delivery",
      "LLM as optional presentation layer",
      "auditability",
      "human review"
    ],
    "categories": ["ai_governance", "delivery_methodology", "risk_management"],
    "industries": ["financial_services", "public_sector", "enterprise"],
    "confidence": 0.9,
    "approved_for_bid_use": true
  },
  {
    "id": "EV-003",
    "type": "policy",
    "title": "Unsupported Claim Prevention",
    "summary": "The system blocks claims that cannot be supported by approved evidence and flags missing evidence before response generation.",
    "claims_supported": [
      "unsupported claim prevention",
      "evidence validation",
      "risk flagging",
      "audit trail"
    ],
    "categories": ["compliance", "risk_management", "ai_governance"],
    "industries": ["enterprise", "regulated"],
    "confidence": 0.86,
    "approved_for_bid_use": true
  },
  {
    "id": "EV-004",
    "type": "certification",
    "title": "ISO 27001 Certification",
    "summary": "No ISO 27001 certification evidence has been supplied.",
    "claims_supported": [],
    "categories": ["security", "compliance"],
    "industries": [],
    "confidence": 0,
    "approved_for_bid_use": false
  }
]
```

---

### 4. Evidence Matcher
Build deterministic matching based on:
- category overlap
- keyword overlap
- claim support overlap
- approved evidence only
- confidence threshold
- mandatory requirement importance

Return:
- matched evidence
- coverage score
- confidence label
- missing evidence
- risk flags

---

### 5. Bid Readiness Engine
Calculate an explainable overall score.

Use these subscores:
- requirement coverage
- mandatory compliance
- evidence strength
- sector fit
- delivery credibility
- risk exposure
- deadline feasibility

Suggested decision bands:

```txt
85-100: Strong bid
70-84: Bid with mitigations
55-69: Weak bid
0-54: Do not bid unless strategic
```

---

### 6. Compliance Matrix
Render a table with:
- requirement ID
- requirement summary
- type
- matched evidence
- score
- confidence
- risks
- next action

---

### 7. Answer Plan Builder
For each scored question, generate an answer plan:

```json
{
  "requirement_id": "REQ-001",
  "structure": [
    "Opening capability statement",
    "Delivery methodology",
    "Governance controls",
    "Testing and validation",
    "Unsupported claim prevention",
    "Evidence and outcomes"
  ],
  "approved_claims": [
    "We use deterministic orchestration before LLM generation",
    "We maintain bounded evidence-backed responses",
    "We block unsupported claims"
  ],
  "blocked_claims": [
    "ISO 27001 certified"
  ],
  "warnings": [
    "No certification evidence supplied"
  ]
}
```

---

### 8. Deterministic Draft Composer
Create a first-draft response using templates and approved evidence.

Do not use an LLM.

The composer should:
- include only approved evidence
- avoid unsupported claims
- include caveats where evidence is missing
- respect word limits where possible
- use formal enterprise language

Example refusal behaviour:

```txt
I cannot include the claim "ISO 27001 certified" because no approved evidence for this certification exists in the evidence library.
```

---

### 9. UI Requirements
Create three main views:

1. Bid Readiness
   - overall score
   - decision
   - subscores
   - top strengths
   - top risks

2. Compliance Matrix
   - requirement-by-requirement mapping

3. Response Builder
   - answer plan
   - approved claims
   - blocked claims
   - deterministic draft

UI tone:
- dark, premium, operational
- calm and enterprise-grade
- less is more
- no gimmicky AI sparkle styling

---

## Acceptance Criteria
The MVP is complete when:

- [ ] User can paste sample tender text.
- [ ] System extracts requirements.
- [ ] System matches evidence.
- [ ] System scores bid readiness.
- [ ] System shows a compliance matrix.
- [ ] System creates answer plans.
- [ ] System creates deterministic draft responses.
- [ ] System refuses unsupported claims.
- [ ] System works without an LLM.
- [ ] Code is clean, typed, and easy to extend.
- [ ] Demo can be shown in under five minutes.

---

## Final Demo Narrative
Use this when presenting the prototype:

> I took the deterministic fit-analysis architecture from my interactive CV and applied it to Bidworx. The system does not ask an LLM to invent bid prose. It extracts the buyer requirements, maps them to approved evidence, scores the bid, identifies risk, builds an answer plan, and only then composes a response. The LLM is optional polish, not the product brain.

## Killer Line
The safest AI bid system is the one that knows when not to write.
