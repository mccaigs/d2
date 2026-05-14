import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export const metadata = {
  title: "Workflows - Bidworx",
  description: "Operational procurement intelligence workflows supported by Bidworx.",
};

const WORKFLOWS = [
  {
    name: "Tender opportunity triage",
    summary:
      "Assess buyer fit, mandatory requirements, evidence coverage, scoring signals, and delivery risk before committing bid time.",
    highlights: ["Requirement extraction", "Go/no-go scoring", "Risk and action summary"],
  },
  {
    name: "Evidence coverage review",
    summary:
      "Map proposed claims to approved proof points, policies, certifications, delivery examples, and evidence categories.",
    highlights: ["Claim support", "Evidence gaps", "Source chips"],
  },
  {
    name: "Compliance and submission check",
    summary:
      "Separate pass/fail requirements from scored quality answers and identify missing documents or declarations.",
    highlights: ["Mandatory artefacts", "Submission rules", "Compliance blockers"],
  },
];

export default function ProjectsPage() {
  return (
    <div className="min-h-screen bg-[#07111F] text-[#F8FAFC]">
      <nav className="flex items-center justify-between border-b border-[#1E3A5F] px-6 py-5 sm:px-12">
        <Link href="/" className="flex items-center gap-2 text-sm text-[#94A3B8] transition-colors hover:text-[#F8FAFC]">
          <ArrowLeft className="h-4 w-4" />
          <span>Back to command view</span>
        </Link>
      </nav>

      <main className="mx-auto max-w-4xl px-6 py-16 sm:px-12">
        <h1 className="mb-6 text-4xl font-bold text-[#F8FAFC] sm:text-5xl">
          Workflows
        </h1>
        <p className="mb-12 text-lg leading-8 text-[#94A3B8]">
          Bidworx structures tender intelligence into repeatable operational workflows.
        </p>

        <div className="space-y-6">
          {WORKFLOWS.map((workflow) => (
            <article key={workflow.name} className="border border-[#1E3A5F] bg-[#0D1B2E] p-6">
              <h2 className="text-2xl font-semibold text-[#F8FAFC]">{workflow.name}</h2>
              <p className="mt-3 leading-relaxed text-[#94A3B8]">{workflow.summary}</p>
              <div className="mt-5 flex flex-wrap gap-2">
                {workflow.highlights.map((highlight) => (
                  <span key={highlight} className="border border-[#1E3A5F] bg-[#101F35] px-2.5 py-1 text-xs text-[#38BDF8]">
                    {highlight}
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
