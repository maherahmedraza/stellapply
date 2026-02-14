import React from "react";
import { Navbar, Footer, Container, Section } from "@/components/layout";
import { Heading, Text, Card, CardContent, Button } from "@/components/ui";
import { SquigglyLine, Sparkle } from "@/components/decorations/hand-drawn-elements";
import Link from "next/link";
import { Rocket, Target, Zap, MousePointer2, Shield, Heart } from "lucide-react";

export default function FeaturesPage() {
    const features = [
        {
            title: "AI Resume Sketcher",
            description: "Our AI doesn't just fill templates; it sketches a unique story for every application based on your real experience.",
            icon: Zap,
        },
        {
            title: "Hyper-Personalized Cover Letters",
            description: "Stop using cookie-cutter letters. We draft ones that sound like you and speak directly to what the hiring manager wants.",
            icon: Heart,
        },
        {
            title: "Smart ATS Matching",
            description: "Corporate filters are just puzzles. We've cracked the code to ensure your application reaches a human eye.",
            icon: Target,
        },
        {
            title: "One-Click Application Prep",
            description: "Get everything you need for an application in seconds—tailored resume, letter, and interview talking points.",
            icon: MousePointer2,
        },
        {
            title: "Privacy-First Design",
            description: "Your data is your property. We use it only to help you find work, never to sell to third parties.",
            icon: Shield,
        },
        {
            title: "Launch Analytics",
            description: "Track your application trajectory with our simple, hand-drawn dashboard. Know where you stand.",
            icon: Rocket,
        },
    ];

    return (
        <div className="flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-grow">
                <Section background="alt" className="pt-20 pb-16 relative overflow-hidden">
                    <SquigglyLine className="absolute top-10 right-[10%] w-48 text-accent/20" />
                    <Container className="text-center relative">
                        <Heading level="h1" decoration="underline" className="mb-6">
                            Our Sketchbook of Features
                        </Heading>
                        <Text size="xl" variant="muted" className="max-w-2xl mx-auto">
                            We built StellarApply to take the "work" out of searching for work. Here's a look under the hood.
                        </Text>
                    </Container>
                </Section>

                <Section className="py-20">
                    <Container>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                            {features.map((feature, i) => (
                                <Card key={i} variant="elevated" className="h-full">
                                    <CardContent className="pt-8">
                                        <div className="w-12 h-12 wobbly-sm bg-background-muted flex items-center justify-center mb-6">
                                            <feature.icon className="w-6 h-6 text-accent" />
                                        </div>
                                        <Heading level="h4" className="mb-3">{feature.title}</Heading>
                                        <Text variant="muted">{feature.description}</Text>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    </Container>
                </Section>

                <Section background="muted" className="py-20 border-t-2 border-border border-dashed text-center">
                    <Container size="sm">
                        <Sparkle className="mx-auto mb-6 text-accent-warning" size={40} />
                        <Heading level="h2" className="mb-6">Ready to see these in action?</Heading>
                        <Text size="lg" className="mb-8">Join the thousands of candidates finding their dream roles with the StellarApply edge.</Text>
                        <Button size="lg" asChild>
                            <Link href="/auth/register">Start My Journey</Link>
                        </Button>
                    </Container>
                </Section>
            </main>
            <Footer />
        </div>
    );
}
