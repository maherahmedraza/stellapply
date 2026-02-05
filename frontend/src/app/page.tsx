"use client";

import React, { useEffect } from "react";
import Link from "next/link";
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
  useEffect(() => {
    // Automatically log out when landing on the home page (clean state)
    document.cookie = "access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    localStorage.removeItem("access_token");
  }, []);

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

          <Container size="md" className="text-center relative">
            {/* Announcement Badge */}
            <div className="mb-10 inline-block">
              <PostItTag rotation={-2} className="bg-background-accent">
                <div className="flex items-center gap-2 px-1">
                  <Sparkles className="w-4 h-4 text-accent-warning" />
                  <span className="uppercase tracking-wider font-bold">New: AI Sketchbook Engine</span>
                </div>
              </PostItTag>
            </div>

            <Heading level="h1" decoration="none" className="mb-8 leading-[1.1] md:leading-[1.1]">
              Apply to <span className="wavy-underline text-accent">10x More</span> Jobs <br className="hidden md:block" />
              <span className="inline-block rotate-subtle bg-background-muted px-4 py-1 mt-2">Without the Stress</span>
            </Heading>

            <Text size="xl" variant="muted" className="max-w-2xl mx-auto mb-12 leading-relaxed">
              Stop drawing blanks on applications. StellarApply uses AI to sketch perfectly tailored resumes and automate your journey to your dream role.
            </Text>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-6 relative">
              <Button size="lg" className="-rotate-1 group" asChild>
                <Link href="/auth/register">
                  Get Started For Free
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
                    <div className="w-16 h-16 wobbly-sm bg-background flex items-center justify-center mb-6 shadow-hand-sm transition-transform group-hover:-translate-y-1 group-hover:rotate-6">
                      <feature.icon className="w-8 h-8 text-accent" strokeWidth={2.5} />
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
            <Button size="xl" className="group shadow-hand-lg">
              <Link href="/auth/register" className="flex items-center">
                Launch My Journey
                <Sparkles className="ml-3 w-6 h-6 text-accent-warning fill-accent-warning transition-transform group-hover:scale-125" />
              </Link>
            </Button>
          </Container>
        </Section>
      </main>

      <Footer />
    </div>
  );
}
