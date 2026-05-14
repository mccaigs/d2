import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Bidworx - Evidence-backed bid intelligence",
  description:
    "Evidence-backed bid intelligence for teams that cannot afford unsupported claims.",
  openGraph: {
    title: "Bidworx - Evidence-backed bid intelligence",
    description:
      "Analyse tenders, score opportunities, map evidence, and identify compliance risk.",
    url: "https://bidworx.local",
    siteName: "Bidworx",
    locale: "en_GB",
    type: "website",
    images: [
      {
        url: "https://bidworx.local/og-image.png",
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
    images: ["https://bidworx.local/og-image.png"],
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
