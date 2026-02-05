"use client";

import React from "react";
import Link from "next/link";
import { useAuthStore } from "@/stores/auth.store";
import { ArrowRight, Sparkles, Zap, Target, MousePointer2, MoveDown } from "lucide-react";
import {
  Button,
  Card,
  CardContent,
  Heading,
  Text,
  Badge
} from "@/components/ui";
import {
  Header,
  Footer,
  Container,
  Section
} from "@/components/layout";
import {
  SquigglyLine,
  HandDrawnArrow,
  Sparkle,
  CornerMarks,
  PostItTag
} from "@/components/decorations/hand-drawn-elements";
import { cn } from "@/lib/utils";

export default function Home() {
  const { isAuthenticated } = useAuthStore();
  const ctaLink = isAuthenticated ? "/dashboard" : "/auth/register";
  const ctaText = isAuthenticated ? "Go to Dashboard" : "Get Started For Free";



  return (
    <div className="flex flex-col min-h-screen">
      <Header />

      <main className="flex-grow">
        {/* Hero Section */}
        <Section padding="none" className="relative pt-16 pb-20 md:pt-32 md:pb-32 overflow-hidden">
          {/* Decorative Sparkles and Squiggles */}
          <Sparkle className="absolute top-20 left-[15%] text-accent-warning animate-float" size={32} />
          <Sparkle className="absolute bottom-40 right-[15%] text-accent animate-float delay-1000" size={24} />

          <div className="absolute top-32 right-[5%] hidden lg:block opacity-40">
            <SquigglyLine className="w-64 h-24 text-accent rotate-12" />
          </div>

          <h1 className="text-6xl md:text-8xl font-marker tracking-tighter text-pencil-black mb-8 leading-[0.9] -rotate-1">
            Apply to <span className="text-ink-blue underline decoration-marker-red decoration-wavy decoration-4">10x More</span> Jobs!
          </h1>

          <p className="text-2xl md:text-3xl font-handwritten text-pencil-black/90 mb-12 max-w-2xl mx-auto leading-relaxed">
            Stop drawing blanks on applications. Stellapply uses AI to sketch perfectly tailored resumes and automate your journey.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-8 relative">
            <Link href="/auth/register">
              <SketchButton variant="accent" className="text-3xl py-6 px-12 -rotate-2">
                Start Your Journey
                <ArrowRight className="w-8 h-8 ml-2" strokeWidth={3} />
              </SketchButton>
            </Link>

            <Link href="#features">
              <div className="group cursor-pointer">
                <span className="text-2xl font-bold border-b-2 border-dashed border-pencil-black pb-1 hover:text-ink-blue transition-colors">
                  How it works?
                </span>
              </div>
            </Link>

            {/* Sketchy Arrow pointing to CTA */}
            <div className="absolute -left-20 top-1/2 -translate-y-1/2 hidden lg:block -rotate-12">
              <svg width="60" height="60" viewBox="0 0 60 60" fill="none" className="stroke-marker-red">
                <path d="M10 10 Q 30 15, 50 50 M 50 50 L 40 45 M 50 50 L 55 40" strokeWidth="4" strokeLinecap="round" />
              </svg>
              <span className="font-marker text-marker-red text-xl absolute -left-16 -top-4 whitespace-nowrap">Click here!</span>
            </div>
          </div>
        </div>

        <div className="flex justify-center mt-20 animate-bounce">
          <MoveDown className="w-10 h-10 text-pencil-black/30" strokeWidth={3} />
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-muted-paper/30 border-y-4 border-dashed border-pencil-black">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-20">
            <h2 className="text-5xl md:text-6xl font-marker mb-6 -rotate-1">Everything you need</h2>
            <div className="w-48 h-2 bg-marker-red mx-auto wobble opacity-30" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {[
              {
                title: "AI Resume Builder",
                desc: "Hand-crafted tailoring for every single job post.",
                icon: Zap,
                color: "yellow",
                rotation: "-rotate-2"
              },
              {
                title: "ATS Bypass",
                desc: "Cracking the code of corporate filters with ease.",
                icon: Target,
                color: "white",
                rotation: "rotate-1"
              },
              {
                title: "Auto-Apply",
                desc: "We do the boring legwork while you catch some z's.",
                icon: MousePointer2,
                color: "white",
                rotation: "-rotate-1"
              }
            ].map((f, i) => (
              <SketchCard
                key={i}
                color={f.color as any}
                decoration="tape"
                className={cn("h-full py-12 px-8 flex flex-col items-center text-center", f.rotation)}
              >
                <div className="w-16 h-16 wobble bg-ink-blue/10 flex items-center justify-center mb-6">
                  <f.icon className="w-10 h-10 text-ink-blue" strokeWidth={3} />
                </div>
              </PostItTag>
            </div>

            <Heading level="h1" decoration="none" className="mb-8 leading-[1.1] md:leading-[1.1]">
              Apply to <span className="wavy-underline text-marker-red dark:text-marker-red">10x More</span> Jobs <br className="hidden md:block" />
              <span className="inline-block rotate-subtle bg-background-muted dark:bg-pencil-black/40 px-4 py-1 mt-2">Without the Stress</span>
            </Heading>

      {/* Footer */}
      <footer className="mt-auto py-20 bg-pencil-black text-white border-t-8 border-marker-red">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <div className="w-16 h-16 wobble bg-white flex items-center justify-center mx-auto mb-8 -rotate-6">
            <Rocket className="w-10 h-10 text-pencil-black" strokeWidth={3} />
          </div>
          <h2 className="text-4xl font-marker mb-6">Built for winners.</h2>
          <div className="flex justify-center gap-8 font-handwritten text-xl mb-12 border-y border-white/10 py-6">
            <Link href="/privacy" className="hover:text-marker-red transition-colors">Privacy</Link>
            <Link href="/terms" className="hover:text-marker-red transition-colors">Terms</Link>
            <Link href="/support" className="hover:text-marker-red transition-colors">Support</Link>
          </div>
          <p className="font-handwritten text-white/40">© 2026 Stellapply.ai - All rights reserved (I think)</p>
        </div>
      </footer>
    </div>
  );
}
