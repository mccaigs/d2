import Link from "next/link";
import { ArrowRight, Layers, Cpu, Code2, Zap } from "lucide-react";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";

const CORE_STRENGTHS = [
  {
    icon: Cpu,
    title: "Applied AI Systems",
    description:
      "Designs and builds AI systems with clear product boundaries — not just LLM wrappers. Focused on deterministic, trustworthy outputs.",
  },
  {
    icon: Code2,
    title: "Full-Stack Engineering",
    description:
      "Strong across Python backend and Next.js frontend. Delivers end-to-end from architecture to deployed product.",
  },
  {
    icon: Layers,
    title: "Product Architecture",
    description:
      "Combines systems thinking with founder-style product instincts. Shapes ideas into credible, working products quickly.",
  },
  {
    icon: Zap,
    title: "Rapid MVP Delivery",
    description:
      "Known for speed from concept to working system. Builds with production-mindedness from day one.",
  },
];

const FEATURED_PROJECTS = [
  {
    name: "CareersAI",
    type: "SaaS Platform",
    summary:
      "A candidate-facing AI job intelligence platform. Structured fit scoring, role matching, and recruiter-facing visibility.",
    stack: ["Next.js", "TypeScript", "Convex", "Clerk", "Stripe"],
  },
  {
    name: "RecruitersAI",
    type: "SaaS Platform",
    summary:
      "Recruiter-side platform surfacing vetted, scored candidate intelligence to support faster hiring decisions.",
    stack: ["Next.js", "TypeScript", "Convex", "Clerk"],
  },
  {
    name: "InterviewsAI",
    type: "Applied AI Product",
    summary:
      "Structured interview and evaluation product with adaptive questioning, scoring, and backend evaluation logic.",
    stack: ["Python", "FastAPI", "Next.js", "TypeScript"],
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#faf8f0] text-stone-900">
      <SiteHeader />

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-6 sm:px-12 pt-20 pb-24">
        <div className="max-w-3xl">
          <p className="text-xs font-medium text-amber-700 uppercase tracking-widest mb-6">
            Scotland, UK — Open to senior AI roles
          </p>
          <h1 className="font-serif text-5xl sm:text-6xl lg:text-7xl leading-[1.05] text-stone-900 mb-8 text-balance">
            AI Architect &amp;
            <br />
            Systems Builder
          </h1>
          <p className="text-stone-600 text-lg sm:text-xl leading-relaxed max-w-xl mb-10">
            Senior AI consultant focused on applied AI systems, full-stack product
            development, and workflow automation. Strongest where product thinking,
            engineering delivery, and AI design overlap.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link
              href="/chat"
              className="flex items-center gap-2 px-6 py-3 bg-stone-900 text-stone-50 rounded-xl text-sm font-medium hover:bg-stone-800 transition-colors"
            >
              Ask the assistant
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a
              href="mailto:hello@davidrobertson.pro"
              className="px-6 py-3 border border-stone-300 text-stone-700 rounded-xl text-sm font-medium hover:border-stone-500 transition-colors"
            >
              Get in touch
            </a>
          </div>
        </div>
      </section>

      {/* Divider */}
      <div className="border-t border-stone-200" />

      {/* Core strengths */}
      <section className="max-w-5xl mx-auto px-6 sm:px-12 py-20">
        <p className="text-xs font-medium text-stone-400 uppercase tracking-widest mb-12">
          Core strengths
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {CORE_STRENGTHS.map((s) => (
            <div
              key={s.title}
              className="p-6 bg-[#fdfcf8] border border-stone-200 rounded-2xl"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-9 h-9 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center shrink-0">
                  <s.icon className="w-4 h-4 text-amber-700" />
                </div>
                <h3 className="font-serif text-lg text-stone-900">{s.title}</h3>
              </div>
              <p className="text-sm text-stone-600 leading-relaxed">{s.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Divider */}
      <div className="border-t border-stone-200" />

      {/* Featured projects */}
      <section className="max-w-5xl mx-auto px-6 sm:px-12 py-20">
        <p className="text-xs font-medium text-stone-400 uppercase tracking-widest mb-12">
          Featured builds
        </p>
        <div className="space-y-5">
          {FEATURED_PROJECTS.map((project) => (
            <div
              key={project.name}
              className="p-6 bg-[#fdfcf8] border border-stone-200 rounded-2xl"
            >
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mb-3">
                <div>
                  <h3 className="font-serif text-xl text-stone-900">{project.name}</h3>
                  <p className="text-xs text-stone-400 mt-0.5">{project.type}</p>
                </div>
                <div className="flex flex-wrap gap-1.5 sm:justify-end">
                  {project.stack.map((t) => (
                    <span
                      key={t}
                      className="px-2.5 py-1 text-xs bg-stone-100 text-stone-600 rounded-full border border-stone-200"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>
              <p className="text-sm text-stone-600 leading-relaxed">{project.summary}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Divider */}
      <div className="border-t border-stone-200" />

      {/* CTA */}
      <section className="max-w-5xl mx-auto px-6 sm:px-12 py-20">
        <div className="bg-stone-900 rounded-2xl px-8 py-12 text-center">
          <h2 className="font-serif text-3xl sm:text-4xl text-stone-50 mb-4 text-balance">
            Have a role or project in mind?
          </h2>
          <p className="text-stone-400 text-sm sm:text-base max-w-md mx-auto mb-8 leading-relaxed">
            Use the assistant to explore fit, or get in touch directly. David is
            open to senior AI engineering, architecture, and product engineering roles.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            <Link
              href="/chat"
              className="flex items-center gap-2 px-6 py-3 bg-stone-50 text-stone-900 rounded-xl text-sm font-medium hover:bg-white transition-colors"
            >
              Ask the assistant
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a
              href="mailto:hello@davidrobertson.pro"
              className="px-6 py-3 border border-stone-600 text-stone-300 rounded-xl text-sm font-medium hover:border-stone-400 hover:text-stone-100 transition-colors"
            >
              Send an email
            </a>
          </div>
        </div>
      </section>

      <SiteFooter />
    </div>
  );
}
