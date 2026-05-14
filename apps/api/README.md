# Bidworx API

FastAPI backend for evidence-backed bid intelligence.

## Capabilities

- Streaming chat endpoint with deterministic answers from structured procurement data
- Product summary endpoint
- Suggested prompts for tender analysis
- Deterministic bid readiness scoring
- Scoped refusal when approved evidence is missing

## Routes

- `GET /api/health`
- `POST /api/chat/stream`
- `GET /api/profile`
- `GET /api/suggestions`
- `POST /api/fit/analyse`

The `/fit/analyse` route keeps the existing response contract while scoring bid readiness rather than legacy suitability.

## Data

- `product.json` - Bidworx positioning, operating model, and use cases
- `capabilities.json` - procurement analysis capabilities
- `workflows.json` - tender intelligence workflows
- `procurement_examples.json` - procurement analysis examples and domains
- `buyer_roles.json` - buyer-side roles and evaluators
- `faqs.json` - common Bidworx questions
- `proof_points.json` - trust and evidence proof points
- `tenders.json` - placeholder tender records
- `frameworks.json` - placeholder framework records
- `compliance_rules.json` - compliance rule placeholders
- `scoring_rules.json` - deterministic scoring dimensions
- `evidence_categories.json` - supported evidence category placeholders
