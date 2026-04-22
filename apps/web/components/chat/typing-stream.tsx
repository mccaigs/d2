"use client";

export function TypingStream() {
  return (
    <div className="flex gap-1 py-2">
      <span className="w-1.5 h-1.5 rounded-full bg-stone-400 animate-bounce [animation-delay:0ms]" />
      <span className="w-1.5 h-1.5 rounded-full bg-stone-400 animate-bounce [animation-delay:150ms]" />
      <span className="w-1.5 h-1.5 rounded-full bg-stone-400 animate-bounce [animation-delay:300ms]" />
    </div>
  );
}
