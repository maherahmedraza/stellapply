import React from "react";
import { Header, Footer, Container, Section } from "@/components/layout";
import { Heading, Text, Card, CardContent } from "@/components/ui";
import { SquigglyLine, CornerMarks } from "@/components/decorations/hand-drawn-elements";
import { Shield } from "lucide-react";

export default function PrivacyPage() {
    return (
        <div className="flex flex-col min-h-screen">
            <Header />
            <main className="flex-grow">
                <Section background="alt" className="pt-20 pb-16 relative overflow-hidden">
                    <Container className="text-center">
                        <div className="w-16 h-16 wobbly-sm bg-accent/10 flex items-center justify-center mx-auto mb-6">
                            <Shield className="w-8 h-8 text-accent" strokeWidth={2.5} />
                        </div>
                        <Heading level="h1" decoration="underline" className="mb-6">
                            Privacy Policy
                        </Heading>
                        <Text size="xl" variant="muted" className="max-w-2xl mx-auto">
                            At StellarApply, we value your privacy (mostly because we don't want the paperwork either).
                            Here's how we handle your cosmic data.
                        </Text>
                    </Container>
                </Section>

                <Section className="py-20">
                    <Container size="md">
                        <Card variant="default" padding="lg" decoration="tape">
                            <CornerMarks className="text-secondary/20" />
                            <div className="prose prose-lg dark:prose-invert max-w-none space-y-12">
                                <section>
                                    <Heading level="h3" className="mb-4">1. Data Collection</Heading>
                                    <Text className="leading-relaxed">
                                        We collect your name, email, and resume details. Why? So the AI can actually
                                        help you get a job. If we didn't, you'd just be talking to a blank piece of paper.
                                    </Text>
                                </section>

                                <section>
                                    <Heading level="h3" className="mb-4">2. How We Use It</Heading>
                                    <Text className="leading-relaxed">
                                        Your data stays within the asteroid belt of our systems. We use it to tailor your
                                        applications and automate the boring stuff. We don't sell it to space pirates or
                                        ad brokers.
                                    </Text>
                                </section>

                                <section>
                                    <Heading level="h3" className="mb-4">3. AI Transparency</Heading>
                                    <Text className="leading-relaxed">
                                        We use Large Language Models to help you sketch your career. These models process
                                        your data only for your active requests. We do not train proprietary models on
                                        your private career history without explicit permission.
                                    </Text>
                                </section>

                                <section>
                                    <Heading level="h3" className="mb-4">4. Security</Heading>
                                    <Text className="leading-relaxed">
                                        We use top-tier encryption (and some hand-drawn wards) to keep your credentials safe.
                                        We promise to treat your data better than we treat our own high-priority sketches.
                                    </Text>
                                </section>

                                <div className="pt-12 text-center">
                                    <SquigglyLine className="mx-auto w-32 mb-4 text-border/30" />
                                    <Text variant="subtle" size="sm">
                                        Last updated: February 2026 (or whenever the ink dries)
                                    </Text>
                                </div>
                            </div>
                        </Card>
                    </Container>
                </Section>
            </main>
            <Footer />
        </div>
    );
}
