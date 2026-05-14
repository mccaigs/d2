import Link from "next/link";
import { ArrowRight } from "lucide-react";

export function SiteHeader() {
  return (
    <nav className="flex items-center justify-between border-b border-[#1E3A5F] bg-[#07111F]/95 px-6 py-5 sm:px-12">
      <div>
        <Link
          href="/"
          className="text-lg font-semibold text-[#F8FAFC] transition-colors hover:text-[#38BDF8]"
        >
          Bidworx
        </Link>
      </div>
      <div className="flex items-center gap-6">
        <Link
          href="/profile"
          className="hidden text-sm text-[#94A3B8] transition-colors hover:text-[#F8FAFC] sm:inline"
        >
          Platform
        </Link>
        <Link
          href="/projects"
          className="hidden text-sm text-[#94A3B8] transition-colors hover:text-[#F8FAFC] sm:inline"
        >
          Workflows
        </Link>
        <Link
          href="/contact"
          className="hidden text-sm text-[#94A3B8] transition-colors hover:text-[#F8FAFC] sm:inline"
        >
          Deploy
        </Link>
        <Link
          href="/chat"
          className="flex items-center gap-2 rounded-lg bg-[#38BDF8] px-4 py-2 text-sm font-semibold text-[#07111F] transition-colors hover:bg-[#60A5FA]"
        >
          Analyse tender
          <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>
    </nav>
  );
}
