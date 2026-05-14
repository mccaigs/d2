"use client";

import type { SourceChip } from "@/lib/types";

interface SourceChipsProps {
  sources: SourceChip[];
}

const CATEGORY_STYLES: Record<string, string> = {
  capabilities: "bg-[#0B2A3D] text-[#38BDF8] border-[#1E3A5F]",
  workflows: "bg-[#10243F] text-[#60A5FA] border-[#1E3A5F]",
  compliance: "bg-[#2F2112] text-[#F59E0B] border-[#5A3A12]",
  procurement: "bg-[#0F2B1B] text-[#22C55E] border-[#1B5E35]",
  product: "bg-[#101F35] text-[#F8FAFC] border-[#1E3A5F]",
  proof: "bg-[#0F2B1B] text-[#22C55E] border-[#1B5E35]",
  scoring: "bg-[#0B2A3D] text-[#38BDF8] border-[#1E3A5F]",
  architecture: "bg-[#10243F] text-[#60A5FA] border-[#1E3A5F]",
  faq: "bg-[#101F35] text-[#94A3B8] border-[#1E3A5F]",
};

const DEFAULT_STYLE = "bg-[#101F35] text-[#94A3B8] border-[#1E3A5F]";

export function SourceChips({ sources }: SourceChipsProps) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-4 flex flex-wrap gap-1.5">
      {sources.map((source, i) => (
        <span
          key={i}
          className={`inline-flex items-center border px-2.5 py-0.5 text-[11px] font-medium tracking-wide ${
            CATEGORY_STYLES[source.category] ?? DEFAULT_STYLE
          }`}
        >
          {source.label}
        </span>
      ))}
    </div>
  );
}
