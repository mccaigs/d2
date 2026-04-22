"use client";

import { useState, useTransition } from "react";
import { useSearchParams } from "next/navigation";
import { CheckCircle2, Phone, Send } from "lucide-react";
import { ConfettiBurst } from "./confetti-burst";

type ContactFormValues = {
  name: string;
  email: string;
  company: string;
  website: string;
  engagement_type: string;
  budget: string;
  message: string;
  consent: boolean;
  organisation_code: string;
};

type ContactResponse =
  | {
      ok: true;
      submittedAt: string;
      message: string;
    }
  | {
      ok: false;
      error: string;
      fieldErrors?: Record<string, string>;
    };

const INITIAL_VALUES: ContactFormValues = {
  name: "",
  email: "",
  company: "",
  website: "",
  engagement_type: "",
  budget: "",
  message: "",
  consent: false,
  organisation_code: "",
};

export function ContactForm() {
  const [values, setValues] = useState<ContactFormValues>(INITIAL_VALUES);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const searchParams = useSearchParams();

  // Pick up intent from URL params (set by chat CTA or fit analysis)
  const urlIntent = searchParams.get("intent") || "general";

  function updateField<K extends keyof ContactFormValues>(
    key: K,
    value: ContactFormValues[K]
  ) {
    setValues((current) => ({ ...current, [key]: value }));
    setFieldErrors((current) => {
      if (!current[key]) return current;
      const next = { ...current };
      delete next[key];
      return next;
    });
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    setSuccessMessage(null);

    startTransition(async () => {
      try {
        const response = await fetch("/api/contact", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            ...values,
            intent: urlIntent,
          }),
        });

        const payload = (await response.json()) as ContactResponse;
        if (!response.ok || !payload.ok) {
          setFieldErrors(payload.ok ? {} : payload.fieldErrors ?? {});
          setFormError(payload.ok ? "Could not submit the form." : payload.error);
          return;
        }

        setValues(INITIAL_VALUES);
        setFieldErrors({});
        setSuccessMessage(payload.message);
      } catch {
        setFormError("Something went wrong while sending the enquiry. Please try again.");
      }
    });
  }

  if (successMessage) {
    return (
      <div className="relative rounded-[2rem] bg-[#fcfbf5] p-8 shadow-[0_18px_60px_rgba(28,25,23,0.08)] motion-safe:animate-fade-up overflow-hidden">
        <ConfettiBurst />

        <div className="relative flex items-start gap-4">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-emerald-50 text-emerald-700">
            <CheckCircle2 className="h-5 w-5" />
          </div>
          <div className="space-y-5 flex-1">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.28em] text-stone-400">
                Received
              </p>
              <h2 className="mt-2 font-serif text-3xl leading-tight text-stone-900">
                Your message has been received.
              </h2>
              <p className="mt-3 max-w-xl text-base leading-8 text-stone-600">
                David will review it directly. If there is a fit, expect a reply within a working day.
              </p>
            </div>

            {/* Gated phone reveal — only visible after successful submission */}
            <div className="rounded-[1.5rem] bg-stone-900 px-6 py-5 text-stone-50">
              <div className="flex items-center gap-2">
                <Phone className="h-3.5 w-3.5 text-stone-400" />
                <p className="text-[11px] font-semibold uppercase tracking-[0.28em] text-stone-400">
                  Direct line — now available
                </p>
              </div>
              <p className="mt-3 text-xl font-medium tracking-wide">
                07565 840188
              </p>
              <p className="mt-1.5 text-sm text-stone-400">
                Available for a direct conversation if the brief is time-sensitive.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-[2rem] bg-[#fcfbf5] p-6 shadow-[0_18px_60px_rgba(28,25,23,0.08)] sm:p-8 motion-safe:animate-fade-up"
    >
      <div className="grid gap-5 sm:grid-cols-2">
        <Field
          label="Name"
          required
          value={values.name}
          error={fieldErrors.name}
          onChange={(value) => updateField("name", value)}
        />
        <Field
          label="Email"
          type="email"
          required
          value={values.email}
          error={fieldErrors.email}
          onChange={(value) => updateField("email", value)}
        />
        <Field
          label="Company"
          value={values.company}
          error={fieldErrors.company}
          onChange={(value) => updateField("company", value)}
        />
        <Field
          label="Website"
          value={values.website}
          error={fieldErrors.website}
          onChange={(value) => updateField("website", value)}
          placeholder="example.com"
        />
        <Field
          label="Engagement type"
          value={values.engagement_type}
          error={fieldErrors.engagement_type}
          onChange={(value) => updateField("engagement_type", value)}
          placeholder="Senior hire, MVP build, advisory"
        />
        <Field
          label="Budget"
          value={values.budget}
          error={fieldErrors.budget}
          onChange={(value) => updateField("budget", value)}
          placeholder="Optional"
        />
      </div>

      <div className="mt-5">
        <Field
          label="Message"
          required
          value={values.message}
          error={fieldErrors.message}
          onChange={(value) => updateField("message", value)}
          multiline
          rows={7}
          placeholder="Outline the role or project, timings, and the outcome you need."
        />
      </div>

      <div className="hidden" aria-hidden="true">
        <Field
          label="Organisation code"
          value={values.organisation_code}
          error={fieldErrors.organisation_code}
          onChange={(value) => updateField("organisation_code", value)}
          autoComplete="off"
          tabIndex={-1}
        />
      </div>

      <label className="mt-6 flex items-start gap-3 rounded-[1.25rem] bg-stone-50 px-4 py-4 text-sm leading-7 text-stone-600">
        <input
          type="checkbox"
          checked={values.consent}
          onChange={(event) => updateField("consent", event.target.checked)}
          className="mt-1 h-4 w-4 rounded border-stone-300 text-stone-900 focus:ring-stone-400"
        />
        <span>
          I consent to David receiving and reviewing these details so he can reply
          to this enquiry.
        </span>
      </label>
      {fieldErrors.consent ? (
        <p className="mt-2 text-sm text-rose-600">{fieldErrors.consent}</p>
      ) : null}

      {formError ? (
        <p className="mt-5 rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {formError}
        </p>
      ) : null}

      <div className="mt-7 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <p className="max-w-md text-sm leading-7 text-stone-500">
          Share enough context for a useful reply: scope, timeline, and what good
          looks like.
        </p>
        <button
          type="submit"
          disabled={isPending}
          className="inline-flex items-center justify-center gap-2 rounded-full bg-stone-900 px-5 py-3 text-sm font-medium text-stone-50 transition-colors hover:bg-stone-800 disabled:cursor-not-allowed disabled:bg-stone-400"
        >
          <Send className="h-4 w-4" />
          {isPending ? "Sending..." : "Send enquiry"}
        </button>
      </div>
    </form>
  );
}

