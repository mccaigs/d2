"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { analyseFit } from "@/lib/api";
import type { FitResponse } from "@/lib/types";

interface FitAnalysisPanelProps {
  onClose: () => void;
}

// ---------------------------------------------------------------------------
// Inline markdown renderer — **bold** only
// ---------------------------------------------------------------------------

function renderInline(text: string) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return <span key={i}>{part}</span>;
  });
}

// ---------------------------------------------------------------------------
// Colour helpers — honest thresholds
//   0–40  muted red    clear weakness
//  41–60  amber        neutral / not central
//  61–80  soft green   relevant, good
//  81–100 strong green high-confidence match
// ---------------------------------------------------------------------------

function scoreColor(score: number) {
  if (score >= 81) return "text-emerald-700";
  if (score >= 61) return "text-emerald-600";
  if (score >= 41) return "text-amber-600";
  return "text-rose-600";
}

function barTrack(score: number) {
  if (score >= 81) return "bg-emerald-600/20";
  if (score >= 61) return "bg-emerald-500/20";
  if (score >= 41) return "bg-amber-500/20";
  return "bg-rose-500/20";
}

function barFill(score: number) {
  if (score >= 81) return "bg-emerald-600/55";
  if (score >= 61) return "bg-emerald-500/45";
  if (score >= 41) return "bg-amber-500/50";
  return "bg-rose-500/45";
}

function confidenceColor(level: string) {
  if (level === "high") return "text-emerald-700";
  if (level === "medium") return "text-amber-600";
  return "text-stone-500";
}

// ---------------------------------------------------------------------------
// Evidence tag — derived from backend scoring signals
// ---------------------------------------------------------------------------

const EVIDENCE_CONFIG: Record<
  string,
  { label: string; className: string }
> = {
  direct: {
    label: "Direct evidence",
    className:
      "bg-emerald-50 text-emerald-700 border border-emerald-200/70",
  },
  strong_adjacent: {
    label: "Strong adjacent evidence",
    className: "bg-sky-50 text-sky-700 border border-sky-200/70",
  },
  partial_inference: {
    label: "Partial inference",
    className: "bg-stone-100 text-stone-500 border border-stone-200/70",
  },
  not_central: {
    label: "Not central to this role",
    className: "bg-stone-50 text-stone-400 border border-stone-200/50",
  },
};

