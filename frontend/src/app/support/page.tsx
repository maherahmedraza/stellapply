"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Navbar, Footer, Container, Section } from "@/components/layout";
import { Heading, Text, Card, CardContent, Button } from "@/components/ui";
import { SketchInput, SketchButton } from "@/components/ui/hand-drawn";
import { MessageCircle, BookOpen, Mail, Send, CheckCircle, HelpCircle, Zap, Clock } from "lucide-react";

export default function SupportPage() {
    const [sent, setSent] = useState(false);

    const faqs = [
        { q: "Is StellarApply free to use?", a: "Yes! Our Free Sketch plan includes 3 tailored resumes and 5 AI cover letters per month. Upgrade for unlimited access." },
        { q: "How does AI resume tailoring work?", a: "Our AI reads the job description, then selects and adapts your experience from your Persona profile to create a perfectly targeted resume." },
        { q: "Is my data secure?", a: "Absolutely. All personal data is encrypted at rest (AES-256) and in transit (TLS 1.3). We never sell your data to third parties." },
        { q: "Can I cancel my subscription?", a: "Yes, anytime from your dashboard settings. You'll retain access until the end of your billing period." },
    ];

    return (
        <div className="flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-grow">
                <Section background="alt" className="pt-20 pb-16 relative">
                    <Container className="text-center">
                        <div className="flex justify-center mb-6">
                            <div className="w-20 h-20 wobbly-sm bg-accent-secondary/10 flex items-center justify-center">
                                <MessageCircle className="w-10 h-10 text-accent-secondary" strokeWidth={2.5} />
                            </div>
                        </div>
                        <Heading level="h1" decoration="underline" className="mb-6">
                            Help & Support
                        </Heading>
                        <Text size="xl" variant="muted" className="max-w-2xl mx-auto">
                            Have a question or running into an issue? We&apos;re here to help you get back on track.
                        </Text>
                    </Container>
                </Section>

                {/* Quick Help Cards */}
                <Section className="py-16">
                    <Container>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
                            {[
                                { icon: BookOpen, title: "Documentation", desc: "Guides and tutorials for all features", href: "#faq" },
                                { icon: Mail, title: "Email Support", desc: "Get help within 24 hours", href: "#contact" },
                                { icon: Clock, title: "Status Page", desc: "Check system uptime and incidents", href: "#" },
                            ].map((item, i) => (
                                <a key={i} href={item.href}>
                                    <Card variant="elevated" className="h-full hover:shadow-hand-md transition-shadow cursor-pointer">
                                        <CardContent className="pt-8 text-center">
                                            <div className="w-14 h-14 wobbly-sm bg-background-muted flex items-center justify-center mx-auto mb-4">
                                                <item.icon className="w-7 h-7 text-accent" />
                                            </div>
                                            <Heading level="h4" className="mb-2">{item.title}</Heading>
                                            <Text variant="muted">{item.desc}</Text>
                                        </CardContent>
                                    </Card>
                                </a>
                            ))}
                        </div>
                    </Container>
                </Section>

                {/* FAQ Section */}
                <Section id="faq" background="muted" className="py-20 border-y-2 border-dashed border-border">
                    <Container size="md">
                        <div className="text-center mb-12">
                            <Heading level="h2" className="mb-4">Frequently Asked Questions</Heading>
                            <Text variant="muted" size="lg">Quick answers to common questions</Text>
                        </div>
                        <div className="space-y-6">
                            {faqs.map((faq, i) => (
                                <Card key={i} variant="default">
                                    <CardContent>
                                        <div className="flex gap-4">
                                            <HelpCircle className="w-6 h-6 text-accent shrink-0 mt-0.5" />
                                            <div>
                                                <Heading level="h4" className="mb-2">{faq.q}</Heading>
                                                <Text variant="muted">{faq.a}</Text>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    </Container>
                </Section>

                {/* Contact Form */}
                <Section id="contact" className="py-20">
                    <Container size="sm">
                        <div className="text-center mb-12">
                            <Heading level="h2" className="mb-4">Still Need Help?</Heading>
                            <Text variant="muted" size="lg">Drop us a message and we&apos;ll get back to you within 24 hours</Text>
                        </div>

                        <Card variant="elevated">
                            <CardContent>
                                {sent ? (
                                    <div className="text-center py-12 space-y-6">
                                        <div className="w-20 h-20 wobbly-sm bg-accent/10 flex items-center justify-center mx-auto">
                                            <CheckCircle className="w-10 h-10 text-accent" />
                                        </div>
                                        <Heading level="h3">Message Sent!</Heading>
                                        <Text variant="muted" size="lg">
                                            We&apos;ll get back to you within 24 hours. Check your email for updates.
                                        </Text>
                                        <Button variant="outline" onClick={() => setSent(false)}>
                                            Send Another Message
                                        </Button>
                                    </div>
                                ) : (
                                    <div className="space-y-6">
                                        <div>
                                            <label className="block text-lg font-bold mb-2">Your Name</label>
                                            <SketchInput placeholder="Your name" className="w-full" />
                                        </div>
                                        <div>
                                            <label className="block text-lg font-bold mb-2">Email Address</label>
                                            <SketchInput placeholder="you@example.com" className="w-full" />
                                        </div>
                                        <div>
                                            <label className="block text-lg font-bold mb-2">How can we help?</label>
                                            <textarea
                                                className="w-full min-h-[150px] wobble border-[3px] border-pencil-black dark:border-white p-4 font-handwritten text-xl bg-background-alt dark:bg-background-muted focus:outline-none focus:border-ink-blue focus:ring-4 focus:ring-ink-blue/10"
                                                placeholder="Describe your issue or question..."
                                            />
                                        </div>
                                        <SketchButton
                                            variant="accent"
                                            className="w-full flex items-center justify-center gap-2 text-xl py-4"
                                            onClick={() => setSent(true)}
                                        >
                                            <Send className="w-5 h-5" /> Send Message
                                        </SketchButton>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </Container>
                </Section>
            </main>
            <Footer />
        </div>
    );
}
