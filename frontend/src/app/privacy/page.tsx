"use client";

import React from "react";
import { Navbar, Footer, Container, Section } from "@/components/layout";
import { Heading, Text, Card, CardContent } from "@/components/ui";
import { Shield, Eye, Lock, Trash2, Globe, Mail } from "lucide-react";

export default function PrivacyPage() {
    const sections = [
        {
            icon: Eye,
            title: "1. Information We Collect",
            content: "We collect information you provide directly: your name, email address, and resume data. We also collect usage analytics to improve our AI models. We never collect data from your device without your knowledge."
        },
        {
            icon: Lock,
            title: "2. How We Use Your Data",
            content: "Your data is used exclusively to power our AI resume tailoring and application automation features. We use anonymized, aggregated data to improve our matching algorithms. We never sell your personal information to third parties."
        },
        {
            icon: Shield,
            title: "3. Data Security",
            content: "All personal data is encrypted at rest using AES-256 encryption and in transit using TLS 1.3. Passwords are hashed with bcrypt. We perform regular security audits and penetration testing to ensure your data remains protected."
        },
        {
            icon: Trash2,
            title: "4. Data Retention & Deletion",
            content: "You can request deletion of your account and all associated data at any time through your dashboard settings. Upon deletion, all personal data is permanently removed within 30 days. Anonymized analytics data may be retained."
        },
        {
            icon: Globe,
            title: "5. International Transfers",
            content: "Your data is stored in EU-based servers. If data is transferred outside the EU, we ensure adequate protection through Standard Contractual Clauses (SCCs) and compliance with GDPR requirements."
        },
        {
            icon: Mail,
            title: "6. Contact & Rights",
            content: "Under GDPR and applicable laws, you have the right to access, rectify, port, and delete your data. For privacy-related inquiries, contact our Data Protection Officer at privacy@stellapply.ai."
        },
    ];

    return (
        <div className="flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-grow">
                <Section background="alt" className="pt-20 pb-16 relative">
                    <Container className="text-center">
                        <div className="flex justify-center mb-6">
                            <div className="w-20 h-20 wobbly-sm bg-accent/10 flex items-center justify-center">
                                <Shield className="w-10 h-10 text-accent" strokeWidth={2.5} />
                            </div>
                        </div>
                        <Heading level="h1" decoration="underline" className="mb-6">
                            Privacy Policy
                        </Heading>
                        <Text size="xl" variant="muted" className="max-w-2xl mx-auto">
                            Your privacy matters. Here&apos;s exactly how we collect, use, and protect your data.
                        </Text>
                    </Container>
                </Section>

                <Section className="py-20">
                    <Container size="md">
                        <div className="space-y-8">
                            {sections.map((section, i) => (
                                <Card key={i} variant="default">
                                    <CardContent>
                                        <div className="flex items-start gap-5">
                                            <div className="w-12 h-12 wobbly-sm bg-background-muted flex items-center justify-center shrink-0 mt-1">
                                                <section.icon className="w-6 h-6 text-accent" strokeWidth={2.5} />
                                            </div>
                                            <div>
                                                <Heading level="h3" className="mb-3">{section.title}</Heading>
                                                <Text variant="muted" size="lg" className="leading-relaxed">
                                                    {section.content}
                                                </Text>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>

                        <div className="mt-16 text-center">
                            <Text variant="muted">
                                Last updated: February 2026 · Effective immediately upon publication
                            </Text>
                        </div>
                    </Container>
                </Section>
            </main>
            <Footer />
        </div>
    );
}
