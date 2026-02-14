import React from "react";
import { Navbar, Footer, Container, Section } from "@/components/layout";
import { Heading, Text, Card, CardContent } from "@/components/ui";
import { SquigglyLine, CornerMarks } from "@/components/decorations/hand-drawn-elements";
import { Rocket, Heart, Coffee, Lightbulb } from "lucide-react";

export default function AboutPage() {
    return (
        <div className="flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-grow">
                <Section background="alt" className="pt-20 pb-16 relative overflow-hidden">
                    <div className="absolute -top-10 -right-10 opacity-10">
                        <Rocket size={300} className="rotate-12" />
                    </div>
                    <Container className="text-center relative">
                        <Heading level="h1" decoration="underline" className="mb-6">
                            Our Sketchy Story
                        </Heading>
                        <Text size="xl" variant="muted" className="max-w-2xl mx-auto">
                            StellarApply didn't start in a boardroom. It started on a napkin, born from the frustration of applying to 100 jobs and hearing nothing.
                        </Text>
                    </Container>
                </Section>

                <Section className="py-20">
                    <Container size="md">
                        <div className="relative mb-20">
                            <Card variant="default" className="p-8">
                                <CornerMarks className="text-accent/30" />
                                <Heading level="h2" className="mb-6 rotate-1">The Mission</Heading>
                                <Text size="lg" className="mb-6 leading-relaxed">
                                    The modern job hunt is broken. Automated filters, soulless templates, and a "volume-first" culture have made it harder than ever for great candidates to stand out.
                                </Text>
                                <Text size="lg" className="leading-relaxed">
                                    We built StellarApply to put the "human" back into the application, using AI as a pencil to help you sketch your true worth for every role.
                                </Text>
                            </Card>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                            <div className="space-y-6">
                                <div className="flex gap-4 items-start">
                                    <div className="p-3 wobbly-sm bg-accent/10">
                                        <Heart className="text-accent w-6 h-6" />
                                    </div>
                                    <div>
                                        <Heading level="h4" className="mb-2">People over Processes</Heading>
                                        <Text variant="muted">We build tools that empower the individual, not the corporate machine.</Text>
                                    </div>
                                </div>
                                <div className="flex gap-4 items-start">
                                    <div className="p-3 wobbly-sm bg-accent-secondary/10">
                                        <Lightbulb className="text-accent-secondary w-6 h-6" />
                                    </div>
                                    <div>
                                        <Heading level="h4" className="mb-2">Creative AI</Heading>
                                        <Text variant="muted">AI shouldn't replace your voice—it should help you find it.</Text>
                                    </div>
                                </div>
                            </div>
                            <div className="space-y-6">
                                <div className="flex gap-4 items-start">
                                    <div className="p-3 wobbly-sm bg-accent-warning/10">
                                        <Coffee className="text-accent-warning w-6 h-6" />
                                    </div>
                                    <div>
                                        <Heading level="h4" className="mb-2">Hand-Drawn Quality</Heading>
                                        <Text variant="muted">We care about the details, from our wobbly borders to our AI prompts.</Text>
                                    </div>
                                </div>
                                <div className="flex gap-4 items-start">
                                    <div className="p-3 wobbly-sm bg-accent/10">
                                        <Rocket className="text-accent w-6 h-6" />
                                    </div>
                                    <div>
                                        <Heading level="h4" className="mb-2">Launch Mindset</Heading>
                                        <Text variant="muted">Success is a journey. We're here to help you clear the launchpad.</Text>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </Container>
                </Section>
            </main>
            <Footer />
        </div>
    );
}
