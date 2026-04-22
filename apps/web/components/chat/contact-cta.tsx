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
        className="inline-flex items-center gap-2 rounded-full bg-amber-50 px-4 py-2 text-sm font-medium text-amber-900 transition-colors hover:bg-amber-100"
      >
        <span>{cta.label}</span>
        <ArrowUpRight className="h-3.5 w-3.5" />
      </Link>
    </div>
  );
}
