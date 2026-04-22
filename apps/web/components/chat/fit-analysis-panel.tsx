"use client";

import { useState } from "react";
import { analyseFit } from "@/lib/api";
import type { FitResponse } from "@/lib/types";

interface FitAnalysisPanelProps {
  onClose: () => void;
}

function renderInline(text: string) {
  // Tiny markdown: **bold** only — keeps the summary deterministic and safe.
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return <span key={i}>{part}</span>;
  });
}

function scoreColor(score: number) {
  if (score >= 80) return "text-emerald-700";
  if (score >= 65) return "text-emerald-600";
  if (score >= 50) return "text-amber-700";
  return "text-stone-500";
}

function barColor(score: number) {
  if (score >= 80) return "bg-emerald-600/20";
  if (score >= 65) return "bg-emerald-500/15";
  if (score >= 50) return "bg-amber-600/15";
  return "bg-stone-400/15";
}

function barFill(score: number) {
  if (score >= 80) return "bg-emerald-600/50";
  if (score >= 65) return "bg-emerald-500/40";
  if (score >= 50) return "bg-amber-600/40";
  return "bg-stone-400/30";
}

function confidenceColor(level: string) {
  if (level === "high") return "text-emerald-700";
  if (level === "medium") return "text-amber-700";
  return "text-stone-500";
}

const BREAKDOWN_LABELS: Record<string, string> = {
  technical: "Technical",
  applied_ai: "Applied AI",
  product_architecture: "Product / Architecture",
  domain: "Domain",
  seniority: "Seniority",
};

const BREAKDOWN_ORDER: (keyof typeof BREAKDOWN_LABELS)[] = [
  "technical",
  "applied_ai",
  "product_architecture",
  "domain",
  "seniority",
];

