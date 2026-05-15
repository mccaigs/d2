import type { Metadata } from "next";
import "./globals.css";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://bidworx.example";
const ogImageUrl = `${siteUrl.replace(/\/$/, "")}/og-image.png`;

export const metadata: Metadata = {
  title: "Bidworx - Evidence-backed bid intelligence",
  description:
    "Evidence-backed bid intelligence for teams that cannot afford unsupported claims.",
  openGraph: {
    title: "Bidworx - Evidence-backed bid intelligence",
    description:
      "Analyse tenders, score opportunities, map evidence, and identify compliance risk.",
    url: siteUrl,
    siteName: "Bidworx",
    locale: "en_GB",
    type: "website",
    images: [
      {
        url: ogImageUrl,
        width: 1200,
        height: 630,
        alt: "Bidworx - Evidence-backed bid intelligence",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Bidworx - Evidence-backed bid intelligence",
    description:
      "Analyse tenders, score opportunities, map evidence, and identify compliance risk.",
    images: [ogImageUrl],
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
