import React from "react";
import { Header, Footer, Container, Section } from "@/components/layout";
import { Heading, Text, Card, CardContent, Badge, Button } from "@/components/ui";
import { SquigglyLine, Sparkle } from "@/components/decorations/hand-drawn-elements";
import Link from "next/link";

export default function CareersPage() {
    const openings = [
        { title: "Senior AI Engineer", department: "Engineering", location: "Remote" },
        { title: "Product Designer (Sketch Expert)", department: "Product", location: "Toronto / Remote" },
        { title: "Content Strategist", department: "Growth", location: "Remote" },
    ];

    return (
        <div className="flex flex-col min-h-screen">
            <Header />
            <main className="flex-grow">
                <Section background="alt" className="pt-20 pb-16 relative overflow-hidden">
                    <Container className="text-center">
                        <Heading level="h1" decoration="underline" className="mb-6">
                            Join the Studio
                        </Heading>
                        <Text size="xl" variant="muted" className="max-w-2xl mx-auto">
                            We're looking for artists, engineers, and dreamers to help us redraw the future of work.
                        </Text>
                    </Container>
                </Section>

                <Section className="py-20">
                    <Container size="md">
                        <div className="text-center mb-16">
                            <Heading level="h2" className="mb-4">Why work with us?</Heading>
                            <Text variant="muted">We value autonomy, creativity, and the courage to sketch outside the lines.</Text>
                        </div>

                        <div className="space-y-6 mb-20">
                            {openings.map((job, i) => (
                                <Card key={i} variant="elevated">
                                    <CardContent className="py-6 flex flex-col md:flex-row justify-between items-center gap-6">
                                        <div>
                                            <Heading level="h4" className="mb-1">{job.title}</Heading>
                                            <div className="flex gap-3">
                                                <Text size="sm" variant="muted">{job.department}</Text>
                                                <span className="text-border">•</span>
                                                <Text size="sm" variant="muted">{job.location}</Text>
                                            </div>
                                        </div>
                                        <Button variant="outline" asChild>
                                            <Link href="/contact">Apply Now</Link>
                                        </Button>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>

                        <Card variant="default" padding="lg" className="bg-background-muted/30">
                            <div className="flex flex-col items-center text-center">
                                <Sparkle className="mb-6 text-accent-warning" />
                                <Heading level="h3" className="mb-4">Don't see a perfect fit?</Heading>
                                <Text className="mb-8 max-w-lg">
                                    We're always looking for cosmic talent. Send us your resume (bonus points if it's tailored using StellarApply!) and a note about why you're a fit for the sketchbook.
                                </Text>
                                <Button variant="link" asChild>
                                    <Link href="/contact" className="font-heading text-lg">Send an Open Application →</Link>
                                </Button>
                            </div>
                        </Card>
                    </Container>
                </Section>
            </main>
            <Footer />
        </div>
    );
}
