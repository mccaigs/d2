import { Suspense } from "react";
import { ArrowRight } from "lucide-react";
import Link from "next/link";
import { SiteFooter } from "@/components/layout/site-footer";
import { SiteHeader } from "@/components/layout/site-header";
import { ContactForm } from "@/components/contact/contact-form";

export const metadata = {
  title: "Contact - David Robertson",
  description:
    "Use the contact form to discuss roles, projects, and advisory work with David Robertson.",
};

const ENGAGEMENT_NOTES = [
  "Senior AI engineering and architecture roles",
  "Short, focused MVP or workflow builds",
  "Applied AI system design and technical advisory",
];

export default function ContactPage() {
  return (
    <div className="min-h-screen overflow-hidden bg-[#faf8f0] text-stone-900">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-[28rem] bg-[radial-gradient(circle_at_top_left,_rgba(217,119,6,0.15),_transparent_48%),radial-gradient(circle_at_top_right,_rgba(120,113,108,0.12),_transparent_42%)]" />

      <SiteHeader />

      <main className="relative mx-auto max-w-6xl px-6 pb-20 pt-14 sm:px-12 sm:pt-20">
        <div className="grid gap-12 lg:grid-cols-[1.05fr_0.95fr] lg:items-start">
          <section className="max-w-2xl motion-safe:animate-fade-up">
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-stone-400">
              Contact
            </p>
            <h1 className="mt-5 font-serif text-5xl leading-[1.02] text-balance text-stone-900 sm:text-6xl">
              A calmer way to start the conversation.
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-9 text-stone-600">
              Use the form to share the role, project, or advisory brief. Keep it
              concise but specific enough to be useful: scope, timing, and what a
              good outcome looks like.
            </p>

            <div className="mt-10 grid gap-4 sm:grid-cols-3">
              {ENGAGEMENT_NOTES.map((item) => (
                <div
                  key={item}
                  className="rounded-[1.75rem] bg-[#fcfbf5] px-5 py-5 text-sm leading-7 text-stone-600 shadow-[0_14px_40px_rgba(28,25,23,0.05)]"
                >
                  {item}
                </div>
              ))}
            </div>

            <div className="mt-10 rounded-[2rem] bg-stone-900 px-6 py-6 text-stone-50 shadow-[0_20px_60px_rgba(28,25,23,0.14)] motion-safe:animate-fade-up-delayed">
              <p className="text-xs uppercase tracking-[0.28em] text-stone-400">
                Before you send
              </p>
              <p className="mt-4 max-w-xl text-base leading-8 text-stone-200">
                The strongest enquiries tend to explain the decision in front of
                you: who the work is for, what needs to ship, and where David would
                add the most leverage.
              </p>
              <div className="mt-5">
                <Link
                  href="/chat"
                  className="inline-flex items-center gap-2 text-sm font-medium text-stone-100 transition-colors hover:text-white"
                >
                  Prefer to explore fit first
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </section>

          <section className="lg:pt-6">
            <Suspense>
              <ContactForm />
            </Suspense>
          </section>
        </div>
      </main>

      <SiteFooter />
    </div>
  );
}
