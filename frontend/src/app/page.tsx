"use client";

import React from "react";
import Link from "next/link";
import { useAuthStore } from "@/stores/auth.store";
import { ArrowRight, Sparkles, Zap, Target, MousePointer2, MoveDown, Rocket } from "lucide-react";
import {
  SketchButton,
  SketchCard,
  Heading,
  Text,
  Badge
} from "@/components/ui";
import {
  Navbar,
  Footer,
  Section
} from "@/components/layout";
import {
  SquigglyLine,
  Sparkle,
  PostItTag
} from "@/components/decorations/hand-drawn-elements";
import { cn } from "@/lib/utils";

export default function Home() {
  const { isAuthenticated } = useAuthStore();
  const ctaLink = isAuthenticated ? "/dashboard" : "/auth/register";
  const ctaText = isAuthenticated ? "Go to Dashboard" : "Get Started For Free";

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground selection:bg-accent/30">
      <Navbar />

      <main className="flex-grow">
        {/* Hero Section */}
        <Section className="relative pt-16 pb-20 md:pt-32 md:pb-32 overflow-hidden text-center">
          {/* Decorative Sparkles and Squiggles */}
          <Sparkle className="absolute top-20 left-[15%] text-accent-warning" size={32} />
          <Sparkle className="absolute bottom-40 right-[15%] text-accent delay-1000" size={24} />

          <div className="absolute top-32 right-[5%] hidden lg:block opacity-40">
            <SquigglyLine className="w-64 h-24 text-accent rotate-12" />
          </div>

          <div className="max-w-7xl mx-auto px-6 relative z-10">
            <div className="mb-6 flex justify-center">
              <PostItTag rotation={-2} className="bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200 border-yellow-400">
                <span className="flex items-center gap-2">
                  <Sparkles size={16} /> New: Gemini 3.0 Integration
                </span>
              </PostItTag>
            </div>

            <h1 className="text-6xl md:text-8xl font-heading tracking-tighter mb-8 leading-[0.9] -rotate-1">
              Apply to <span className="text-accent-secondary underline decoration-accent decoration-wavy decoration-4">10x More</span> Jobs!
            </h1>

            <p className="text-xl md:text-2xl font-body text-foreground/80 mb-12 max-w-2xl mx-auto leading-relaxed">
              Stop drawing blanks on applications. Stellapply uses AI to sketch perfectly tailored resumes and automate your journey.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-8 relative">
              <Link href={ctaLink}>
                <SketchButton variant="accent" className="text-2xl py-4 px-10 -rotate-2">
                  {ctaText}
                  <ArrowRight className="w-6 h-6 ml-2" strokeWidth={3} />
                </SketchButton>
              </Link>

              <Link href="#features">
                <div className="group cursor-pointer">
                  <span className="text-xl font-bold border-b-2 border-dashed border-foreground/30 pb-1 hover:text-accent-secondary transition-colors">
                    How it works?
                  </span>
                </div>
              </Link>

              {/* Sketchy Arrow pointing to CTA */}
              <div className="absolute -left-20 top-1/2 -translate-y-1/2 hidden lg:block -rotate-12 opacity-40">
                <svg width="60" height="60" viewBox="0 0 60 60" fill="none" className="stroke-accent">
                  <path d="M10 10 Q 30 15, 50 50 M 50 50 L 40 45 M 50 50 L 55 40" strokeWidth="4" strokeLinecap="round" />
                </svg>
                <span className="font-heading text-accent text-xl absolute -left-16 -top-4 whitespace-nowrap">Start here!</span>
              </div>
            </div>

            <div className="flex justify-center mt-20 animate-bounce cursor-pointer opacity-30">
              <MoveDown className="w-10 h-10" strokeWidth={3} />
            </div>
          </div>
        </Section>

        {/* Features Section */}
        <Section id="features" className="py-24 bg-background-muted/30 border-y-4 border-dashed border-border">
          <div className="max-w-5xl mx-auto px-6">
            <div className="text-center mb-20">
              <h2 className="text-5xl md:text-6xl font-heading mb-6 -rotate-1">Everything you need</h2>
              <div className="w-48 h-2 bg-accent mx-auto wobble opacity-30" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
              {[
                {
                  title: "AI Resume Builder",
                  desc: "Hand-crafted tailoring for every single job post.",
                  icon: Zap,
                  color: "white" as const,
                  rotation: "-rotate-2"
                },
                {
                  title: "ATS Bypass",
                  desc: "Cracking the code of corporate filters with ease.",
                  icon: Target,
                  color: "yellow" as const,
                  rotation: "rotate-1"
                },
                {
                  title: "Auto-Apply",
                  desc: "We do the boring legwork while you catch some z's.",
                  icon: MousePointer2,
                  color: "white" as const,
                  rotation: "-rotate-1"
                }
              ].map((f, i) => (
                <SketchCard
                  key={i}
                  color={f.color}
                  decoration="tape"
                  className={cn("h-full py-12 px-8 flex flex-col items-center text-center", f.rotation)}
                >
                  <div className="w-16 h-16 wobble bg-accent-secondary/10 flex items-center justify-center mb-6">
                    <f.icon className="w-10 h-10 text-accent-secondary" strokeWidth={3} />
                  </div>
                  <Heading level="h3" className="mb-4">{f.title}</Heading>
                  <Text className="text-foreground/70 leading-relaxed font-body text-balance">
                    {f.desc}
                  </Text>
                </SketchCard>
              ))}
            </div>
          </div>
        </Section>

        {/* Call to Action Section */}
        <Section className="py-32 relative overflow-hidden text-center">
          <div className="max-w-3xl mx-auto px-6 relative z-10">
            <Heading level="h2" className="text-5xl md:text-7xl mb-12 -rotate-1">
              Stop <span className="text-accent underline decoration-marker-red decoration-wavy">Waiting</span>, <br />
              Start Applying.
            </Heading>
            <Link href="/auth/register">
              <SketchButton variant="accent" className="text-3xl py-6 px-16 rotate-1">
                Join Stellapply Now
              </SketchButton>
            </Link>
          </div>
        </Section>
      </main>

      <Footer />
    </div>
  );
}
