"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import Link from "next/link";
import { ArrowLeft, Gauge, ScanText, ShieldCheck } from "lucide-react";
import { ChatInput } from "./chat-input";
import { ChatMessageComponent } from "./chat-message";
import { SuggestionCards } from "./suggestion-cards";
import { FitAnalysisPanel } from "./fit-analysis-panel";
import { SampleTenderPicker } from "./sample-tender-picker";
import { sendChatMessage } from "@/lib/api";
import { SUGGESTED_PROMPTS, HIRE_PROMPT, STACK_HIGHLIGHT } from "@/lib/constants";
import type { ChatMessage, SampleTender, StreamMetadata } from "@/lib/types";

function generateId() {
  return Math.random().toString(36).slice(2);
}

export function ChatShell() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showFit, setShowFit] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const isLoadingRef = useRef(false);
  const hasMessages = messages.length > 0;

  const pendingRef = useRef<string>("");
  const flushScheduledRef = useRef(false);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  const sendMessage = useCallback(async (text: string, displayText?: string) => {
    if (isLoadingRef.current) return;
    isLoadingRef.current = true;
    setIsLoading(true);

    const userMsg: ChatMessage = {
      id: generateId(),
      role: "user",
      content: displayText ?? text,
    };
    const assistantId = generateId();
    const assistantMsg: ChatMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
      isStreaming: true,
    };
    setMessages((prev) => [...prev, userMsg, assistantMsg]);

    pendingRef.current = "";
    flushScheduledRef.current = false;

    const scheduleFlush = () => {
      if (flushScheduledRef.current) return;
      flushScheduledRef.current = true;
      const run = () => {
        flushScheduledRef.current = false;
        const toAppend = pendingRef.current;
        if (!toAppend) return;
        pendingRef.current = "";
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, content: m.content + toAppend } : m
          )
        );
      };
      if (typeof window !== "undefined" && window.requestAnimationFrame) {
        window.requestAnimationFrame(run);
      } else {
        setTimeout(run, 16);
      }
    };

    const flushNow = () => {
      const toAppend = pendingRef.current;
      pendingRef.current = "";
      flushScheduledRef.current = false;
      if (!toAppend) return;
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId ? { ...m, content: m.content + toAppend } : m
        )
      );
    };

    const stop = () => {
      flushNow();
      isLoadingRef.current = false;
      setIsLoading(false);
    };

    await sendChatMessage(text, {
      onChunk: (chunk) => {
        pendingRef.current += chunk;
        scheduleFlush();
      },
      onMetadata: (meta: StreamMetadata) => {
        flushNow();
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  sources: meta.sources,
                  followUps: meta.follow_ups,
                  cta: meta.cta ?? null,
                  showContactForm: meta.show_contact_form ?? false,
                  contactReason: meta.contact_reason ?? null,
                }
              : m
          )
        );
      },
      onDone: () => {
        flushNow();
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, isStreaming: false } : m
          )
        );
        stop();
      },
      onError: (err) => {
        flushNow();
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  content: m.content || err.message,
                  isStreaming: false,
                }
              : m
          )
        );
        stop();
      },
    });

    if (isLoadingRef.current) stop();
  }, []);

  const runSampleTender = useCallback(
    (sample: SampleTender) => {
      void sendMessage(sample.text, `Sample tender: ${sample.title}`);
    },
    [sendMessage]
  );

  return (
    <div className="flex h-screen flex-col bg-[#07111F] text-[#F8FAFC]">
      <header className="flex shrink-0 items-center justify-between border-b border-[#1E3A5F] bg-[#07111F]/95 px-6 py-4 backdrop-blur-sm">
        <Link
          href="/"
          className="flex items-center gap-2 text-sm text-[#94A3B8] transition-colors hover:text-[#F8FAFC]"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Bidworx</span>
        </Link>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowFit((v) => !v)}
            className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs transition-all duration-150 ${
              showFit
                ? "border-[#38BDF8] bg-[#38BDF8] text-[#07111F]"
                : "border-[#1E3A5F] text-[#94A3B8] hover:border-[#38BDF8] hover:text-[#F8FAFC]"
            }`}
          >
            <ScanText className="h-3.5 w-3.5" />
            <span>Bid readiness</span>
          </button>
          <p className="text-xs font-medium uppercase tracking-widest text-[#94A3B8]">
            Ask Bidworx
          </p>
        </div>
      </header>

      {showFit ? (
        <div className="flex-1 overflow-y-auto">
          <FitAnalysisPanel onClose={() => setShowFit(false)} />
        </div>
      ) : (
        <>
          <main className="flex-1 overflow-y-auto">
            {!hasMessages ? (
              <div className="flex min-h-full flex-col items-center justify-center px-6 py-16">
                <div className="mb-8 flex h-14 w-14 items-center justify-center border border-[#1E3A5F] bg-[#0D1B2E]">
                  <ShieldCheck className="h-7 w-7 text-[#38BDF8]" />
                </div>
                <h1 className="mb-3 text-center text-3xl font-bold text-balance text-[#F8FAFC] sm:text-4xl">
                  Ask Bidworx
                </h1>
                <p className="mb-12 max-w-md text-center text-sm leading-relaxed text-[#94A3B8] sm:text-base">
                  Analyse tenders, buyer requirements, compliance risk,
                  evidence gaps, and bid readiness from structured procurement records.
                </p>
                <div className="w-full max-w-2xl space-y-4">
                  <SampleTenderPicker onSelect={runSampleTender} isLoading={isLoading} />

                  <SuggestionCards prompts={SUGGESTED_PROMPTS} onSelect={sendMessage} />

                  <button
                    onClick={() => sendMessage(HIRE_PROMPT)}
                    className="group flex w-full items-start gap-3 border border-[#1E3A5F] bg-[#0D1B2E] px-4 py-3 text-left transition-all duration-150 hover:border-[#22C55E]"
                  >
                    <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center border border-[#1E3A5F] bg-[#101F35]">
                      <Gauge className="h-3.5 w-3.5 text-[#22C55E]" />
                    </span>
                    <span className="flex-1">
                      <span className="block text-sm font-medium text-[#F8FAFC]">
                        Analyse this tender opportunity
                      </span>
                      <span className="mt-0.5 block text-xs leading-relaxed text-[#94A3B8]">
                        {STACK_HIGHLIGHT}
                      </span>
                    </span>
                  </button>

                  <div className="flex justify-center pt-2">
                    <button
                      onClick={() => setShowFit(true)}
                      className="flex items-center gap-2 rounded-lg border border-[#1E3A5F] bg-[#0D1B2E] px-4 py-2 text-xs text-[#94A3B8] transition-all duration-150 hover:border-[#38BDF8] hover:text-[#F8FAFC]"
                    >
                      <ScanText className="h-3.5 w-3.5" />
                      Paste tender text for readiness scoring
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="mx-auto max-w-3xl px-6 py-8">
                {messages.map((msg) => (
                  <ChatMessageComponent
                    key={msg.id}
                    message={msg}
                    onFollowUp={sendMessage}
                  />
                ))}
                <div ref={bottomRef} />
              </div>
            )}
          </main>

          <div className="shrink-0">
            <ChatInput onSend={sendMessage} isLoading={isLoading} />
          </div>
        </>
      )}
    </div>
  );
}
