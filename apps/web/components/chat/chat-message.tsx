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
        <div key={index} className="flex gap-2.5 leading-relaxed text-[#CBD5E1]">
          <span className="mt-0.5 shrink-0 select-none text-[#38BDF8]">-</span>
          <span dangerouslySetInnerHTML={{ __html: formatted }} />
        </div>
      );
    }

    return (
      <p
        key={index}
        className="leading-relaxed text-[#CBD5E1]"
        dangerouslySetInnerHTML={{ __html: formatted }}
      />
    );
  });
}

function LoadingDots() {
  return (
    <div className="flex items-center gap-1 py-1">
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#38BDF8] [animation-delay:0ms]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#60A5FA] [animation-delay:150ms]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-[#22C55E] [animation-delay:300ms]" />
    </div>
  );
}

export function ChatMessageComponent({ message, onFollowUp }: ChatMessageProps) {
  if (message.role === "user") {
    return (
      <div className="mb-6 flex justify-end">
        <div className="max-w-xl border border-[#1E3A5F] bg-[#101F35] px-4 py-3 text-sm leading-relaxed text-[#F8FAFC]">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="mb-10">
      <div className="mb-3 flex items-center gap-2">
        <div className="flex h-6 w-6 shrink-0 items-center justify-center border border-[#1E3A5F] bg-[#0D1B2E]">
          <span className="text-[10px] font-bold tracking-tight text-[#38BDF8]">BX</span>
        </div>
        <span className="text-xs font-medium uppercase tracking-widest text-[#94A3B8]">
          Bidworx
        </span>
        {message.isStreaming ? (
          <span className="text-xs italic normal-case tracking-normal text-[#94A3B8]">
            analysing
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
            <p className="mb-2.5 text-[11px] font-medium uppercase tracking-widest text-[#94A3B8]">
              Next queries
            </p>
            <SuggestionCards prompts={message.followUps} onSelect={onFollowUp} compact />
          </div>
        ) : null}
      </div>
    </div>
  );
}
