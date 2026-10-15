import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MemoScan AI — Marks Memo Extraction & Academic Analytics",
  description: "Automated student marks memo extraction, verification, academic analytics, and consolidated Excel generation.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full bg-slate-50 text-slate-900">{children}</body>
    </html>
  );
}
