"use client";

import type { ChatMessage } from "@/lib/types";
import { SourceChips } from "./source-chips";
import { SuggestionCards } from "./suggestion-cards";
import { ContactCta } from "./contact-cta";

interface ChatMessageProps {
  message: ChatMessage;
  onFollowUp: (prompt: string) => void;
}

function renderContent(content: string) {
  const lines = content.split("\n");
  return lines.map((line, index) => {
    if (!line.trim()) return <div key={index} className="h-2" />;

    const formatted = line
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*([^*]+)\*/g, "<em>$1</em>")
      .replace(/^(?:- |• )/, "");

    const isBullet = line.startsWith("- ") || line.startsWith("• ");

    if (isBullet) {
      return (
        <div key={index} className="flex gap-2.5 text-stone-700 leading-relaxed">
          <span className="mt-0.5 shrink-0 select-none text-amber-500/80">-</span>
          <span dangerouslySetInnerHTML={{ __html: formatted }} />
        </div>
      );
    }

    return (
      <p
        key={index}
        className="text-stone-700 leading-relaxed"
        dangerouslySetInnerHTML={{ __html: formatted }}
      />
    );
  });
}

function LoadingDots() {
  return (
    <div className="flex items-center gap-1 py-1">
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-amber-400/70 [animation-delay:0ms]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-amber-400/70 [animation-delay:150ms]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-amber-400/70 [animation-delay:300ms]" />
    </div>
  );
}

export function ChatMessageComponent({ message, onFollowUp }: ChatMessageProps) {
  if (message.role === "user") {
    return (
      <div className="mb-6 flex justify-end">
        <div className="max-w-xl rounded-2xl rounded-tr-sm bg-stone-800 px-4 py-3 text-sm leading-relaxed text-stone-50">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="mb-10">
      <div className="mb-3 flex items-center gap-2">
        <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-amber-200 bg-amber-100">
          <span className="text-[10px] font-bold tracking-tight text-amber-700">DR</span>
        </div>
        <span className="text-xs font-medium uppercase tracking-widest text-stone-400">
          Assistant
        </span>
        {message.isStreaming ? (
          <span className="text-xs italic normal-case tracking-normal text-stone-400">
            thinking
          </span>
        ) : null}
      </div>

      <div className="pl-8">
        {message.isStreaming && !message.content ? (
          <LoadingDots />
        ) : (
          <div className="space-y-2 text-sm">{renderContent(message.content)}</div>
        )}

        {!message.isStreaming && message.cta ? <ContactCta cta={message.cta} /> : null}

        {!message.isStreaming && message.sources && message.sources.length > 0 ? (
          <SourceChips sources={message.sources} />
        ) : null}

        {!message.isStreaming && message.followUps && message.followUps.length > 0 ? (
          <div className="mt-6">
            <p className="mb-2.5 text-[11px] font-medium uppercase tracking-widest text-stone-400">
              Explore further
            </p>
            <SuggestionCards prompts={message.followUps} onSelect={onFollowUp} compact />
          </div>
        ) : null}
      </div>
    </div>
  );
}
