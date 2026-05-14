"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, FileSearch, ShieldAlert } from "lucide-react";
import { fetchSampleTenders } from "@/lib/api";
import type { SampleTender } from "@/lib/types";

interface SampleTenderPickerProps {
  onSelect: (sample: SampleTender) => void;
  isLoading: boolean;
}

function iconForBand(band: string) {
  if (band === "Bid-ready with checks") return CheckCircle2;
  if (band === "Review before bid") return ShieldAlert;
  return AlertTriangle;
}

function colourForBand(band: string) {
  if (band === "Bid-ready with checks") return "text-[#22C55E]";
  if (band === "Review before bid") return "text-[#F59E0B]";
  return "text-[#EF4444]";
}

export function SampleTenderPicker({ onSelect, isLoading }: SampleTenderPickerProps) {
  const [samples, setSamples] = useState<SampleTender[]>([]);
  const [loadState, setLoadState] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    let cancelled = false;

    fetchSampleTenders()
      .then((items) => {
        if (cancelled) return;
        setSamples(items);
        setLoadState("ready");
      })
      .catch(() => {
        if (cancelled) return;
        setLoadState("error");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="w-full border border-[#1E3A5F] bg-[#0D1B2E]">
      <div className="border-b border-[#1E3A5F] px-4 py-3 sm:px-5">
        <div className="flex items-center gap-2">
          <FileSearch className="h-4 w-4 text-[#38BDF8]" />
          <h2 className="text-sm font-semibold text-[#F8FAFC]">Try a sample tender</h2>
        </div>
      </div>

      {loadState === "loading" ? (
        <p className="px-4 py-4 text-sm text-[#94A3B8] sm:px-5">Loading sample tenders...</p>
      ) : null}

      {loadState === "error" ? (
        <p className="px-4 py-4 text-sm text-[#F59E0B] sm:px-5">
          Sample tenders could not be loaded. You can still paste tender text below.
        </p>
      ) : null}

      {loadState === "ready" ? (
        <div className="grid grid-cols-1 border-t border-[#1E3A5F] sm:grid-cols-3">
          {samples.map((sample) => {
            const Icon = iconForBand(sample.expected_band);
            return (
              <button
                key={sample.id}
                type="button"
                onClick={() => onSelect(sample)}
                disabled={isLoading}
                className="group flex min-h-[172px] flex-col border-b border-[#1E3A5F] px-4 py-4 text-left transition-colors hover:bg-[#101F35] disabled:cursor-not-allowed disabled:opacity-50 sm:border-b-0 sm:border-r sm:last:border-r-0"
              >
                <div className="mb-3 flex items-start justify-between gap-3">
                  <Icon className={`h-4 w-4 shrink-0 ${colourForBand(sample.expected_band)}`} />
                  <span className="border border-[#1E3A5F] px-2 py-1 text-[10px] font-semibold uppercase tracking-widest text-[#94A3B8]">
                    Run
                  </span>
                </div>
                <span className="text-sm font-semibold leading-snug text-[#F8FAFC]">
                  {sample.title}
                </span>
                <span className="mt-2 flex-1 text-xs leading-relaxed text-[#94A3B8]">
                  {sample.description}
                </span>
                <span className={`mt-4 text-xs font-medium ${colourForBand(sample.expected_band)}`}>
                  {sample.expected_band}
                </span>
              </button>
            );
          })}
        </div>
      ) : null}
    </section>
  );
}
