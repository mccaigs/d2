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
          : "grid grid-cols-1 sm:grid-cols-2 gap-3"
      }
    >
      {prompts.map((prompt, i) => (
        <button
          key={i}
          onClick={() => onSelect(prompt)}
          className={
            compact
              ? "px-3 py-1.5 text-[12px] text-stone-500 border border-stone-200/80 rounded-full bg-white hover:border-amber-400/60 hover:text-amber-800 hover:bg-amber-50/40 transition-all duration-150 text-left leading-snug"
              : "p-4 text-sm text-stone-600 border border-stone-200 rounded-xl bg-white hover:border-amber-400/50 hover:bg-amber-50/20 hover:text-stone-800 transition-all duration-150 text-left leading-snug"
          }
        >
          {!compact && (
            <span className="block text-amber-600/50 text-[10px] font-semibold mb-1.5 uppercase tracking-widest">
              Ask
            </span>
          )}
          {prompt}
        </button>
      ))}
    </div>
  );
}
