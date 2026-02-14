"use client";

import React from "react";
import { Navbar, Footer, Container, Section } from "@/components/layout";
import { Heading, Text, Card, CardContent } from "@/components/ui";
import { Scale, FileCheck, AlertTriangle, Ban, CreditCard, Gavel } from "lucide-react";

export default function TermsPage() {
    const sections = [
        {
            icon: FileCheck,
            title: "1. Acceptance of Terms",
            content: "By creating an account or using StellarApply, you agree to these Terms of Service. If you do not agree, please do not use our platform. We may update these terms periodically; continued use constitutes acceptance of changes."
        },
        {
            icon: Scale,
            title: "2. Use of the Service",
            content: "StellarApply provides AI-powered resume tailoring and job application automation. You must provide accurate information and are responsible for all activity under your account. You must be at least 16 years old to use this service."
        },
        {
            icon: Ban,
            title: "3. Prohibited Conduct",
            content: "You may not: use the platform for fraudulent applications, attempt to reverse-engineer our AI models, share your account credentials, or use automated tools to scrape our service. Violations may result in immediate account termination."
        },
        {
            icon: CreditCard,
            title: "4. Billing & Subscriptions",
            content: "Free tier users have limited AI generations per month. Paid subscriptions are billed monthly and can be cancelled at any time. Refunds are provided on a case-by-case basis within 14 days of purchase."
        },
        {
            icon: AlertTriangle,
            title: "5. Limitation of Liability",
            content: "StellarApply provides tools to assist your job search but does not guarantee employment outcomes. We are not liable for hiring decisions made by employers. Our total liability is limited to the amount you paid in the 12 months prior to any claim."
        },
        {
            icon: Gavel,
            title: "6. Governing Law & Disputes",
            content: "These terms are governed by the laws of the European Union. Any disputes shall be resolved through binding arbitration. You agree to attempt informal resolution before initiating formal proceedings."
        },
    ];

    return (
        <div className="flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-grow">
                <Section background="alt" className="pt-20 pb-16 relative">
                    <Container className="text-center">
                        <div className="flex justify-center mb-6">
                            <div className="w-20 h-20 wobbly-sm bg-accent-warning/10 flex items-center justify-center">
                                <Scale className="w-10 h-10 text-accent-warning" strokeWidth={2.5} />
                            </div>
                        </div>
                        <Heading level="h1" decoration="underline" className="mb-6">
                            Terms of Service
                        </Heading>
                        <Text size="xl" variant="muted" className="max-w-2xl mx-auto">
                            The ground rules for using StellarApply. Clear, fair, and straightforward.
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
                                                <section.icon className="w-6 h-6 text-accent-warning" strokeWidth={2.5} />
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
                                Last updated: February 2026 · These terms are effective upon account creation
                            </Text>
                        </div>
                    </Container>
                </Section>
            </main>
            <Footer />
        </div>
    );
}
