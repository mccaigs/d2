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
      // keep focus so users can continue typing straight away
      el.focus();
    }
  }

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    submit();
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    // Enter submits; Shift+Enter inserts a newline.
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
    <div className="border-t border-stone-200 bg-[#faf8f0]/95 backdrop-blur-sm px-4 py-4">
      <div className="max-w-3xl mx-auto">
        <form
          onSubmit={handleSubmit}
          className="flex items-end gap-3 bg-white border border-stone-200 rounded-2xl px-4 py-3 shadow-sm focus-within:border-stone-400 transition-colors"
        >
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            onInput={handleInput}
            placeholder="Ask about David's skills, projects, experience, or role fit…"
            rows={1}
            aria-label="Message"
            className="flex-1 resize-none bg-transparent text-stone-800 placeholder:text-stone-400 text-sm leading-relaxed outline-none min-h-[24px] max-h-40"
          />
          <button
            type="submit"
            disabled={!canSend}
            aria-label="Send message"
            className="shrink-0 w-8 h-8 rounded-xl bg-stone-800 text-white flex items-center justify-center hover:bg-stone-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-150"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
        <p className="text-center text-xs text-stone-400 mt-2">
          This assistant only answers questions about David Robertson&apos;s professional background.
        </p>
      </div>
    </div>
  );
}
