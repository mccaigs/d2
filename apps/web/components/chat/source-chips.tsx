"use client";

import type { SourceChip } from "@/lib/types";

interface SourceChipsProps {
  sources: SourceChip[];
}

const CATEGORY_STYLES: Record<string, string> = {
  skills: "bg-sky-50 text-sky-700 border-sky-200",
  projects: "bg-violet-50 text-violet-700 border-violet-200",
  experience: "bg-emerald-50 text-emerald-700 border-emerald-200",
  profile: "bg-amber-50 text-amber-700 border-amber-200",
  achievements: "bg-rose-50 text-rose-700 border-rose-200",
  faq: "bg-stone-100 text-stone-600 border-stone-200",
};

const DEFAULT_STYLE = "bg-stone-100 text-stone-600 border-stone-200";

export function SourceChips({ sources }: SourceChipsProps) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-1.5 mt-4">
      {sources.map((source, i) => (
        <span
          key={i}
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium border tracking-wide ${
            CATEGORY_STYLES[source.category] ?? DEFAULT_STYLE
          }`}
        >
          {source.label}
        </span>
      ))}
    </div>
  );
}
