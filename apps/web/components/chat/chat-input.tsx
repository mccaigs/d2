"use client";

import { useState, useRef, type FormEvent, type KeyboardEvent } from "react";
import { Send } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function submit() {
    const trimmed = value.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setValue("");
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.focus();
    }
  }

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    submit();
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      submit();
    }
  }

  function handleInput() {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  }

  const canSend = value.trim().length > 0 && !isLoading;

  return (
    <div className="border-t border-[#1E3A5F] bg-[#07111F]/95 px-4 py-4 backdrop-blur-sm">
      <div className="mx-auto max-w-3xl">
        <form
          onSubmit={handleSubmit}
          className="flex items-end gap-3 border border-[#1E3A5F] bg-[#0D1B2E] px-4 py-3 transition-colors focus-within:border-[#38BDF8]"
        >
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            onInput={handleInput}
            placeholder="Ask about a tender, evidence gap, compliance risk, or buyer requirement..."
            rows={1}
            aria-label="Message"
            className="max-h-40 min-h-[24px] flex-1 resize-none bg-transparent text-sm leading-relaxed text-[#F8FAFC] outline-none placeholder:text-[#94A3B8]"
          />
          <button
            type="submit"
            disabled={!canSend}
            aria-label="Send message"
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#38BDF8] text-[#07111F] transition-all duration-150 hover:bg-[#60A5FA] disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Send className="h-3.5 w-3.5" />
          </button>
        </form>
        <p className="mt-2 text-center text-xs text-[#94A3B8]">
          Bidworx only answers from approved procurement intelligence records.
        </p>
      </div>
    </div>
  );
}
