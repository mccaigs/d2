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
  return lines.map((line, i) => {
    if (!line.trim()) return <div key={i} className="h-2" />;

    // Italic: *text*
    const formatted = line
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*([^*]+)\*/g, "<em>$1</em>")
      .replace(/^— /, "");

    const isBullet = line.startsWith("— ");

    if (isBullet) {
      return (
        <div key={i} className="flex gap-2.5 text-stone-700 leading-relaxed">
          <span className="text-amber-500/80 mt-0.5 shrink-0 select-none">—</span>
          <span dangerouslySetInnerHTML={{ __html: formatted }} />
        </div>
      );
    }

    return (
      <p
        key={i}
        className="text-stone-700 leading-relaxed"
        dangerouslySetInnerHTML={{ __html: formatted }}
      />
    );
  });
}

function LoadingDots() {
  return (
    <div className="flex items-center gap-1 py-1">
      <span className="w-1.5 h-1.5 rounded-full bg-amber-400/70 animate-bounce [animation-delay:0ms]" />
      <span className="w-1.5 h-1.5 rounded-full bg-amber-400/70 animate-bounce [animation-delay:150ms]" />
      <span className="w-1.5 h-1.5 rounded-full bg-amber-400/70 animate-bounce [animation-delay:300ms]" />
    </div>
  );
}

export function ChatMessageComponent({ message, onFollowUp }: ChatMessageProps) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end mb-6">
        <div className="max-w-xl px-4 py-3 bg-stone-800 text-stone-50 rounded-2xl rounded-tr-sm text-sm leading-relaxed">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="mb-10">
      <div className="flex items-center gap-2 mb-3">
        <div className="w-6 h-6 rounded-full bg-amber-100 border border-amber-200 flex items-center justify-center shrink-0">
          <span className="text-amber-700 text-[10px] font-bold tracking-tight">DR</span>
        </div>
        <span className="text-xs font-medium text-stone-400 uppercase tracking-widest">
          Assistant
        </span>
        {message.isStreaming && (
          <span className="text-xs text-stone-400 italic font-normal normal-case tracking-normal">
            — thinking
          </span>
        )}
      </div>

      <div className="pl-8">
        {message.isStreaming && !message.content ? (
          <LoadingDots />
        ) : (
          <div className="space-y-2 text-sm">
            {renderContent(message.content)}
          </div>
        )}

        {!message.isStreaming && message.showContactForm && <ContactCta />}

        {!message.isStreaming && message.sources && message.sources.length > 0 && (
          <SourceChips sources={message.sources} />
        )}

        {!message.isStreaming && message.followUps && message.followUps.length > 0 && (
          <div className="mt-6">
            <p className="text-[11px] text-stone-400 uppercase tracking-widest mb-2.5 font-medium">
              Explore further
            </p>
            <SuggestionCards
              prompts={message.followUps}
              onSelect={onFollowUp}
              compact
            />
          </div>
        )}
      </div>
    </div>
  );
}
