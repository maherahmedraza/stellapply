<<<<<<< HEAD
import React from "react";
import { Header, Footer, Container, Section } from "@/components/layout";
import { Heading, Text, Card, CardContent, Button } from "@/components/ui";
import { SquigglyLine, CornerMarks, HandDrawnArrow } from "@/components/decorations/hand-drawn-elements";
import { Mail, MessageCircle, FileQuestion, Book } from "lucide-react";
import Link from "next/link";

export default function SupportPage() {
    const quickLinks = [
        {
            title: "Documentation",
            desc: "Learn how to use every brush and pencil in the StellarApply kit.",
            icon: Book,
            link: "#",
            cta: "View Docs",
        },
        {
            title: "FAQs",
            desc: "Answers to common questions about AI, privacy, and accounts.",
            icon: FileQuestion,
            link: "#",
            cta: "Browse FAQs",
        },
        {
            title: "Community",
            desc: "Connect with fellow job seekers and share your success stories.",
            icon: MessageCircle,
            link: "#",
            cta: "Join Discord",
        },
    ];

    return (
        <div className="flex flex-col min-h-screen">
            <Header />
            <main className="flex-grow">
                <Section background="alt" className="pt-20 pb-16 relative overflow-hidden">
                    <Container className="text-center relative">
                        <SquigglyLine className="absolute -top-10 right-[15%] w-48 text-accent/20" />
                        <Heading level="h1" decoration="underline" className="mb-6">
                            Support Center
                        </Heading>
                        <Text size="xl" variant="muted" className="max-w-2xl mx-auto">
                            We're here to help you land your dream job. Whether you're stuck on a feature or have a cosmic suggestion, we're ready.
                        </Text>
                    </Container>
                </Section>

                <Section className="py-20">
                    <Container>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
                            {quickLinks.map((item, i) => (
                                <Card key={i} variant="elevated" className="text-center">
                                    <CardContent className="pt-10">
                                        <div className="w-14 h-14 wobbly-circle bg-background-muted flex items-center justify-center mx-auto mb-6 shadow-hand-sm">
                                            <item.icon className="w-7 h-7 text-accent" />
                                        </div>
                                        <Heading level="h4" className="mb-3">{item.title}</Heading>
                                        <Text variant="muted" size="sm" className="mb-6">{item.desc}</Text>
                                        <Button variant="outline" size="sm" className="w-full" asChild>
                                            <Link href={item.link}>{item.cta}</Link>
                                        </Button>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center border-t-2 border-dashed border-border pt-20">
                            <div className="relative">
                                <CornerMarks className="text-accent/20" />
                                <Heading level="h2" className="mb-6">Still stuck?</Heading>
                                <Text size="lg" className="mb-8 font-body">
                                    Our human support team is standing by. We treat every ticket like a custom sketch—no canned responses, just real help.
                                </Text>
                                <div className="flex items-center gap-4 p-4 wobbly-sm border-2 border-accent bg-accent/5">
                                    <Mail className="text-accent" />
                                    <div>
                                        <Text className="font-bold">Email us directly</Text>
                                        <Text variant="muted" size="sm">support@stellapply.ai</Text>
                                    </div>
                                </div>
                                <div className="mt-8">
                                    <HandDrawnArrow direction="right" className="text-accent/40" />
                                </div>
                            </div>

                            <Card variant="default" padding="lg">
                                <Heading level="h3" className="mb-8">Quick Message</Heading>
                                <div className="space-y-6">
                                    <div className="space-y-2">
                                        <label className="font-heading text-sm uppercase tracking-wider">Your Email</label>
                                        <div className="p-3 wobbly-sm border-2 border-border bg-background">
                                            <input type="email" placeholder="you@example.com" className="w-full bg-transparent outline-none" />
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="font-heading text-sm uppercase tracking-wider">How can we help?</label>
                                        <div className="p-3 wobbly-md border-2 border-border bg-background min-h-[120px]">
                                            <textarea placeholder="Tell us what's on your mind..." className="w-full h-full bg-transparent outline-none resize-none" />
                                        </div>
                                    </div>
                                    <Button className="w-full shadow-hand-md">Send Ticket</Button>
                                </div>
                            </Card>
                        </div>
                    </Container>
                </Section>
            </main>
            <Footer />
=======
"use client";

import Link from "next/link";
import { SketchCard, SketchButton, SketchInput } from "@/components/ui/hand-drawn";
import { ArrowLeft, MessageCircle, Send } from "lucide-react";
import { useState } from "react";

export default function SupportPage() {
    const [sent, setSent] = useState(false);

    return (
        <div className="min-h-screen bg-paper-bg p-8 md:p-16">
            <div className="max-w-4xl mx-auto">
                <Link href="/">
                    <SketchButton variant="secondary" className="mb-12 flex items-center gap-2">
                        <ArrowLeft className="w-5 h-5" /> Back to Home
                    </SketchButton>
                </Link>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-12 text-pencil-black">
                    <div className="space-y-8">
                        <div className="flex items-center gap-4">
                            <div className="w-16 h-16 wobble bg-ink-blue/10 flex items-center justify-center">
                                <MessageCircle className="w-10 h-10 text-ink-blue" strokeWidth={3} />
                            </div>
                            <h1 className="text-5xl md:text-6xl font-marker -rotate-2">Support</h1>
                        </div>

                        <p className="text-2xl font-handwritten leading-relaxed">
                            Need a hand? Our space crew is here to help!
                            Whether it's a bug or a missing pencil, just drop a message.
                        </p>

                        <SketchCard color="yellow" decoration="tack" className="p-8">
                            <h3 className="text-2xl font-marker mb-4">Quick FAQ</h3>
                            <ul className="list-disc list-inside font-handwritten text-xl space-y-3">
                                <li>Is it free? (Yes, for now!)</li>
                                <li>Can I change my name? (Yes, in settings)</li>
                                <li>Where do resumes go? (To the moon!)</li>
                            </ul>
                        </SketchCard>
                    </div>

                    <SketchCard decoration="tape" className="bg-white p-8 space-y-6">
                        {sent ? (
                            <div className="h-full flex flex-col items-center justify-center text-center space-y-6 animate-jiggle py-12">
                                <div className="w-20 h-20 bg-marker-red/10 rounded-full flex items-center justify-center text-5xl">🚀</div>
                                <h1 className="text-4xl font-marker text-marker-red">Sent to Orbit!</h1>
                                <p className="text-2xl font-handwritten">We'll get back to you before the next solar flare.</p>
                                <SketchButton onClick={() => setSent(false)} variant="secondary">Send another</SketchButton>
                            </div>
                        ) : (
                            <>
                                <h2 className="text-3xl font-marker mb-4">Drop a note</h2>
                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <label className="text-xl font-marker block">Who are you?</label>
                                        <SketchInput placeholder="Your Space Name" className="w-full" />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xl font-marker block">How can we reach you?</label>
                                        <SketchInput placeholder="email@asteroid.com" className="w-full" />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-xl font-marker block">Message</label>
                                        <textarea
                                            className="w-full min-h-[150px] wobble border-[3px] border-pencil-black p-4 font-handwritten text-xl focus:outline-none focus:border-ink-blue focus:ring-4 focus:ring-ink-blue/10"
                                            placeholder="Write your cosmic thoughts here..."
                                        />
                                    </div>
                                    <SketchButton
                                        variant="accent"
                                        className="w-full flex items-center justify-center gap-2 text-2xl py-4"
                                        onClick={() => setSent(true)}
                                    >
                                        <Send className="w-6 h-6" /> Blast Off!
                                    </SketchButton>
                                </div>
                            </>
                        )}
                    </SketchCard>
                </div>
            </div>
>>>>>>> feature/resume-upload-gdpr-compliance
        </div>
    );
}
