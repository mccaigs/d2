import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/next";
import "./globals.css";

export const metadata: Metadata = {
  title: "David Robertson — AI Architect",
  description:
    "Interactive AI-powered CV with live chat, deterministic fit analysis, and real-time evaluation.",
  openGraph: {
    title: "David Robertson — Interactive AI CV",
    description:
      "Ask questions, analyse role fit, and explore a live AI-powered CV experience.",
    url: "https://www.davidrobertson.pro",
    siteName: "David Robertson",
    locale: "en_GB",
    type: "website",
    images: [
      {
        url: "https://www.davidrobertson.pro/og-image.png",
        width: 1200,
        height: 630,
        alt: "David Robertson — Interactive AI CV",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "David Robertson — Interactive AI CV",
    description:
      "Ask questions, analyse role fit, and explore a live AI-powered CV experience.",
    images: ["https://www.davidrobertson.pro/og-image.png"],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
