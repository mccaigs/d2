"use client";

import { useState } from "react";
import { Mail, Send, ArrowUpRight } from "lucide-react";
import { CONTACT_EMAIL } from "@/lib/constants";

/**
 * Premium inline CTA shown when the backend flags a high-intent conversion
 * signal (e.g. "What are David's day rates?" or "How do I contact David?").
 *
 * Deliberately restrained: opens an optional lightweight form that composes
 * a well-structured email to David. No separate backend endpoint required.
 */
export function ContactCta() {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [company, setCompany] = useState("");
  const [brief, setBrief] = useState("");
  const [timeline, setTimeline] = useState("");
  const [budget, setBudget] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const subject = encodeURIComponent(
      `Project enquiry${company ? ` — ${company}` : ""}`
    );
    const body = encodeURIComponent(
      [
        `Name: ${name}`,
        `Email: ${email}`,
        company ? `Company: ${company}` : null,
        "",
        "What we need built:",
        brief,
        "",
        timeline ? `Timeline: ${timeline}` : null,
        budget ? `Budget: ${budget}` : null,
      ]
        .filter(Boolean)
        .join("\n")
    );
    window.location.href = `mailto:${CONTACT_EMAIL}?subject=${subject}&body=${body}`;
  };

  return (
    <div className="mt-6 rounded-2xl border border-amber-200/70 bg-[#fdfcf4] p-5 sm:p-6">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 w-9 h-9 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center shrink-0">
          <Mail className="w-4 h-4 text-amber-700" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-serif text-lg text-stone-900 leading-tight">
            Discuss a project with David
          </h3>
          <p className="mt-1 text-sm text-stone-600 leading-relaxed">
            Share a short outline of the scope, timeline, and goals. David
            reads every enquiry personally and typically replies within 24–48
            hours.
          </p>

          {!open ? (
            <div className="mt-4 flex flex-wrap items-center gap-2">
              <button
                onClick={() => setOpen(true)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-stone-900 text-stone-50 text-sm font-medium hover:bg-stone-800 transition-colors"
              >
                <Send className="w-3.5 h-3.5" />
                Start a project brief
              </button>
              <a
                href={`mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(
                  "Project enquiry"
                )}`}
                className="inline-flex items-center gap-1.5 text-sm text-stone-600 hover:text-stone-900 transition-colors px-3 py-2"
              >
                Or email directly
                <ArrowUpRight className="w-3.5 h-3.5" />
              </a>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="mt-4 space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Field
                  label="Name"
                  value={name}
                  onChange={setName}
                  required
                />
                <Field
                  label="Email"
                  type="email"
                  value={email}
                  onChange={setEmail}
                  required
                />
              </div>
              <Field
                label="Company (optional)"
                value={company}
                onChange={setCompany}
              />
              <Field
                label="What do you need built?"
                value={brief}
                onChange={setBrief}
                multiline
                required
              />
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Field
                  label="Timeline"
                  value={timeline}
                  onChange={setTimeline}
                  placeholder="e.g. 4 weeks, Q1 start"
                />
                <Field
                  label="Budget (optional)"
                  value={budget}
                  onChange={setBudget}
                />
              </div>
              <div className="flex items-center gap-2 pt-1">
                <button
                  type="submit"
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-stone-900 text-stone-50 text-sm font-medium hover:bg-stone-800 transition-colors"
                >
                  <Send className="w-3.5 h-3.5" />
                  Send brief
                </button>
                <button
                  type="button"
                  onClick={() => setOpen(false)}
                  className="text-sm text-stone-500 hover:text-stone-800 px-3 py-2"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

interface FieldProps {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  placeholder?: string;
  required?: boolean;
  multiline?: boolean;
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  placeholder,
  required,
  multiline,
}: FieldProps) {
  const baseCls =
    "w-full rounded-lg border border-stone-200 bg-white px-3 py-2 text-sm text-stone-800 placeholder:text-stone-400 focus:outline-none focus:border-amber-400 focus:ring-1 focus:ring-amber-200 transition-colors";
  return (
    <label className="block">
      <span className="block text-[11px] font-medium text-stone-500 uppercase tracking-wider mb-1">
        {label}
      </span>
      {multiline ? (
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          required={required}
          rows={3}
          className={baseCls}
        />
      ) : (
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          required={required}
          className={baseCls}
        />
      )}
    </label>
  );
}
