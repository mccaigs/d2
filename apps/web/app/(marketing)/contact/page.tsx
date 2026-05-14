import { ArrowRight } from "lucide-react";
import Link from "next/link";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";

export const metadata = {
  title: "Deploy - Bidworx",
  description:
    "Start a Bidworx procurement intelligence workflow for tender analysis and evidence mapping.",
};

const STARTING_POINTS = [
  "Analyse a tender opportunity",
  "Map evidence against buyer requirements",
  "Identify compliance and submission risks",
];

export default function ContactPage() {
  return (
    <div className="min-h-screen overflow-hidden bg-[#07111F] text-[#F8FAFC]">
      <SiteHeader />

      <main className="mx-auto max-w-6xl px-6 pb-20 pt-14 sm:px-12 sm:pt-20">
        <section className="max-w-3xl">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[#38BDF8]">
            Deploy
          </p>
          <h1 className="mt-5 text-5xl font-bold leading-[1.05] text-balance text-[#F8FAFC] sm:text-6xl">
            Start with the tender, not a blank bid response.
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-[#94A3B8]">
            Bidworx begins by structuring requirements, evidence, compliance
            risk, and readiness scoring so the response team knows what is
            supportable before drafting.
          </p>

          <div className="mt-10 grid gap-4 sm:grid-cols-3">
            {STARTING_POINTS.map((item) => (
              <div key={item} className="border border-[#1E3A5F] bg-[#0D1B2E] px-5 py-5 text-sm leading-7 text-[#CBD5E1]">
                {item}
              </div>
            ))}
          </div>

          <Link
            href="/chat"
            className="mt-10 inline-flex items-center gap-2 rounded-lg bg-[#38BDF8] px-5 py-3 text-sm font-semibold text-[#07111F] transition-colors hover:bg-[#60A5FA]"
          >
            Analyse a tender
            <ArrowRight className="h-4 w-4" />
          </Link>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
