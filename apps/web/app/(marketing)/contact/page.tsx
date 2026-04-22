import Link from "next/link";
import { ArrowLeft, Mail, MessageSquare } from "lucide-react";

export const metadata = {
  title: "Contact — David Robertson",
  description: "Get in touch with David Robertson for role discussions, project opportunities, or general inquiries.",
};

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-[#faf8f0] text-stone-900">
      <nav className="flex items-center justify-between px-6 sm:px-12 py-5 border-b border-stone-200">
        <Link href="/" className="flex items-center gap-2 text-sm text-stone-500 hover:text-stone-800 transition-colors">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to home</span>
        </Link>
      </nav>

      <main className="max-w-3xl mx-auto px-6 sm:px-12 py-16">
        <h1 className="font-serif text-4xl sm:text-5xl text-stone-900 mb-6">
          Get in Touch
        </h1>
        <p className="text-stone-600 text-lg leading-relaxed mb-12">
          Open to senior AI engineering, architecture, and product engineering roles. 
          Particularly interested in positions where applied AI, systems design, and 
          end-to-end delivery overlap.
        </p>

        <div className="space-y-6">
          <div className="p-6 bg-[#fdfcf8] border border-stone-200 rounded-2xl">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center shrink-0">
                <MessageSquare className="w-5 h-5 text-amber-700" />
              </div>
              <div className="flex-1">
                <h2 className="font-serif text-xl text-stone-900 mb-2">
                  Use the Profile Assistant
                </h2>
                <p className="text-stone-600 leading-relaxed mb-4">
                  Ask questions about skills, experience, projects, and role fit. 
                  The assistant provides grounded answers from structured professional data.
                </p>
                <Link
                  href="/chat"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-stone-900 text-stone-50 rounded-xl text-sm font-medium hover:bg-stone-800 transition-colors"
                >
                  Open assistant
                </Link>
              </div>
            </div>
          </div>

          <div className="p-6 bg-[#fdfcf8] border border-stone-200 rounded-2xl">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center shrink-0">
                <Mail className="w-5 h-5 text-amber-700" />
              </div>
              <div className="flex-1">
                <h2 className="font-serif text-xl text-stone-900 mb-2">
                  Send an Email
                </h2>
                <p className="text-stone-600 leading-relaxed mb-4">
                  For direct conversations about roles, projects, or collaboration opportunities.
                </p>
                <a
                  href="mailto:hello@davidrobertson.pro"
                  className="inline-flex items-center gap-2 px-4 py-2 border border-stone-300 text-stone-700 rounded-xl text-sm font-medium hover:border-stone-500 transition-colors"
                >
                  hello@davidrobertson.pro
                </a>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-12 p-6 bg-stone-50 border border-stone-200 rounded-2xl">
          <h3 className="font-serif text-lg text-stone-900 mb-3">
            What to expect
          </h3>
          <ul className="space-y-2 text-sm text-stone-600">
            <li className="flex gap-2">
              <span className="text-amber-600/70 mt-0.5 shrink-0">—</span>
              <span>Responses typically within 24-48 hours</span>
            </li>
            <li className="flex gap-2">
              <span className="text-amber-600/70 mt-0.5 shrink-0">—</span>
              <span>Open to discussing senior AI and architecture roles</span>
            </li>
            <li className="flex gap-2">
              <span className="text-amber-600/70 mt-0.5 shrink-0">—</span>
              <span>Based in Scotland, UK — open to remote, hybrid, or relocation discussions</span>
            </li>
          </ul>
        </div>
      </main>
    </div>
  );
}
