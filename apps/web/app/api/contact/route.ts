import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";

const RATE_LIMIT_WINDOW_MS = 10 * 60 * 1000;
const RATE_LIMIT_MAX_REQUESTS = 5;

const submissionStore = new Map<string, number[]>();

type ContactBody = {
  name?: unknown;
  email?: unknown;
  company?: unknown;
  website?: unknown;
  engagement_type?: unknown;
  budget?: unknown;
  message?: unknown;
  consent?: unknown;
  organisation_code?: unknown;
  intent?: unknown;
};

const VALID_INTENTS = [
  "hire",
  "advisory",
  "mvp",
  "full_time",
  "contract",
  "general",
  "fit_analysis",
] as const;

function cleanText(value: unknown) {
  return typeof value === "string" ? value.trim() : "";
}

function validateEmail(email: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function normaliseWebsite(input: string) {
  if (!input) return "";
  const candidate = /^https?:\/\//i.test(input) ? input : `https://${input}`;
  try {
    const url = new URL(candidate);
    return url.toString();
  } catch {
    return "";
  }
}

function normaliseIntent(value: unknown): string {
  const raw = typeof value === "string" ? value.trim().toLowerCase() : "";
  if ((VALID_INTENTS as readonly string[]).includes(raw)) return raw;
  return "general";
}

function getClientKey(request: NextRequest) {
  const forwardedFor = request.headers.get("x-forwarded-for");
  if (forwardedFor) {
    return forwardedFor.split(",")[0]?.trim() || "unknown";
  }
  return request.headers.get("x-real-ip") || "unknown";
}

function isRateLimited(key: string) {
  const now = Date.now();
  const recent = (submissionStore.get(key) || []).filter(
    (timestamp) => now - timestamp < RATE_LIMIT_WINDOW_MS
  );
  submissionStore.set(key, recent);
  if (recent.length >= RATE_LIMIT_MAX_REQUESTS) {
    return true;
  }
  recent.push(now);
  submissionStore.set(key, recent);
  return false;
}

export async function POST(request: NextRequest) {
  let body: ContactBody;

  try {
    body = (await request.json()) as ContactBody;
  } catch {
    return NextResponse.json(
      { ok: false, error: "Invalid JSON payload." },
      { status: 400 }
    );
  }

  const name = cleanText(body.name);
  const email = cleanText(body.email);
  const company = cleanText(body.company);
  const rawWebsite = cleanText(body.website);
  const engagementType = cleanText(body.engagement_type);
  const budget = cleanText(body.budget);
  const message = cleanText(body.message);
  const honeypot = cleanText(body.organisation_code);
  const consent = body.consent === true;
  const intent = normaliseIntent(body.intent);

  const fieldErrors: Record<string, string> = {};

  if (honeypot) {
    return NextResponse.json(
      { ok: false, error: "Invalid submission." },
      { status: 400 }
    );
  }

  if (name.length < 2) fieldErrors.name = "Please enter your name.";
  if (!validateEmail(email)) fieldErrors.email = "Please enter a valid email address.";
  if (message.length < 20) {
    fieldErrors.message = "Please include a little more detail in your message.";
  }
  if (!consent) {
    fieldErrors.consent = "Consent is required before sending the enquiry.";
  }
  if (company.length > 120) fieldErrors.company = "Company is too long.";
  if (engagementType.length > 120) {
    fieldErrors.engagement_type = "Engagement type is too long.";
  }
  if (budget.length > 120) fieldErrors.budget = "Budget is too long.";

  const website = normaliseWebsite(rawWebsite);
  if (rawWebsite && !website) {
    fieldErrors.website = "Please enter a valid website URL.";
  }

  if (Object.keys(fieldErrors).length > 0) {
    return NextResponse.json(
      { ok: false, error: "Please correct the highlighted fields.", fieldErrors },
      { status: 400 }
    );
  }

  const clientKey = getClientKey(request);
  if (isRateLimited(clientKey)) {
    return NextResponse.json(
      {
        ok: false,
        error: "Too many submissions in a short period. Please try again shortly.",
      },
      { status: 429 }
    );
  }

  // --- Production safety ---
  // In production: missing config is a hard failure — never pretend a submission succeeded.
  // In development: log a warning and fail with a clear message.
  const webhookUrl = process.env.GOOGLE_APPS_SCRIPT_URL?.trim();
  const isProduction = process.env.NODE_ENV === "production";

  if (!webhookUrl) {
    if (isProduction) {
      console.error(
        "[CONTACT] GOOGLE_APPS_SCRIPT_URL is not configured. Submissions will fail."
      );
      return NextResponse.json(
        { ok: false, error: "Contact form is not configured. Please notify the site owner." },
        { status: 500 }
      );
    }
    // Development: warn but still fail clearly
    console.warn(
      "[CONTACT] GOOGLE_APPS_SCRIPT_URL is not set. Skipping upstream delivery in development."
    );
    return NextResponse.json(
      { ok: false, error: "Contact form is not configured (GOOGLE_APPS_SCRIPT_URL missing)." },
      { status: 500 }
    );
  }

  // Collect request metadata for the sheet
  const userAgent = request.headers.get("user-agent") || "";
  const ip = clientKey;
  const refererPage = request.headers.get("referer") || "";

  // Clean, consistently named payload matching target Google Sheets columns:
  // timestamp | name | email | company | website | engagement_type | budget |
  // message | source | intent | page | user_agent | ip | status
  const payload = {
    timestamp: new Date().toISOString(),
    name,
    email,
    company,
    website,
    engagement_type: engagementType,
    budget,
    message,
    source: "contact-form",
    intent,
    page: refererPage,
    user_agent: userAgent,
    ip,
    status: "new",
  };

  let upstream: Response;
  try {
    upstream = await fetch(webhookUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      cache: "no-store",
    });
  } catch {
    return NextResponse.json(
      { ok: false, error: "Could not forward the enquiry right now." },
      { status: 502 }
    );
  }

  if (!upstream.ok) {
    return NextResponse.json(
      { ok: false, error: "Contact destination rejected the enquiry." },
      { status: 502 }
    );
  }

  return NextResponse.json({
    ok: true,
    submittedAt: payload.timestamp,
    message: "David will review your enquiry directly. If the brief is a fit, expect a reply within a working day.",
  });
}
