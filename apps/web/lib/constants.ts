export const SITE_NAME = "Bidworx";
export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL || "https://bidworx.example";
export const SITE_DESCRIPTION =
  "Evidence-backed bid intelligence for teams that cannot afford unsupported claims.";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "/api";

export const SUGGESTED_PROMPTS = [
  "Analyse this tender opportunity",
  "What are the likely compliance risks?",
  "What evidence do we need to support this claim?",
  "Summarise the buyer requirements",
  "Score this opportunity",
  "Identify missing submission requirements",
];

export const HIRE_PROMPT = "Analyse this tender opportunity";
export const STACK_HIGHLIGHT =
  "Structured evidence + deterministic scoring + compliance risk checks.";

export const SOCIAL_LINKS = {
  github: "https://github.com/bidworx",
  linkedin: "https://linkedin.com/company/bidworx",
  twitter: "https://twitter.com/bidworx",
};
