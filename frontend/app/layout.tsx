import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MedConnect — Gestion de cabinet médical",
  description: "Prototype POC — données fictives uniquement",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
