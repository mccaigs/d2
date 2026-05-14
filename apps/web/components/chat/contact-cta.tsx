"use client";

import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import type { ChatCta } from "@/lib/types";

interface ContactCtaProps {
  cta: ChatCta;
}

export function ContactCta({ cta }: ContactCtaProps) {
  if (cta.type !== "link") return null;

  return (
    <div className="mt-5">
      <Link
        href={cta.href}
        className="inline-flex items-center gap-2 rounded-lg bg-[#22C55E] px-4 py-2 text-sm font-semibold text-[#07111F] transition-colors hover:bg-[#38BDF8]"
      >
        <span>{cta.label}</span>
        <ArrowUpRight className="h-3.5 w-3.5" />
      </Link>
    </div>
  );
}
