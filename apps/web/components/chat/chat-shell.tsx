"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import Link from "next/link";
import { ArrowLeft, ScanText, Zap } from "lucide-react";
import { ChatInput } from "./chat-input";
import { ChatMessageComponent } from "./chat-message";
import { SuggestionCards } from "./suggestion-cards";
import { FitAnalysisPanel } from "./fit-analysis-panel";
import { sendChatMessage } from "@/lib/api";
import { SUGGESTED_PROMPTS, HIRE_PROMPT, STACK_HIGHLIGHT } from "@/lib/constants";
import type { ChatMessage, StreamMetadata } from "@/lib/types";

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

  // Buffer streamed chunks and flush them on an animation frame so we don't
  // re-render for every tiny SSE event. Keeps the reveal smooth.
  const pendingRef = useRef<string>("");
  const flushScheduledRef = useRef(false);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  const sendMessage = useCallback(async (text: string) => {
    if (isLoadingRef.current) return;
    isLoadingRef.current = true;
    setIsLoading(true);

    const userMsg: ChatMessage = { id: generateId(), role: "user", content: text };
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
        // Ensure any buffered text is visible before metadata-dependent UI shows.
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

    // Failsafe: if something swallowed the callbacks, still clear state.
    if (isLoadingRef.current) stop();
  }, []);

  return (
    <div className="flex flex-col h-screen bg-[#faf8f0]">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-stone-200 bg-[#faf8f0]/95 backdrop-blur-sm shrink-0">
        <Link
          href="/"
          className="flex items-center gap-2 text-sm text-stone-500 hover:text-stone-800 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>David Robertson</span>
        </Link>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowFit((v) => !v)}
            className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border transition-all duration-150 ${
              showFit
                ? "bg-stone-800 text-white border-stone-800"
                : "text-stone-500 border-stone-200 hover:border-stone-400 hover:text-stone-700"
            }`}
          >
            <ScanText className="w-3.5 h-3.5" />
            <span>Fit analysis</span>
          </button>
          <p className="text-xs text-stone-400 uppercase tracking-widest font-medium">
            Profile Assistant
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
              <div className="flex flex-col items-center justify-center min-h-full px-6 py-16">
                <div className="w-14 h-14 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center mb-8">
                  <span className="text-amber-800 font-serif text-xl font-semibold">DR</span>
                </div>
                <h1 className="font-serif text-3xl sm:text-4xl text-stone-900 mb-3 text-center text-balance">
                  Ask about David Robertson
                </h1>
                <p className="text-stone-500 text-sm sm:text-base text-center max-w-md leading-relaxed mb-12">
                  Ask about David&apos;s AI systems work, architecture background, technical
                  stack, project delivery, and role fit.
                </p>
                <div className="w-full max-w-2xl space-y-4">
                  <SuggestionCards prompts={SUGGESTED_PROMPTS} onSelect={sendMessage} />

                  {/* Short-project CTA — subtle but credible */}
                  <button
                    onClick={() => sendMessage(HIRE_PROMPT)}
                    className="group w-full text-left bg-white border border-stone-200 hover:border-amber-300 rounded-xl px-4 py-3 transition-all duration-150 flex items-start gap-3"
                  >
                    <span className="mt-0.5 w-7 h-7 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center shrink-0">
                      <Zap className="w-3.5 h-3.5 text-amber-700" />
                    </span>
                    <span className="flex-1">
                      <span className="block text-sm text-stone-800 font-medium">
                        Hire David for a short project or MVP build
                      </span>
                      <span className="block text-xs text-stone-500 mt-0.5 leading-relaxed">
                        {STACK_HIGHLIGHT}
                      </span>
                    </span>
                  </button>

                  <div className="flex justify-center pt-2">
                    <button
                      onClick={() => setShowFit(true)}
                      className="flex items-center gap-2 text-xs text-stone-400 hover:text-stone-600 border border-stone-200 hover:border-stone-300 rounded-lg px-4 py-2 transition-all duration-150 bg-white"
                    >
                      <ScanText className="w-3.5 h-3.5" />
                      Paste a job description for fit analysis
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="max-w-3xl mx-auto px-6 py-8">
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
