import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import DashboardShell from "@/components/layout/DashboardShell";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
});

export const metadata: Metadata = {
  title: "BPS Analytics Platform",
  description:
    "Platform intelijen ekonomi & statistik berbasis data BPS — Overview, Ekonomi, Regional, Perdagangan, dan Metadata.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body>
        <DashboardShell>{children}</DashboardShell>
      </body>
    </html>
  );
}