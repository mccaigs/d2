"use client";

import { useState } from "react";
import { AlertTriangle, ArrowLeft, CheckCircle2, Gauge } from "lucide-react";
import { analyseFit } from "@/lib/api";
import type { FitResponse } from "@/lib/types";

interface FitAnalysisPanelProps {
  onClose: () => void;
}

function renderInline(text: string) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return <span key={i}>{part}</span>;
  });
}

function scoreColor(score: number) {
  if (score >= 81) return "text-[#22C55E]";
  if (score >= 61) return "text-[#38BDF8]";
  if (score >= 41) return "text-[#F59E0B]";
  return "text-[#EF4444]";
}

function barFill(score: number) {
  if (score >= 81) return "bg-[#22C55E]";
  if (score >= 61) return "bg-[#38BDF8]";
  if (score >= 41) return "bg-[#F59E0B]";
  return "bg-[#EF4444]";
}

const BREAKDOWN_LABELS: Record<string, string> = {
  technical: "Requirement coverage",
  applied_ai: "Evidence strength",
  product_architecture: "Compliance readiness",
  domain: "Delivery risk clarity",
  seniority: "Commercial fit",
};

const BREAKDOWN_ORDER = [
  "technical",
  "applied_ai",
  "product_architecture",
  "domain",
  "seniority",
] as const;

