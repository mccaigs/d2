# Product Definition Record

## Project
Bidworx

## Product name
Bidworx

## Product type
Operational procurement intelligence platform with a Python backend and a Next.js frontend.

## Core idea
Bidworx provides evidence-backed bid intelligence for teams that cannot afford unsupported claims.

The platform analyses tenders, buyer requirements, compliance rules, scoring signals, and evidence coverage from approved structured data. It must not invent proof, certifications, delivery examples, policy coverage, or procurement claims.

## Primary audience
- Bid teams
- Proposal managers
- Procurement consultants
- Capture teams
- Commercial leaders
- Framework managers

## Problem statement
Bid teams often start writing before they know whether a tender is supportable. Unsupported claims, missing evidence, compliance gaps, and unclear buyer requirements can create wasted effort or submission risk.

Bidworx turns procurement material into operational intelligence:
- buyer requirements
- evidence needs
- compliance risks
- deterministic opportunity scores
- source-backed next actions

## Product goals
1. Help teams understand tender readiness before drafting.
2. Prevent unsupported claims from entering bid responses.
3. Score opportunity readiness with deterministic rules.
4. Preserve transparent source/evidence chips.
5. Keep scoped refusal behaviour when evidence is missing.

## Non-goals
- Generic chatbot
- Open-domain bid writer
- Unsupported AI proposal generator
- Legal advice
- Procurement system of record
- Full document management platform

## Key product principles
- Evidence over fluency
- Deterministic analysis over opaque judgement
- Compliance risk before response polish
- Source-backed claims only
- Operational clarity over generic chatbot styling

## Scope for MVP

### In scope
- Ask Bidworx chat interface
- Streaming responses from FastAPI
- Structured procurement JSON knowledge
- Deterministic question classification
- Deterministic retrieval and answer building
- Suggested tender prompts
- Evidence/source chips
- Scoped refusal for unsupported questions
- Bid readiness analysis from pasted tender text

### Out of scope for MVP
- Full tender document parsing
- Authenticated bid workspace
- Live collaboration
- Automated submission
- CRM/procurement suite integrations
- LLM-only answer generation

## Functional requirements

### Chat
- User can open `/chat`
- User can ask procurement and tender questions
- Bidworx streams responses progressively
- Bidworx includes relevant evidence/source chips
- Bidworx suggests follow-up questions
- Bidworx refuses out-of-scope or unsupported claims clearly

### Knowledge
- Knowledge must be stored in structured JSON files
- Knowledge must include:
  - product/company summary
  - capabilities
  - workflows
  - procurement examples
  - proof points
  - buyer roles
  - FAQs
  - tender/framework/compliance/scoring placeholders

### Retrieval
- System classifies question into one or more procurement intents
- System retrieves relevant structured data records
- System generates answers from templates and approved facts only

### Bid readiness analysis
- Architecture supports pasted tender text
- System returns deterministic readiness scoring based on defined matching rules

## UX requirements
- Dark operational SaaS design
- Mobile responsive
- Clear tender-first prompts
- Streaming response UX
- Evidence/source chips
- Compliance and risk language
- No generic chatbot styling

## Trust and safety rules
- Never fabricate evidence
- Never infer certifications or policies
- Never answer beyond approved data
- Never overclaim bid readiness
- If confidence is low, say so
- If evidence is missing, flag it plainly

## Success criteria
- Bid team can understand opportunity risk quickly
- User can ask common tender, evidence, and compliance questions
- Responses remain grounded and source-backed
- UI feels like procurement command infrastructure
- Product preserves deterministic architecture
