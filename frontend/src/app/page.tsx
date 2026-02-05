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

<<<<<<< HEAD
          <Container size="md" className="text-center relative">
            {/* Announcement Badge */}
            <div className="mb-10 inline-block">
              <PostItTag rotation={-2} className="bg-background-accent">
                <div className="flex items-center gap-2 px-1">
                  <Sparkles className="w-4 h-4 text-accent-warning" />
                  <span className="uppercase tracking-wider font-bold">New: AI Sketchbook Engine</span>
=======
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
>>>>>>> feature/resume-upload-gdpr-compliance
                </div>
              </PostItTag>
            </div>

            <Heading level="h1" decoration="none" className="mb-8 leading-[1.1] md:leading-[1.1]">
              Apply to <span className="wavy-underline text-marker-red dark:text-marker-red">10x More</span> Jobs <br className="hidden md:block" />
              <span className="inline-block rotate-subtle bg-background-muted dark:bg-pencil-black/40 px-4 py-1 mt-2">Without the Stress</span>
            </Heading>

<<<<<<< HEAD
            <Text size="xl" variant="muted" className="max-w-2xl mx-auto mb-12 leading-relaxed">
              Stop drawing blanks on applications. StellarApply uses AI to sketch perfectly tailored resumes and automate your journey to your dream role.
            </Text>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-6 relative">
              <Button size="lg" className="-rotate-1 group" asChild>
                <Link href={ctaLink}>
                  {ctaText}
                  <ArrowRight className="w-5 h-5 ml-2 transition-transform group-hover:translate-x-1" strokeWidth={2.5} />
                </Link>
              </Button>

              <Button variant="outline" size="lg" className="rotate-1" asChild>
                <Link href="#features">See How it Works</Link>
              </Button>

              {/* Decorative Arrow */}
              <div className="absolute -left-28 top-1/2 -translate-y-1/2 hidden xl:block -rotate-12">
                <HandDrawnArrow direction="right" className="text-accent" />
                <Text variant="subtle" size="sm" className="font-heading absolute -left-12 -top-6 whitespace-nowrap rotate-6">
                  Check this out!
                </Text>
              </div>
            </div>

            <div className="mt-16 sm:mt-24 flex justify-center animate-bounce opacity-30">
              <MoveDown size={32} />
            </div>
          </Container>
        </Section>

        {/* Features Section */}
        <Section id="features" background="alt" className="border-t-2 border-border border-dashed">
          <Container size="lg">
            <div className="text-center mb-20 relative">
              <Heading level="h2" decoration="underline" className="mb-4">
                Everything you need
              </Heading>
              <Text variant="muted" size="lg">Simple tools for a complex job market</Text>

              {/* Corner marks for the section header */}
              <div className="hidden md:block">
                <CornerMarks className="text-accent/20" />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
              {[
                {
                  title: "AI Resume Sketcher",
                  desc: "Our AI draws from your experience to paint the perfect picture for every single job post.",
                  icon: Zap,
                  variant: "elevated",
                  rotation: -1.5,
                  tag: "Smart"
                },
                {
                  title: "ATS Cracker",
                  desc: "Corporate filters are just puzzles we've already solved. Get found by human recruiters.",
                  icon: Target,
                  variant: "accent",
                  rotation: 1,
                  tag: "Fast"
                },
                {
                  title: "Auto-Pilot Mode",
                  desc: "We do the boring legwork—filling forms and tailored cover letters—while you focus on interviews.",
                  icon: MousePointer2,
                  variant: "elevated",
                  rotation: -0.5,
                  tag: "Automated"
                }
              ].map((feature, i) => (
                <Card
                  key={i}
                  variant={feature.variant as any}
                  className={cn("h-full group")}
                  style={{ transform: `rotate(${feature.rotation}deg)` }}
                >
                  <CardContent className="pt-10 flex flex-col items-center text-center">
                    <div className="w-16 h-16 wobbly-sm bg-background flex items-center justify-center mb-6 shadow-hand-sm transition-transform group-hover:-translate-y-1 group-hover:rotate-6 border-2 border-pencil-black">
                      <feature.icon className="w-8 h-8 text-ink-blue" strokeWidth={2.5} />
                    </div>
                    <Badge variant="primary" size="sm" className="mb-4">{feature.tag}</Badge>
                    <Heading level="h4" className="mb-4">{feature.title}</Heading>
                    <Text variant="muted" leading="relaxed">
                      {feature.desc}
                    </Text>
                  </CardContent>
                </Card>
              ))}
            </div>
          </Container>
        </Section>

        {/* Trust Section */}
        <Section>
          <Container size="md">
            <Text variant="subtle" size="sm" className="text-center uppercase tracking-[0.3em] font-bold mb-12">
              Future Alumni At
            </Text>
            <div className="flex flex-wrap justify-center gap-x-12 gap-y-8 opacity-40 grayscale transition-all duration-700 hover:grayscale-0 hover:opacity-100">
              {["GOOGLE", "META", "STRIPE", "AIRBNB", "NETFLIX"].map(logo => (
                <span key={logo} className="font-heading text-3xl select-none">{logo}</span>
              ))}
            </div>
          </Container>
        </Section>

        {/* Call to Action Section */}
        <Section background="muted" className="border-y-2 border-border">
          <Container size="md" className="text-center relative">
            <SquigglyLine className="absolute -top-10 left-1/2 -translate-x-1/2 w-32 text-accent/20" />

            <Heading level="h2" className="mb-8 rotate-1">
              Ready to Sketch Your New Career?
            </Heading>
            <Text size="lg" className="mb-10 max-w-lg mx-auto">
              Join 1,000+ applicants who have found their dream roles using StellarApply's hand-drawn AI edge.
            </Text>
            <Button size="xl" className="group shadow-hand-lg" asChild>
              <Link href={ctaLink} className="flex items-center">
                {isAuthenticated ? "Go to Dashboard" : "Launch My Journey"}
                <Sparkles className="ml-3 w-6 h-6 text-accent-warning fill-accent-warning transition-transform group-hover:scale-125" />
              </Link>
            </Button>
          </Container>
        </Section>
      </main>

      <Footer />
=======
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
>>>>>>> feature/resume-upload-gdpr-compliance
    </div>
  );
}
