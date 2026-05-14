"use client";

interface SuggestionCardsProps {
  prompts: string[];
  onSelect: (prompt: string) => void;
  compact?: boolean;
}

export function SuggestionCards({
  prompts,
  onSelect,
  compact = false,
}: SuggestionCardsProps) {
  return (
    <div
      className={
        compact
          ? "flex flex-wrap gap-2"
          : "grid grid-cols-1 gap-3 sm:grid-cols-2"
      }
    >
      {prompts.map((prompt, i) => (
        <button
          key={i}
          onClick={() => onSelect(prompt)}
          className={
            compact
              ? "border border-[#1E3A5F] bg-[#0D1B2E] px-3 py-1.5 text-left text-[12px] leading-snug text-[#94A3B8] transition-all duration-150 hover:border-[#38BDF8] hover:text-[#F8FAFC]"
              : "border border-[#1E3A5F] bg-[#0D1B2E] p-4 text-left text-sm leading-snug text-[#94A3B8] transition-all duration-150 hover:border-[#38BDF8] hover:bg-[#101F35] hover:text-[#F8FAFC]"
          }
        >
          {!compact && (
            <span className="mb-1.5 block text-[10px] font-semibold uppercase tracking-widest text-[#38BDF8]">
              Query
            </span>
          )}
          {prompt}
        </button>
      ))}
    </div>
  );
}
