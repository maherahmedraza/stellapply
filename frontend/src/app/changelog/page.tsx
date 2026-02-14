import React from "react";
import { Navbar, Footer, Container, Section } from "@/components/layout";
import { Heading, Text, Card, CardContent, Badge } from "@/components/ui";
import { SquigglyLine, Sparkle } from "@/components/decorations/hand-drawn-elements";
import { Rocket, Sparkles, Shield, Wrench } from "lucide-react";

export default function ChangelogPage() {
    const updates = [
        {
            version: "v1.2.0",
            date: "Feb 04, 2026",
            title: "The Hand-Drawn Revolution",
            icon: Sparkles,
            tag: "Feature",
            items: [
                "Complete redesign with sketchbook/hand-drawn aesthetic",
                "New adaptive dark mode (Dark Kraft Paper)",
                "Integrated high-fidelity components (Wobbly borders, offset shadows)",
                "Launched decorative SVG library for sections",
            ],
        },
        {
            version: "v1.1.5",
            date: "Jan 28, 2026",
            title: "Infrastructure & Security",
            icon: Shield,
            tag: "Security",
            items: [
                "Enhanced token rotation in middleware",
                "Public path optimization for landing sub-pages",
                "Database performance indexing for job searches",
            ],
        },
        {
            version: "v1.1.0",
            date: "Jan 15, 2026",
            title: "AI Sketching Baseline",
            icon: Rocket,
            tag: "Core",
            items: [
                "Initial release of AI Resume Tailoring",
                "Basic user dashboard and auth flow",
                "PDF export functionality for generated resumes",
            ],
        },
    ];

    return (
        <div className="flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-grow">
                <Section background="alt" className="pt-20 pb-16 relative overflow-hidden">
                    <Sparkle className="absolute top-10 right-[15%] text-accent" size={32} />
                    <Container className="text-center">
                        <Heading level="h1" decoration="underline" className="mb-6">
                            Changelog
                        </Heading>
                        <Text size="xl" variant="muted" className="max-w-2xl mx-auto">
                            Keeping the sketch up to date. Here's a record of every pencil stroke and polish we've added.
                        </Text>
                    </Container>
                </Section>

                <Section className="py-20">
                    <Container size="md">
                        <div className="space-y-16">
                            {updates.map((update, i) => (
                                <div key={i} className="relative">
                                    <div className="flex flex-col md:flex-row gap-8 items-start">
                                        <div className="shrink-0 flex flex-col items-center">
                                            <div className="w-16 h-16 wobbly-sm bg-background-muted flex items-center justify-center mb-2 shadow-hand-sm">
                                                <update.icon className="w-8 h-8 text-accent" />
                                            </div>
                                            <Text variant="subtle" size="sm" className="font-heading">{update.version}</Text>
                                        </div>
                                        <div className="flex-grow">
                                            <div className="flex items-center gap-3 mb-4">
                                                <Badge variant="outline" size="sm">{update.tag}</Badge>
                                                <Text variant="muted" size="sm">{update.date}</Text>
                                            </div>
                                            <Heading level="h2" className="mb-6">{update.title}</Heading>
                                            <ul className="space-y-4">
                                                {update.items.map((item, j) => (
                                                    <li key={j} className="flex items-start gap-4">
                                                        <Wrench className="w-5 h-5 text-accent/40 shrink-0 mt-0.5" />
                                                        <Text>{item}</Text>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    </div>
                                    {i < updates.length - 1 && (
                                        <SquigglyLine className="mt-16 text-border/30 w-full" />
                                    )}
                                </div>
                            ))}
                        </div>
                    </Container>
                </Section>
            </main>
            <Footer />
        </div>
    );
}
