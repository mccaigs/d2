# Product Definition Record

## Project
davidrobertson.pro

## Product name
David Robertson - Recruiter Assistant

## Product type
Interactive recruiter-facing profile assistant with a Python backend and a Next.js frontend.

## Core idea
Create a premium, recruiter-friendly chat experience that answers questions about David Robertson’s professional background, technical skills, projects, experience, and role suitability.

The assistant must only answer from approved, structured career data. It must not hallucinate, speculate, or answer questions outside scope.

## Primary audience
- Recruiters
- Founders
- Hiring managers
- Technical interviewers
- Potential clients

## Problem statement
A static CV is passive and forces recruiters to scan manually for relevance.

This product turns a professional profile into an interactive system that:
- answers questions quickly
- surfaces relevant strengths
- provides evidence-backed responses
- demonstrates product, engineering, and AI systems thinking in the process

## Product goals
1. Present David Robertson as a senior AI architect / systems builder.
2. Make the profile easier to explore than a traditional CV.
3. Prove technical and product capability through the product itself.
4. Keep responses grounded, deterministic, and trustworthy.
5. Support future job description fit analysis.

## Non-goals
- General purpose chatbot
- Personal assistant
- Open-domain search engine
- Opinion generator
- Therapy, personal advice, or unrelated Q&A
- Full LLM dependency at MVP stage

## Key product principles
- Truth over fluency
- Structured evidence over vague claims
- Premium editorial design over flashy SaaS clutter
- Fast interaction over feature overload
- Calm confidence over gimmicks

## Scope for MVP

### In scope
- Recruiter chat interface
- Streaming responses from Python backend
- Structured CV knowledge base
- Deterministic question classification
- Deterministic retrieval and answer building
- Suggested prompts
- Source chips / evidence labels
- Scope refusal for unsupported questions
- Profile pages for skills, projects, experience, contact

### Out of scope for MVP
- Live LLM answer generation
- Voice mode
- Admin dashboard
- Recruiter authentication
- CV upload from external users
- Analytics dashboard
- Full job description document parsing

## Functional requirements

### Chat
- User can open `/chat`
- User can ask questions about David’s profile
- Assistant streams response progressively
- Assistant includes relevant evidence labels
- Assistant suggests follow-up questions
- Assistant refuses out-of-scope questions clearly

### Profile knowledge
- Knowledge must be stored in structured JSON files
- Knowledge must include:
  - profile summary
  - roles
  - skills
  - projects
  - achievements
  - preferred roles
  - sectors
  - FAQs

### Retrieval
- System classifies question into one or more intents
- System retrieves relevant data records
- System generates answer from templates and approved facts only

### Future fit analysis
- Architecture must allow a later feature where a recruiter pastes a job description
- System returns a deterministic fit analysis based on defined matching rules

## UX requirements
- Premium editorial visual style
- Minimal interface
- Mobile responsive
- Strong readability
- Clear recruiter-first prompts
- Clear visual distinction between suggested questions and chat responses
- Subtle streaming behaviour
- Calm motion only

## Trust and safety rules
- Never fabricate experience
- Never infer personal details
- Never answer beyond approved data
- Never overclaim suitability
- If confidence is low, say so
- If data is missing, say so plainly

## Success criteria
- Recruiter can understand David’s suitability in under 2 minutes
- Recruiter can ask at least 10 common questions and get useful answers
- Site feels premium and intentional
- Responses are accurate and grounded
- Product acts as a portfolio piece as much as a profile assistant

## MVP technical stack
- Frontend: Next.js 16.2, TypeScript, Tailwind, shadcn/ui
- Backend: Python, FastAPI, Pydantic
- Data: JSON initially, optional SQLite later
- Deployment: Vercel for web, Railway / Render / DigitalOcean for API

## Version roadmap

### v1
- Structured CV chat
- Streaming answers
- Suggested prompts
- Profile pages
- Contact CTA

### v1.1
- Job description paste fit analysis
- Better retrieval ranking
- Recruiter analytics
- Better source references

### v1.2
- Optional LLM rewriting layer behind feature flag
- Download CV CTA flow
- Calendly / contact conversion path