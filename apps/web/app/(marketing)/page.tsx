import Link from "next/link";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  FileSearch,
  Gauge,
  Layers,
  ShieldCheck,
} from "lucide-react";
import { SiteHeader } from "@/components/layout/site-header";
import { SiteFooter } from "@/components/layout/site-footer";

const ANALYSIS_AREAS = [
  "Buyer requirements",
  "Mandatory compliance",
  "Scored questions",
  "Evidence gaps",
  "Submission artefacts",
  "Commercial fit",
];

const SCORING_RULES = [
  "Requirement coverage",
  "Evidence strength",
  "Compliance readiness",
  "Delivery risk",
  "Commercial fit",
];

const WORKFLOW = [
  "Ingest tender text",
  "Extract buyer requirements",
  "Map evidence and proof points",
  "Flag compliance risk",
  "Score readiness",
  "Return sourced next actions",
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#07111F] text-[#F8FAFC]">
      <SiteHeader />

      <section className="mx-auto max-w-6xl px-6 pb-16 pt-16 sm:px-12 lg:pb-20">
        <div className="grid gap-10 lg:grid-cols-[1.05fr_0.95fr] lg:items-center">
          <div>
            <p className="mb-5 text-xs font-semibold uppercase tracking-[0.28em] text-[#38BDF8]">
              Bidworx procurement intelligence
            </p>
            <h1 className="max-w-4xl text-5xl font-bold leading-[1.05] text-balance text-[#F8FAFC] sm:text-6xl lg:text-7xl">
              Evidence-backed bid intelligence for teams that cannot afford unsupported claims.
            </h1>
            <p className="mt-7 max-w-2xl text-lg leading-8 text-[#94A3B8]">
              Analyse tenders, score opportunity readiness, map proof points,
              and catch compliance risk before response writing begins.
            </p>
            <div className="mt-9 flex flex-wrap gap-3">
              <Link
                href="/chat"
                className="inline-flex items-center gap-2 rounded-lg bg-[#38BDF8] px-5 py-3 text-sm font-semibold text-[#07111F] transition-colors hover:bg-[#60A5FA]"
              >
                Analyse a tender
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="#workflow"
                className="rounded-lg border border-[#1E3A5F] bg-[#0D1B2E] px-5 py-3 text-sm font-semibold text-[#F8FAFC] transition-colors hover:border-[#38BDF8]"
              >
                View workflow
              </Link>
            </div>
          </div>

          <div className="border border-[#1E3A5F] bg-[#0D1B2E] p-5">
            <div className="mb-5 flex items-center justify-between border-b border-[#1E3A5F] pb-4">
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-[#94A3B8]">
                  Tender readout
                </p>
                <p className="mt-1 text-sm font-semibold text-[#F8FAFC]">
                  Opportunity readiness
                </p>
              </div>
              <Gauge className="h-6 w-6 text-[#38BDF8]" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              {SCORING_RULES.map((item, index) => (
                <div key={item} className="border border-[#1E3A5F] bg-[#101F35] p-4">
                  <p className="text-2xl font-bold text-[#F8FAFC]">{82 - index * 7}</p>
                  <p className="mt-1 text-xs text-[#94A3B8]">{item}</p>
                </div>
              ))}
            </div>
            <div className="mt-4 border border-[#1E3A5F] bg-[#101F35] p-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-[#F59E0B]">
                <AlertTriangle className="h-4 w-4" />
                Evidence gap detected
              </div>
              <p className="mt-2 text-sm leading-6 text-[#94A3B8]">
                Delivery methodology claim requires an approved case example or policy source.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="border-y border-[#1E3A5F] bg-[#0D1B2E]">
        <div className="mx-auto max-w-6xl px-6 py-16 sm:px-12">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[#38BDF8]">
            Evidence-backed bid intelligence
          </p>
          <div className="mt-6 grid gap-6 lg:grid-cols-3">
            {[
              ["Approved evidence only", "Answers are grounded in structured source records and source chips."],
              ["Unsupported claims flagged", "The platform identifies where a claim lacks proof before it reaches the buyer."],
              ["Deterministic by default", "Classification, retrieval, scoring, and answer building remain rule-based."],
            ].map(([title, copy]) => (
              <div key={title} className="border border-[#1E3A5F] bg-[#101F35] p-5">
                <CheckCircle2 className="mb-4 h-5 w-5 text-[#22C55E]" />
                <h2 className="text-base font-semibold text-[#F8FAFC]">{title}</h2>
                <p className="mt-3 text-sm leading-6 text-[#94A3B8]">{copy}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 py-16 sm:px-12">
        <div className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr] lg:items-start">
          <div>
            <FileSearch className="mb-4 h-7 w-7 text-[#38BDF8]" />
            <h2 className="text-3xl font-bold text-[#F8FAFC]">What Bidworx analyses</h2>
            <p className="mt-4 text-sm leading-7 text-[#94A3B8]">
              The platform turns tender material into structured operational intelligence for bid teams.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {ANALYSIS_AREAS.map((area) => (
              <div key={area} className="border border-[#1E3A5F] bg-[#0D1B2E] px-4 py-3 text-sm font-medium text-[#F8FAFC]">
                {area}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="border-y border-[#1E3A5F] bg-[#0D1B2E]">
        <div className="mx-auto grid max-w-6xl gap-8 px-6 py-16 sm:px-12 lg:grid-cols-2">
          <div>
            <Gauge className="mb-4 h-7 w-7 text-[#60A5FA]" />
            <h2 className="text-3xl font-bold">Deterministic scoring</h2>
            <p className="mt-4 text-sm leading-7 text-[#94A3B8]">
              Opportunity readiness is scored from explicit dimensions and transparent weights, not vague model confidence.
            </p>
          </div>
          <div>
            <ShieldCheck className="mb-4 h-7 w-7 text-[#22C55E]" />
            <h2 className="text-3xl font-bold">Compliance and risk checks</h2>
            <p className="mt-4 text-sm leading-7 text-[#94A3B8]">
              Mandatory documents, pass/fail rules, unsupported declarations, and submission instructions are separated from quality scoring.
            </p>
          </div>
        </div>
      </section>

      <section id="workflow" className="mx-auto max-w-6xl px-6 py-16 sm:px-12">
        <div className="mb-8 flex items-center gap-3">
          <Layers className="h-7 w-7 text-[#38BDF8]" />
          <h2 className="text-3xl font-bold">Tender intelligence workflow</h2>
        </div>
        <div className="grid gap-3 md:grid-cols-3">
          {WORKFLOW.map((step, index) => (
            <div key={step} className="border border-[#1E3A5F] bg-[#0D1B2E] p-5">
              <p className="text-xs font-semibold text-[#38BDF8]">0{index + 1}</p>
              <p className="mt-3 text-sm font-semibold text-[#F8FAFC]">{step}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-6 pb-20 sm:px-12">
        <div className="border border-[#1E3A5F] bg-[#101F35] px-6 py-10 text-center">
          <h2 className="text-3xl font-bold text-[#F8FAFC]">
            Ready to test a tender against your evidence?
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-sm leading-7 text-[#94A3B8]">
            Ask Bidworx to summarise buyer requirements, score the opportunity,
            and identify unsupported claims before the team starts drafting.
          </p>
          <Link
            href="/chat"
            className="mt-7 inline-flex items-center gap-2 rounded-lg bg-[#22C55E] px-5 py-3 text-sm font-semibold text-[#07111F] transition-colors hover:bg-[#38BDF8]"
          >
            Analyse a tender
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

      <SiteFooter />
    </div>
  );
}