export function FitAnalysisPanel({ onClose }: FitAnalysisPanelProps) {
  const [jd, setJd] = useState("");
  const [result, setResult] = useState<FitResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyse() {
    if (!jd.trim() || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await analyseFit(jd);
      setResult(res);
    } catch {
      setError("Analysis failed. Please check the API is running and try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-stone-200 shrink-0">
        <div>
          <p className="text-xs text-stone-400 uppercase tracking-widest font-medium mb-0.5">
            Fit Analysis
          </p>
          <h2 className="font-serif text-stone-900 text-lg leading-tight">
            Paste a job description
          </h2>
        </div>
        <button
          onClick={onClose}
          className="text-xs text-stone-400 hover:text-stone-700 transition-colors border border-stone-200 rounded-lg px-3 py-1.5"
        >
          ← Back to chat
        </button>
      </div>

      <div className="flex-1 px-6 py-6 space-y-6 max-w-3xl mx-auto w-full">
        {/* Input area */}
        {!result && (
          <div className="space-y-3">
            <p className="text-sm text-stone-500 leading-relaxed">
              Paste the full job description below. You&apos;ll get a recruiter-
              facing fit summary with strengths, honest gaps, relevant projects,
              and interview talking points.
            </p>
            <textarea
              value={jd}
              onChange={(e) => setJd(e.target.value)}
              placeholder="Paste job description here…"
              rows={10}
              className="w-full resize-none bg-white border border-stone-200 rounded-xl px-4 py-3 text-sm text-stone-800 placeholder:text-stone-400 leading-relaxed outline-none focus:border-stone-400 transition-colors"
            />
            {error && <p className="text-xs text-rose-600">{error}</p>}
            <button
              onClick={handleAnalyse}
              disabled={!jd.trim() || loading}
              className="px-5 py-2.5 text-sm bg-stone-800 text-white rounded-xl hover:bg-stone-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-150"
            >
              {loading ? "Analysing…" : "Analyse fit"}
            </button>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-7">
            {/* Overall score + label */}
            <div className="flex items-start gap-5 p-5 bg-white border border-stone-200 rounded-2xl">
              <div className="text-center shrink-0">
                <p className={`text-4xl font-serif font-semibold tabular-nums ${scoreColor(result.overall_score)}`}>
                  {result.overall_score}
                </p>
                <p className="text-xs text-stone-400 uppercase tracking-wider mt-0.5">/ 100</p>
              </div>
              <div>
                <p className="font-medium text-stone-900 text-base leading-snug">
                  {result.fit_label}
                </p>
                <p className="text-xs text-stone-500 mt-1 leading-relaxed">
                  Deterministic score — technical, applied AI, product/architecture,
                  domain, and seniority signals, weighted.
                </p>
              </div>
            </div>

            {/* Score breakdown */}
            {result.breakdown && (
              <div className="space-y-2">
                <p className="text-[11px] text-stone-400 uppercase tracking-widest font-medium">
                  Score breakdown
                </p>
                <div className="space-y-1.5">
                  {BREAKDOWN_ORDER.map((key) => {
                    const value = result.breakdown[key as keyof typeof result.breakdown];
                    return (
                      <div key={key} className="flex items-center gap-3">
                        <span className="text-xs text-stone-600 w-[140px] shrink-0 tabular-nums">
                          {BREAKDOWN_LABELS[key]}
                        </span>
                        <div className={`flex-1 h-1.5 rounded-full ${barColor(value)} overflow-hidden`}>
                          <div
                            className={`h-full rounded-full ${barFill(value)} transition-all duration-500 ease-out`}
                            style={{ width: `${value}%` }}
                          />
                        </div>
                        <span className={`text-xs font-medium tabular-nums w-7 text-right ${scoreColor(value)}`}>
                          {value}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Confidence indicator */}
            {result.confidence && (
              <div className="flex items-baseline gap-1.5">
                <span className="text-[11px] text-stone-400 uppercase tracking-widest font-medium">
                  Confidence:
                </span>
                <span className={`text-xs font-medium capitalize ${confidenceColor(result.confidence)}`}>
                  {result.confidence}
                </span>
                {result.confidence_reason && (
                  <span className="text-xs text-stone-400">
                    — {result.confidence_reason.charAt(0).toLowerCase() + result.confidence_reason.slice(1)}
                  </span>
                )}
              </div>
            )}

            {/* Summary */}
            {result.summary && (
              <div className="space-y-2">
                <p className="text-[11px] text-stone-400 uppercase tracking-widest font-medium">
                  Hiring summary
                </p>
                <div className="bg-white border border-stone-200 rounded-2xl p-5 space-y-3">
                  {result.summary.split(/\n{2,}/).map((para, i) => (
                    <p key={i} className="text-sm text-stone-700 leading-relaxed">
                      {renderInline(para)}
                    </p>
                  ))}
                </div>
              </div>
            )}

            {/* Strengths */}
            {result.strengths.length > 0 && (
              <div className="space-y-2">
                <p className="text-[11px] text-stone-400 uppercase tracking-widest font-medium">
                  Strengths matched
                </p>
                <div className="space-y-2">
                  {result.strengths.map((s, i) => (
                    <div
                      key={i}
                      className="flex gap-3 bg-white border border-stone-200 rounded-xl px-4 py-3"
                    >
                      <span className="text-emerald-600 shrink-0 mt-0.5">✓</span>
                      <p className="text-sm text-stone-700 leading-relaxed">{s}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Gaps */}
            {result.gaps.length > 0 && (
              <div className="space-y-2">
                <p className="text-[11px] text-stone-400 uppercase tracking-widest font-medium">
                  Honest gaps
                </p>
                <div className="space-y-2">
                  {result.gaps.map((g, i) => (
                    <div
                      key={i}
                      className="bg-white border border-stone-200 rounded-xl px-4 py-3 border-l-2 border-l-amber-400"
                    >
                      <p className="text-sm font-medium text-stone-800">{g.area}</p>
                      <p className="text-xs text-stone-600 mt-1 leading-relaxed">
                        {g.note}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Relevant projects */}
            {result.relevant_projects.length > 0 && (
              <div className="space-y-2">
                <p className="text-[11px] text-stone-400 uppercase tracking-widest font-medium">
                  Relevant projects
                </p>
                <div className="space-y-2">
                  {result.relevant_projects.map((p, i) => (
                    <div key={i} className="bg-white border border-stone-200 rounded-xl px-4 py-3">
                      <p className="text-sm font-medium text-stone-800">{p.name}</p>
                      <p className="text-xs text-stone-500 mt-1 leading-relaxed">
                        {p.reason}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Talking points */}
            {result.talking_points.length > 0 && (
              <div className="space-y-2">
                <p className="text-[11px] text-stone-400 uppercase tracking-widest font-medium">
                  Interview talking points
                </p>
                <div className="space-y-2">
                  {result.talking_points.map((pt, i) => (
                    <div key={i} className="flex gap-3 text-sm text-stone-700 leading-relaxed">
                      <span className="text-amber-500 shrink-0 mt-0.5">—</span>
                      <p>{pt}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Reset */}
            <button
              onClick={() => {
                setResult(null);
                setJd("");
              }}
              className="text-xs text-stone-400 hover:text-stone-700 transition-colors underline underline-offset-2"
            >
              Analyse another job description
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
