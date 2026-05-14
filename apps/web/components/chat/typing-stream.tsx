"use client";

export function TypingStream() {
  return (
    <div className="flex gap-1 py-2">
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#38BDF8] [animation-delay:0ms]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#60A5FA] [animation-delay:150ms]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#22C55E] [animation-delay:300ms]" />
    </div>
  );
}
