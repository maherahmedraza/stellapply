import type { Metadata } from "next";
import Link from "next/link";
import { ArrowLeft, Rocket, Mail, Lock, ArrowRight, Github } from "lucide-react";
import { SketchButton, SketchCard, SketchInput } from "@/components/ui/hand-drawn";
import { Kalam, Patrick_Hand } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/navbar";

const kalam = Kalam({
  weight: ["700"],
  subsets: ["latin"],
  variable: "--font-marker",
});

const patrickHand = Patrick_Hand({
  weight: ["400"],
  subsets: ["latin"],
  variable: "--font-handwritten",
});

export const metadata: Metadata = {
  title: "Stellapply | Sketch Your Career Path",
  description: "Ditch the corporate grind. Stellapply uses AI to auto-sketch your resumes and apply to jobs with a human, hand-drawn touch.",
  keywords: ["AI Resumes", "Job Automation", "Hand-Drawn UI", "Career Sketching", "ATS Bypass"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body
        className={`${kalam.variable} ${patrickHand.variable} antialiased min-h-screen bg-paper-bg dark:bg-background overflow-x-hidden`}
      >
        <Navbar />
        <main className="relative z-10 pt-24 md:pt-32">
          {children}
        </main>
      </body>
    </html>
  );
}
