import Image from "next/image";

import Link from "next/link";
import { ArrowRight, Sparkles, Zap, Shield, Target, MousePointer2, MoveDown, Rocket } from "lucide-react";
import { SketchButton, SketchCard } from "@/components/ui/hand-drawn";
import { cn } from "@/lib/utils";

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-paper-bg dark:bg-background overflow-x-hidden">
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 md:pt-48 md:pb-32">
        {/* Hand-drawn decorative squiggle (SVG) */}
        <div className="absolute top-20 right-[10%] hidden md:block animate-pulse opacity-50">
          <svg width="200" height="150" viewBox="0 0 200 150" fill="none" className="stroke-pencil-black">
            <path d="M10 80 Q 50 10, 100 80 T 190 80" strokeWidth="3" strokeDasharray="8 8" />
          </svg>
        </div>

        <div className="max-w-5xl mx-auto px-6 text-center relative">
          <div className="inline-flex items-center gap-2 px-6 py-2 wobble border-2 border-pencil-black bg-postit-yellow -rotate-2 mb-10 shadow-sketch-sm">
            <Sparkles className="w-5 h-5 text-marker-red" />
            <span className="text-xl font-bold text-pencil-black uppercase tracking-tight">AI-Powered Sketchbook</span>
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
                <h3 className="text-3xl font-marker font-bold mb-4">{f.title}</h3>
                <p className="text-xl font-handwritten text-pencil-black/80">{f.desc}</p>
              </SketchCard>
            ))}
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="py-20 overflow-hidden">
        <div className="max-w-5xl mx-auto px-6">
          <p className="text-center font-marker text-2xl text-pencil-black/40 mb-12 uppercase tracking-[0.2em]">Trusted by the Best</p>
          <div className="flex flex-wrap justify-center gap-x-16 gap-y-12 opacity-30 grayscale hover:grayscale-0 transition-all duration-500">
            {["Google", "Meta", "Stripe", "Airbnb", "Uber"].map(name => (
              <span key={name} className="text-4xl font-marker">{name}</span>
            ))}
          </div>
        </div>
      </section>

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
