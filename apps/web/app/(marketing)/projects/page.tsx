import Link from "next/link";
import { ArrowLeft, ExternalLink } from "lucide-react";

export const metadata = {
  title: "Projects — David Robertson",
  description: "Featured projects and builds by David Robertson.",
};

const PROJECTS = [
  {
    name: "CareersAI",
    type: "SaaS Platform",
    summary: "A candidate-facing AI job intelligence platform focused on fit scoring, role matching, and recruiter-facing visibility.",
    highlights: [
      "Designed as a product for scored role matching and candidate insight",
      "Combines product thinking, AI workflow design, and SaaS delivery",
      "Built to present structured matching rather than vague recommendations",
    ],
    stack: ["Next.js", "TypeScript", "Convex", "Clerk", "Stripe", "Tailwind CSS"],
    themes: ["AI products", "recruitment", "fit scoring", "SaaS"],
  },
  {
    name: "RecruitersAI",
    type: "SaaS Platform",
    summary: "A recruiter-side platform designed to surface vetted, scored candidate intelligence and support faster hiring decisions.",
    highlights: [
      "Built as the recruiter-side counterpart to candidate intelligence workflows",
      "Focused on structured scoring, ranking, and relevance",
      "Designed with agency and employer workflows in mind",
    ],
    stack: ["Next.js", "TypeScript", "Convex", "Clerk", "Stripe"],
    themes: ["recruitment", "AI workflows", "SaaS", "matching systems"],
  },
  {
    name: "InterviewsAI",
    type: "Applied AI Product",
    summary: "A structured interview and evaluation product inspired by a real-world technical assessment pipeline, combining backend logic, evaluation, scoring, and adaptive questioning patterns.",
    highlights: [
      "Built from a real technical assessment idea and extended into a product concept",
      "Uses Python backend logic and a modern frontend stack",
      "Focused on evaluation flow, scoring, and adaptive questioning",
    ],
    stack: ["Python", "FastAPI", "Next.js", "TypeScript"],
    themes: ["interview systems", "evaluation", "AI product design", "workflow automation"],
  },
  {
    name: "UK AI Jobs Pipeline",
    type: "Automation System",
    summary: "A repeatable AI-assisted job search and scoring pipeline that scans job sources, filters relevant roles, and produces structured match reports.",
    highlights: [
      "Demonstrates workflow automation and practical AI system design",
      "Built around daily sourcing, filtering, and fit scoring",
      "Acts as both a practical tool and a proof of systems thinking",
    ],
    stack: ["Python", "Markdown pipelines", "GitHub", "Automation tooling"],
    themes: ["automation", "AI workflows", "recruitment intelligence", "scoring"],
  },
  {
    name: "AI IDE initiative",
    type: "Product Concept / Engineering Initiative",
    summary: "An AI IDE concept inspired by modern coding assistants, focused on model routing, local and cloud workflows, and transparent usage design.",
    highlights: [
      "Shows product-level thinking around AI developer tooling",
      "Explores architecture choices rather than superficial AI wrapping",
      "Focused on practical value, transparency, and system design",
    ],
    stack: ["VS Code ecosystem", "AI workflows", "Product architecture"],
    themes: ["developer tools", "AI systems", "product architecture"],
  },
];

export default function ProjectsPage() {
  return (
    <div className="min-h-screen bg-[#faf8f0] text-stone-900">
      <nav className="flex items-center justify-between px-6 sm:px-12 py-5 border-b border-stone-200">
        <Link href="/" className="flex items-center gap-2 text-sm text-stone-500 hover:text-stone-800 transition-colors">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to home</span>
        </Link>
      </nav>

      <main className="max-w-4xl mx-auto px-6 sm:px-12 py-16">
        <h1 className="font-serif text-4xl sm:text-5xl text-stone-900 mb-6">
          Featured Projects
        </h1>
        <p className="text-stone-600 text-lg leading-relaxed mb-12">
          A selection of applied AI products, SaaS platforms, and automation systems built 
          to demonstrate product thinking, systems design, and end-to-end delivery.
        </p>

        <div className="space-y-8">
          {PROJECTS.map((project) => (
            <article key={project.name} className="p-6 bg-[#fdfcf8] border border-stone-200 rounded-2xl">
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mb-4">
                <div>
                  <h2 className="font-serif text-2xl text-stone-900">{project.name}</h2>
                  <p className="text-sm text-stone-400 mt-1">{project.type}</p>
                </div>
                <div className="flex flex-wrap gap-1.5 sm:justify-end">
                  {project.stack.slice(0, 4).map((tech) => (
                    <span
                      key={tech}
                      className="px-2.5 py-1 text-xs bg-stone-100 text-stone-600 rounded-full border border-stone-200"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>

              <p className="text-stone-600 leading-relaxed mb-4">{project.summary}</p>

              <div className="mb-4">
                <h3 className="text-sm font-medium text-stone-500 uppercase tracking-wider mb-2">
                  Highlights
                </h3>
                <ul className="space-y-1.5">
                  {project.highlights.map((highlight, i) => (
                    <li key={i} className="flex gap-2 text-sm text-stone-600">
                      <span className="text-amber-600/70 mt-0.5 shrink-0">—</span>
                      <span>{highlight}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="flex flex-wrap gap-1.5">
                {project.themes.map((theme) => (
                  <span
                    key={theme}
                    className="px-2 py-0.5 text-xs text-amber-700 bg-amber-50 rounded border border-amber-200"
                  >
                    {theme}
                  </span>
                ))}
              </div>
            </article>
          ))}
        </div>
      </main>
    </div>
  );
}
