import React from "react";
import { Header, Footer, Container, Section } from "@/components/layout";
import { Heading, Text, Card, CardContent } from "@/components/ui";
import { CornerMarks } from "@/components/decorations/hand-drawn-elements";
import { Shield, Lock, Eye, Download, Trash2 } from "lucide-react";

export default function GDPRPage() {
    const principles = [
        { title: "Transparency", icon: Eye, desc: "We are clear about what we collect and why." },
        { title: "Data Portability", icon: Download, desc: "You can export your data at any time." },
        { title: "Right to Forget", icon: Trash2, desc: "One click and your data is erased forever." },
        { title: "Security", icon: Lock, desc: "Your career data is encrypted and protected." },
    ];

    return (
        <div className="flex flex-col min-h-screen">
            <Header />
            <main className="flex-grow">
                <Section background="alt" className="pt-20 pb-16 relative">
                    <Container className="text-center">
                        <div className="inline-flex items-center gap-3 px-4 py-1 wobbly-sm bg-accent/10 border-2 border-accent mb-6">
                            <Shield className="w-5 h-5 text-accent" />
                            <span className="font-heading font-bold text-accent">GDPR COMPLIANCE</span>
                        </div>
                        <Heading level="h1" className="mb-6">Your Privacy, Our Priority</Heading>
                        <Text size="xl" variant="muted" className="max-w-2xl mx-auto">
                            We take data protection seriously—not just because of regulations, but because your career data is deeply personal.
                        </Text>
                    </Container>
                </Section>

                <Section className="py-20">
                    <Container size="md">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-20">
                            {principles.map((p, i) => (
                                <div key={i} className="flex gap-4 p-6 wobbly-md border-2 border-border bg-background-alt">
                                    <p.icon className="w-8 h-8 text-accent shrink-0" />
                                    <div>
                                        <Heading level="h4" className="mb-2">{p.title}</Heading>
                                        <Text variant="muted">{p.desc}</Text>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <Card variant="default" padding="lg" className="relative">
                            <CornerMarks className="text-accent/20" />
                            <Heading level="h3" className="mb-6">Data Privacy Policy (The Human Version)</Heading>
                            <div className="space-y-6">
                                <div>
                                    <Heading level="h5" className="mb-2">1. What we collect</Heading>
                                    <Text variant="muted">Only what's necessary to sketch your resumes: your name, contact info, and career history. That's it.</Text>
                                </div>
                                <div>
                                    <Heading level="h5" className="mb-2">2. How we use AI</Heading>
                                    <Text variant="muted">Our AI models process your data to generate suggestions. We do NOT use your private data to train public models without your explicit, opt-in consent.</Text>
                                </div>
                                <div>
                                    <Heading level="h5" className="mb-2">3. No Selling</Heading>
                                    <Text variant="muted">We never have, and never will, sell your personal information to third-party advertisers or data brokers.</Text>
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
