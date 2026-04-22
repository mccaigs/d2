import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export const metadata = {
  title: "Profile — David Robertson",
  description: "Professional profile and background for David Robertson, AI Architect and Systems Builder.",
};

export default function ProfilePage() {
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
          Professional Profile
        </h1>
        
        <div className="prose prose-stone max-w-none">
          <section className="mb-12">
            <h2 className="font-serif text-2xl text-stone-900 mb-4">Overview</h2>
            <p className="text-stone-600 leading-relaxed mb-4">
              David Robertson is a senior AI consultant and systems builder focused on applied AI, 
              full-stack product development, architecture, and workflow automation. He is strongest 
              where product thinking, engineering delivery, and AI systems design overlap.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="font-serif text-2xl text-stone-900 mb-4">Current Positioning</h2>
            <ul className="space-y-2 text-stone-600">
              <li>Senior AI Architect</li>
              <li>Applied AI Systems Builder</li>
              <li>AI Consultant</li>
              <li>Product-minded Engineer</li>
              <li>Solutions-oriented Technical Leader</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="font-serif text-2xl text-stone-900 mb-4">Core Strengths</h2>
            <ul className="space-y-2 text-stone-600">
              <li>Applied AI systems design</li>
              <li>Python backend engineering</li>
              <li>Next.js product development</li>
              <li>Full-stack SaaS architecture</li>
              <li>Workflow automation</li>
              <li>Agentic systems thinking</li>
              <li>Product strategy and execution</li>
              <li>Rapid MVP delivery</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="font-serif text-2xl text-stone-900 mb-4">Preferred Roles</h2>
            <p className="text-stone-600 leading-relaxed mb-4">
              Open to senior AI, architecture, and product engineering roles, particularly where 
              applied AI, systems design, and end-to-end delivery overlap.
            </p>
            <ul className="space-y-2 text-stone-600">
              <li>Senior AI Engineer</li>
              <li>AI Solutions Architect</li>
              <li>Applied AI Architect</li>
              <li>AI Product Engineer</li>
              <li>Founding AI Engineer</li>
              <li>Technical Product Builder</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl text-stone-900 mb-4">Contact</h2>
            <p className="text-stone-600 leading-relaxed">
              For recruiter conversations, project discussions, or role fit questions, 
              visit the <Link href="/contact" className="text-amber-700 hover:text-amber-800 underline">contact page</Link> or 
              use the <Link href="/chat" className="text-amber-700 hover:text-amber-800 underline">profile assistant</Link>.
            </p>
          </section>
        </div>
      </main>
    </div>
  );
}
