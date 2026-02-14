import React from "react";
import { Navbar, Footer, Container, Section } from "@/components/layout";
import { Heading, Text, Card, CardContent, Badge } from "@/components/ui";
import { SquigglyLine, HandDrawnArrow } from "@/components/decorations/hand-drawn-elements";

export default function RoadmapPage() {
    const milestones = [
        {
            quarter: "Q1 2026",
            status: "COMPLETED",
            items: ["Base AI Sketch Engine", "Hand-Drawn UI System", "Dashboard Launch"],
            variant: "success" as const,
        },
        {
            quarter: "Q2 2026",
            status: "IN PROGRESS",
            items: ["Auto-Apply Browser Ext", "LinkedIn Profile Sync", "Interview Simulator"],
            variant: "primary" as const,
        },
        {
            quarter: "Q3 2026",
            status: "PLANNED",
            items: ["Multi-Language Support", "Career Trajectory AI", "Mobile Sketch App"],
            variant: "default" as const,
        },
        {
            quarter: "Q4 2026",
            status: "FUTURE",
            items: ["Direct Recruiter Connect", "AI Salary Negotiator", "Global Talent Network"],
            variant: "outline" as const,
        },
    ];

    return (
        <div className="flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-grow">
                <Section background="alt" className="pt-20 pb-16 relative overflow-hidden">
                    <Container className="text-center">
                        <Heading level="h1" decoration="underline" className="mb-6">
                            The Path to Orbit
                        </Heading>
                        <Text size="xl" variant="muted" className="max-w-2xl mx-auto">
                            Our roadmap isn't set in stone, but it is sketched in ink. Here's what we're working on next.
                        </Text>
                    </Container>
                </Section>

                <Section className="py-20">
                    <Container size="md">
                        <div className="space-y-12 relative">
                            {/* Vertical line decoration */}
                            <div className="absolute left-[39px] top-0 bottom-0 w-1 border-l-2 border-dashed border-border hidden md:block" />

                            {milestones.map((milestone, i) => (
                                <div key={i} className="flex flex-col md:flex-row gap-8 relative">
                                    <div className="md:w-24 shrink-0 flex flex-col items-center">
                                        <div className={`w-20 h-20 wobbly-circle border-2 border-border bg-background-alt flex items-center justify-center z-10 shadow-hand-sm mb-4`}>
                                            <span className="font-heading text-xl">{milestone.quarter.split(' ')[0]}</span>
                                        </div>
                                    </div>
                                    <div className="flex-grow">
                                        <Card variant="elevated">
                                            <CardContent className="pt-8">
                                                <div className="flex justify-between items-start mb-6">
                                                    <Heading level="h3">{milestone.quarter}</Heading>
                                                    <Badge variant={milestone.variant}>{milestone.status}</Badge>
                                                </div>
                                                <ul className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                                    {milestone.items.map((item, j) => (
                                                        <li key={j} className="flex items-center gap-3">
                                                            <div className="w-2 h-2 rounded-full bg-accent" />
                                                            <Text>{item}</Text>
                                                        </li>
                                                    ))}
                                                </ul>
                                            </CardContent>
                                        </Card>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="mt-20 flex flex-col items-center text-center">
                            <HandDrawnArrow direction="up" className="text-accent mb-6" />
                            <Heading level="h4" className="mb-4">Have an idea?</Heading>
                            <Text variant="muted" className="max-w-md mx-auto mb-8">
                                The best features often come from candidate suggestions. Sketch your thoughts and send them our way.
                            </Text>
                            <button className="px-8 py-3 wobbly-md border-2 border-border bg-background-alt font-bold hover:shadow-hand-md transition-all">
                                Submit Feedback
                            </button>
                        </div>
                    </Container>
                </Section>
            </main>
            <Footer />
        </div>
    );
}