export function FitAnalysisPanel({ onClose }: FitAnalysisPanelProps) {
  const [tenderText, setTenderText] = useState("");
  const [result, setResult] = useState<FitResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyse() {
    if (!tenderText.trim() || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await analyseFit(tenderText);
      setResult(res);
    } catch {
      setError("Analysis failed. Please check the API is running and try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-full flex-col overflow-y-auto bg-[#07111F] text-[#F8FAFC]">
      <div className="flex shrink-0 items-center justify-between border-b border-[#1E3A5F] px-6 py-4">
        <div>
          <p className="mb-0.5 text-xs font-medium uppercase tracking-widest text-[#94A3B8]">
            Bid readiness
          </p>
          <h2 className="text-lg font-semibold leading-tight text-[#F8FAFC]">
            Paste tender text
          </h2>
        </div>
        <button
          onClick={onClose}
          className="inline-flex items-center gap-2 rounded-lg border border-[#1E3A5F] px-3 py-1.5 text-xs text-[#94A3B8] transition-colors hover:border-[#38BDF8] hover:text-[#F8FAFC]"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to chat
        </button>
      </div>

      <div className="mx-auto w-full max-w-3xl flex-1 px-6 py-6">
        {!result && (
          <div className="space-y-4">
            <p className="text-sm leading-relaxed text-[#94A3B8]">
              Paste the tender, RFP, or buyer requirement text. Bidworx returns
              deterministic readiness scoring, evidence gaps, compliance risks,
              and source-aware next actions.
            </p>
            <textarea
              value={tenderText}
              onChange={(e) => setTenderText(e.target.value)}
              placeholder="Paste tender requirements here..."
              rows={12}
              className="w-full resize-none border border-[#1E3A5F] bg-[#0D1B2E] px-4 py-3 text-sm leading-relaxed text-[#F8FAFC] outline-none transition-colors placeholder:text-[#94A3B8] focus:border-[#38BDF8]"
            />
            {error && <p className="text-xs text-[#EF4444]">{error}</p>}
            <button
              onClick={handleAnalyse}
              disabled={!tenderText.trim() || loading}
              className="rounded-lg bg-[#38BDF8] px-5 py-2.5 text-sm font-semibold text-[#07111F] transition-all duration-150 hover:bg-[#60A5FA] disabled:cursor-not-allowed disabled:opacity-40"
            >
              {loading ? "Analysing..." : "Score bid readiness"}
            </button>
          </div>
        )}

        {result && (
          <div className="space-y-8 pb-8">
            <div className="border border-[#1E3A5F] bg-[#0D1B2E] p-6 text-center">
              <Gauge className="mx-auto mb-3 h-7 w-7 text-[#38BDF8]" />
              <p className={`text-7xl font-semibold tabular-nums leading-none ${scoreColor(result.overall_score)}`}>
                {result.overall_score}
              </p>
              <p className="mt-2 text-[11px] uppercase tracking-widest text-[#94A3B8]">
                out of 100
              </p>
              <p className="mt-4 text-2xl font-semibold leading-snug text-[#F8FAFC]">
                {result.fit_label}
              </p>
              <p className="mt-2 text-xs leading-relaxed text-[#94A3B8]">
                Deterministic score from requirement coverage, evidence strength,
                compliance readiness, delivery risk, and commercial fit.
              </p>
            </div>

            <section className="space-y-3">
              <p className="text-[11px] font-medium uppercase tracking-widest text-[#94A3B8]">
                Score breakdown
              </p>
              {BREAKDOWN_ORDER.map((key) => {
                const value = result.breakdown[key as keyof typeof result.breakdown];
                return (
                  <div key={key} className="flex items-center gap-3">
                    <span className="w-40 shrink-0 text-xs text-[#CBD5E1]">
                      {BREAKDOWN_LABELS[key]}
                    </span>
                    <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-[#101F35]">
                      <div
                        className={`h-full ${barFill(value)}`}
                        style={{ width: `${value}%` }}
                      />
                    </div>
                    <span className={`w-8 text-right text-xs font-semibold tabular-nums ${scoreColor(value)}`}>
                      {value}
                    </span>
                  </div>
                );
              })}
            </section>

            <section className="space-y-2.5">
              <p className="text-[11px] font-medium uppercase tracking-widest text-[#94A3B8]">
                Readiness summary
              </p>
              <div className="space-y-3">
                {result.summary.split(/\n{2,}/).map((para, i) => (
                  <p key={i} className="text-sm leading-relaxed text-[#CBD5E1]">
                    {renderInline(para)}
                  </p>
                ))}
              </div>
            </section>

            {result.strengths.length > 0 && (
              <section className="space-y-2.5">
                <p className="text-[11px] font-medium uppercase tracking-widest text-[#94A3B8]">
                  Evidence-positive signals
                </p>
                {result.strengths.map((s, i) => (
                  <div key={i} className="flex gap-2.5 text-sm leading-relaxed text-[#CBD5E1]">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-[#22C55E]" />
                    <p>{s}</p>
                  </div>
                ))}
              </section>
            )}

            {result.gaps.length > 0 && (
              <section className="space-y-2.5">
                <p className="text-[11px] font-medium uppercase tracking-widest text-[#94A3B8]">
                  Compliance and evidence risks
                </p>
                {result.gaps.map((g, i) => (
                  <div key={i} className="border border-[#1E3A5F] bg-[#0D1B2E] p-4">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-[#F59E0B]" />
                      <p className="text-sm font-semibold text-[#F8FAFC]">{g.area}</p>
                    </div>
                    <p className="mt-2 text-xs leading-relaxed text-[#94A3B8]">
                      {g.note}
                    </p>
                  </div>
                ))}
              </section>
            )}

            {result.relevant_projects.length > 0 && (
              <section className="space-y-2.5">
                <p className="text-[11px] font-medium uppercase tracking-widest text-[#94A3B8]">
                  Relevant workflows
                </p>
                {result.relevant_projects.map((p, i) => (
                  <div key={i}>
                    <p className="text-sm font-semibold text-[#F8FAFC]">{p.name}</p>
                    <p className="mt-0.5 text-xs leading-relaxed text-[#94A3B8]">
                      {p.reason}
                    </p>
                  </div>
                ))}
              </section>
            )}

            {result.talking_points.length > 0 && (
              <section className="space-y-2.5">
                <p className="text-[11px] font-medium uppercase tracking-widest text-[#94A3B8]">
                  Next checks
                </p>
                {result.talking_points.map((pt, i) => (
                  <div key={i} className="flex gap-2.5 text-sm leading-relaxed text-[#CBD5E1]">
                    <span className="mt-0.5 shrink-0 text-[#38BDF8]">-</span>
                    <p>{pt}</p>
                  </div>
                ))}
              </section>
            )}

            <button
              onClick={() => {
                setResult(null);
                setTenderText("");
              }}
              className="text-xs text-[#94A3B8] underline underline-offset-2 transition-colors hover:text-[#F8FAFC]"
            >
              Analyse another tender
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