function EvidenceTag({ evidence }: { evidence: string }) {
  const config = EVIDENCE_CONFIG[evidence];
  if (!config) return null;
  return (
    <span
      className={`inline-flex items-center text-[10px] leading-none px-2 py-0.5 rounded-full font-medium tracking-wide ${config.className}`}
    >
      {config.label}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Gap tier helpers — recruiter-facing language
// ---------------------------------------------------------------------------

function gapTierLabel(tier?: string): string {
  if (tier === "hard") return "Worth confirming at interview";
  if (tier === "soft") return "Experience may need validating in this area";
  return "Would be useful to explore";
}

function gapTierColor(tier?: string): string {
  if (tier === "hard") return "text-rose-500/80";
  if (tier === "soft") return "text-amber-600/70";
  return "text-stone-400";
}

// ---------------------------------------------------------------------------
// Breakdown config
// ---------------------------------------------------------------------------

const BREAKDOWN_LABELS: Record<string, string> = {
  technical: "Technical",
  applied_ai: "Applied AI",
  product_architecture: "Product / Architecture",
  domain: "Domain",
  seniority: "Seniority",
};

const BREAKDOWN_ORDER = [
  "technical",
  "applied_ai",
  "product_architecture",
  "domain",
  "seniority",
] as const;

const ROLE_TYPE_LABELS: Record<string, string> = {
  solution_architect: "Solution Architect",
  ai_engineering: "AI Engineering",
  fullstack: "Full-Stack",
  general_tech: "General Tech",
};

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export function FitAnalysisPanel({ onClose }: FitAnalysisPanelProps) {
  const [jd, setJd] = useState("");
  const [result, setResult] = useState<FitResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Triggers the score bar entrance animation after the result DOM renders
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    if (result) {
      const t = setTimeout(() => setAnimated(true), 60);
      return () => clearTimeout(t);
    } else {
      setAnimated(false);
    }
  }, [result]);

  async function handleAnalyse() {
    if (!jd.trim() || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await analyseFit(jd);
      setResult(res);
    } catch {
      setError(
        "Analysis failed. Please check the API is running and try again."
      );
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

      <div className="flex-1 px-6 py-6 max-w-3xl mx-auto w-full">
        {/* Input state */}
        {!result && (
          <div className="space-y-3">
            <p className="text-sm text-stone-500 leading-relaxed">
              Paste the full job description below. You&apos;ll get a
              recruiter-facing fit summary with strengths, honest gaps,
              relevant projects, and interview talking points.
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
          <div className="space-y-10 pb-8">

            {/* ── 1. Hero: Overall Score ── */}
            <div className="text-center pt-2">
              <p
                className={`text-7xl font-serif font-semibold tabular-nums leading-none ${scoreColor(result.overall_score)}`}
              >
                {result.overall_score}
              </p>
              <p className="text-[11px] text-stone-400 uppercase tracking-widest mt-2">
                out of 100
              </p>
              <p className="font-serif text-stone-800 text-2xl mt-4 leading-snug">
                {result.fit_label}
              </p>
              <p className="text-xs text-stone-400 mt-2 leading-relaxed">
                Deterministic score — role-adaptive weighting
                {result.role_type && ROLE_TYPE_LABELS[result.role_type]
                  ? `, calibrated for ${ROLE_TYPE_LABELS[result.role_type]}`
                  : ""}
              </p>
            </div>

            {/* ── 2. Confidence ── */}
            {result.confidence && (
              <div className="space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-stone-400 uppercase tracking-widest font-medium">
                    Confidence
                  </span>
                  <span
                    className={`text-xs font-semibold capitalize ${confidenceColor(result.confidence)}`}
                  >
                    {result.confidence}
                  </span>
                </div>
                {result.confidence_reason && (
                  <p className="text-xs text-stone-500 leading-relaxed">
                    {result.confidence_reason.charAt(0).toUpperCase() +
                      result.confidence_reason.slice(1)}
                    {result.confidence_reason.endsWith(".") ? "" : "."}
                  </p>
                )}
              </div>
            )}

            {/* ── 3. Score Breakdown ── */}
            {result.breakdown && (
              <div className="space-y-3">
                <div className="flex items-baseline gap-1.5 flex-wrap">
                  <p className="text-[11px] text-stone-400 uppercase tracking-widest font-medium">
                    Score breakdown
                  </p>
                  {result.role_type && ROLE_TYPE_LABELS[result.role_type] && (
                    <p className="text-[11px] text-stone-400">
                      · {ROLE_TYPE_LABELS[result.role_type]} role
                    </p>
                  )}
                </div>

                <div className="space-y-4">
                  {BREAKDOWN_ORDER.map((key, i) => {
                    const value =
                      result.breakdown[key as keyof typeof result.breakdown];
                    const evidence =
                      result.dimension_evidence?.[
                        key as keyof typeof result.dimension_evidence
                      ];
                    const weight =
                      result.dimension_weights?.[
                        key as keyof typeof result.dimension_weights
                      ] ?? 0.25;

                    // De-emphasise dimensions that are not central and carry
                    // minimal weight for this role type (e.g. Applied AI for SA)
                    const isDimmed = evidence === "not_central" && weight <= 0.10;

                    return (
                      <div
                        key={key}
                        className={`transition-opacity duration-500 ${isDimmed ? "opacity-45" : ""}`}
                      >
                        {/* Bar row */}
                        <div className="flex items-center gap-3">
                          <span className="text-xs text-stone-600 w-36 shrink-0">
                            {BREAKDOWN_LABELS[key]}
                          </span>
                          <div
                            className={`flex-1 h-1.5 rounded-full ${barTrack(value)} overflow-hidden`}
                          >
                            <div
                              className={`h-full rounded-full ${barFill(value)} transition-[width] duration-700 ease-out`}
                              style={{
                                width: animated ? `${value}%` : "0%",
                                transitionDelay: `${i * 100}ms`,
                              }}
                            />
                          </div>
                          <span
                            className={`text-xs font-semibold tabular-nums w-7 text-right ${scoreColor(value)}`}
                          >
                            {value}
                          </span>
                        </div>

                        {/* Evidence tag */}
                        {evidence && (
                          <div className="mt-1 pl-36">
                            <EvidenceTag evidence={evidence} />
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* ── 4. Hiring Summary ── */}
            {result.summary && (
              <div className="space-y-2.5">
                <p className="text-[11px] text-stone-400 uppercase tracking-widest font-medium">
                  Hiring summary
                </p>
                <div className="space-y-3">
                  {result.summary.split(/\n{2,}/).map((para, i) => (
                    <p
                      key={i}
                      className="text-sm text-stone-700 leading-relaxed"
                    >
                      {renderInline(para)}
                    </p>
                  ))}
                </div>
              </div>
            )}

            {/* ── 5. Strengths ── */}
            {result.strengths.length > 0 && (
              <div className="space-y-2.5">
                <p className="text-[11px] text-stone-400 uppercase tracking-widest font-medium">
                  Strengths
                </p>
                <div className="space-y-2">
                  {result.strengths.map((s, i) => (
                    <div key={i} className="flex gap-2.5 py-0.5">
                      <span className="text-emerald-600 shrink-0 mt-0.5 text-xs font-semibold">
                        ✓
                      </span>
                      <p className="text-sm text-stone-700 leading-relaxed">
                        {s}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ── 6. Areas to explore at interview ── */}
            {result.gaps.length > 0 && (
              <div className="space-y-2.5">
                <p className="text-[11px] text-stone-400 uppercase tracking-widest font-medium">
                  Areas to explore at interview
                </p>
                <div className="space-y-4">
                  {result.gaps.map((g, i) => (
                    <div key={i}>
                      <div className="flex items-baseline gap-2 flex-wrap">
                        <p className="text-sm font-medium text-stone-800">
                          {g.area}
                        </p>
                        <span
                          className={`text-[10px] font-medium ${gapTierColor(g.tier)}`}
                        >
                          · {gapTierLabel(g.tier)}
                        </span>
                      </div>
                      <p className="text-xs text-stone-500 mt-1 leading-relaxed">
                        {g.note}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ── 7. Relevant projects ── */}
            {result.relevant_projects.length > 0 && (
              <div className="space-y-2.5">
                <p className="text-[11px] text-stone-400 uppercase tracking-widest font-medium">
                  Relevant projects
                </p>
                <div className="space-y-4">
                  {result.relevant_projects.map((p, i) => (
                    <div key={i}>
                      <p className="text-sm font-medium text-stone-800">
                        {p.name}
                      </p>
                      <p className="text-xs text-stone-500 mt-0.5 leading-relaxed">
                        {p.reason}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ── 8. Interview talking points ── */}
            {result.talking_points.length > 0 && (
              <div className="space-y-2.5">
                <p className="text-[11px] text-stone-400 uppercase tracking-widest font-medium">
                  Interview talking points
                </p>
                <div className="space-y-2.5">
                  {result.talking_points.map((pt, i) => (
                    <div
                      key={i}
                      className="flex gap-2.5 text-sm text-stone-700 leading-relaxed"
                    >
                      <span className="text-amber-500 shrink-0 mt-0.5 text-xs">
                        —
                      </span>
                      <p>{pt}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ── CTA: strong match bridge ── */}
            {result.overall_score >= 70 &&
              (result.confidence === "high" ||
                result.confidence === "medium") && (
                <div className="rounded-xl border border-stone-200 bg-white px-5 py-4">
                  <p className="text-sm text-stone-700 leading-relaxed">
                    This looks like a strong match. Want David to take a
                    closer look at this role?
                  </p>
                  <Link
                    href="/contact?intent=fit_analysis"
                    className="mt-3 inline-flex items-center gap-1.5 text-sm font-medium text-amber-900 transition-colors hover:text-amber-700"
                  >
                    <span>Start a conversation</span>
                    <ArrowUpRight className="h-3.5 w-3.5" />
                  </Link>
                </div>
              )}

            {/* ── Reset ── */}
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
