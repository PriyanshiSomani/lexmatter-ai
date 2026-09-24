import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LexMatter AI — Legal-Matter Intelligence Platform",
  description: "Agentic Legal-Matter Intelligence & Proof Verification Platform for Attorneys",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-slate-100">{children}</body>
    </html>
  );
}
