import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "David Robertson — AI Architect & Systems Builder",
  description:
    "Senior AI consultant and systems builder. Ask about David's skills, projects, experience, and role suitability.",
  openGraph: {
    title: "David Robertson — AI Architect & Systems Builder",
    description:
      "Senior AI consultant and systems builder focused on applied AI, full-stack product development, and workflow automation.",
    url: "https://davidrobertson.pro",
    siteName: "David Robertson",
    locale: "en_GB",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
