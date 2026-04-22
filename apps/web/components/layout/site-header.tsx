import Link from "next/link";
import { ArrowRight } from "lucide-react";

export function SiteHeader() {
  return (
    <nav className="flex items-center justify-between px-6 sm:px-12 py-5 border-b border-stone-200">
      <div>
        <Link href="/" className="font-serif text-lg text-stone-900 hover:text-stone-700 transition-colors">
          David Robertson
        </Link>
      </div>
      <div className="flex items-center gap-6">
        <Link
          href="/profile"
          className="text-sm text-stone-600 hover:text-stone-900 transition-colors hidden sm:inline"
        >
          Profile
        </Link>
        <Link
          href="/projects"
          className="text-sm text-stone-600 hover:text-stone-900 transition-colors hidden sm:inline"
        >
          Projects
        </Link>
        <Link
          href="/contact"
          className="text-sm text-stone-600 hover:text-stone-900 transition-colors hidden sm:inline"
        >
          Contact
        </Link>
        <Link
          href="/chat"
          className="flex items-center gap-2 px-4 py-2 bg-stone-900 text-stone-50 rounded-xl text-sm font-medium hover:bg-stone-800 transition-colors"
        >
          Ask the assistant
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </nav>
  );
}