interface FieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  error?: string;
  type?: string;
  required?: boolean;
  placeholder?: string;
  multiline?: boolean;
  rows?: number;
  autoComplete?: string;
  tabIndex?: number;
}

function Field({
  label,
  value,
  onChange,
  error,
  type = "text",
  required = false,
  placeholder,
  multiline = false,
  rows = 4,
  autoComplete,
  tabIndex,
}: FieldProps) {
  const sharedClassName =
    "w-full rounded-[1.2rem] border border-stone-200 bg-white px-4 py-3 text-sm text-stone-800 outline-none transition-colors placeholder:text-stone-400 focus:border-amber-400";

  return (
    <label className="block">
      <span className="mb-2 block text-[11px] font-semibold uppercase tracking-[0.22em] text-stone-400">
        {label}
        {required ? " *" : ""}
      </span>
      {multiline ? (
        <textarea
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder={placeholder}
          rows={rows}
          required={required}
          autoComplete={autoComplete}
          tabIndex={tabIndex}
          className={sharedClassName}
        />
      ) : (
        <input
          type={type}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          placeholder={placeholder}
          required={required}
          autoComplete={autoComplete}
          tabIndex={tabIndex}
          className={sharedClassName}
        />
      )}
      {error ? <p className="mt-2 text-sm text-rose-600">{error}</p> : null}
    </label>
  );
}
