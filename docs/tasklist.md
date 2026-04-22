# Build Order Tasklist

## Week 1 target
Ship a polished MVP with deterministic streaming chat and recruiter-facing profile pages.

---

## Priority 1 - Core repo and scaffolding
- [ ] Create monorepo root
- [ ] Create `apps/web`
- [ ] Create `apps/api`
- [ ] Create `docs`
- [ ] Add `pnpm-workspace.yaml`
- [ ] Add `turbo.json`
- [ ] Add root `README.md`

## Priority 2 - Web foundations
- [ ] Scaffold Next.js 16.2 app
- [ ] Install Tailwind
- [ ] Install shadcn/ui
- [ ] Add Newsreader and Manrope
- [ ] Create global styles
- [ ] Create base layout
- [ ] Create homepage route
- [ ] Create chat route

## Priority 3 - API foundations
- [ ] Scaffold FastAPI app
- [ ] Add route registration
- [ ] Add config module
- [ ] Add models
- [ ] Add service structure
- [ ] Add test scaffolding

## Priority 4 - Knowledge base
- [ ] Convert CV into structured JSON
- [ ] Write `profile.json`
- [ ] Write `skills.json`
- [ ] Write `projects.json`
- [ ] Write `experience.json`
- [ ] Write `achievements.json`
- [ ] Write `faqs.json`
- [ ] Write `job_titles.json`

## Priority 5 - Chat engine
- [ ] Implement intent classifier
- [ ] Implement retriever
- [ ] Implement answer builder
- [ ] Implement out-of-scope refusal
- [ ] Add confidence logic
- [ ] Add follow-up suggestion generation

## Priority 6 - Streaming
- [ ] Build `/chat/stream` endpoint
- [ ] Stream text progressively
- [ ] Return sources metadata
- [ ] Return follow-up prompts
- [ ] Handle error cases

## Priority 7 - Chat UI
- [ ] Build empty state
- [ ] Build suggestion cards
- [ ] Build sticky input
- [ ] Build streamed assistant message rendering
- [ ] Build source chips
- [ ] Build follow-up suggestions
- [ ] Add loading states
- [ ] Add error state

## Priority 8 - Marketing pages
- [ ] Build homepage hero
- [ ] Build profile page
- [ ] Build projects page
- [ ] Build contact page

## Priority 9 - Polish
- [ ] Copy pass
- [ ] Mobile pass
- [ ] Accessibility pass
- [ ] Performance pass
- [ ] Visual consistency pass

## Priority 10 - Deployment
- [ ] Deploy web
- [ ] Deploy API
- [ ] Connect domain
- [ ] Add health endpoint
- [ ] Smoke test production build

---

## MVP definition of done
- [ ] Recruiter can open the site
- [ ] Recruiter can ask questions in chat
- [ ] Answers stream smoothly
- [ ] Answers remain within approved CV scope
- [ ] UI feels premium and intentional
- [ ] Site works well on desktop and mobile