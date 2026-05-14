import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export const metadata = {
  title: "Platform - Bidworx",
  description: "Bidworx product structure, procurement intelligence model, and trust principles.",
};

const PRINCIPLES = [
  "Structured JSON knowledge",
  "FastAPI backend",
  "Pydantic models",
  "Deterministic classifier",
  "Deterministic retriever",
  "Deterministic answer builder",
  "Streaming response UX",
  "Evidence/source chips",
  "Scoped refusal behaviour",
];

export default function ProfilePage() {
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
          Platform
        </h1>
        <p className="mb-12 text-lg leading-8 text-[#94A3B8]">
          Bidworx is evidence-backed bid intelligence for teams that cannot
          afford unsupported claims. It is built around deterministic
          procurement analysis rather than generic bid generation.
        </p>

        <section className="mb-12">
          <h2 className="mb-4 text-2xl font-semibold text-[#F8FAFC]">Operating Model</h2>
          <p className="leading-relaxed text-[#CBD5E1]">
            The system extracts buyer requirements, maps claims to approved
            evidence, scores bid readiness, flags compliance risks, and refuses
            unsupported assertions when the evidence library is incomplete.
          </p>
        </section>

        <section className="mb-12">
          <h2 className="mb-4 text-2xl font-semibold text-[#F8FAFC]">Architecture Preserved</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {PRINCIPLES.map((item) => (
              <div key={item} className="border border-[#1E3A5F] bg-[#0D1B2E] px-4 py-3 text-sm text-[#CBD5E1]">
                {item}
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2 className="mb-4 text-2xl font-semibold text-[#F8FAFC]">Next Step</h2>
          <p className="leading-relaxed text-[#CBD5E1]">
            Use <Link href="/chat" className="text-[#38BDF8] underline underline-offset-4">Ask Bidworx</Link> to analyse a tender, score opportunity readiness, or identify missing submission requirements.
          </p>
        </section>
      </main>
    </div>
  );
}
