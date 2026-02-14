import React from "react";
import { Navbar, Footer, Container, Section } from "@/components/layout";
import { Heading, Text, Card, CardContent, Button, Input, Textarea } from "@/components/ui";
import { SquigglyLine, HandDrawnArrow } from "@/components/decorations/hand-drawn-elements";
import { Mail, MessageCircle, MapPin } from "lucide-react";

export default function ContactPage() {
    return (
        <div className="flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-grow">
                <Section background="alt" className="pt-20 pb-16 relative">
                    <Container className="text-center">
                        <Heading level="h1" decoration="underline" className="mb-6">
                            Drop us a line
                        </Heading>
                        <Text size="xl" variant="muted" className="max-w-2xl mx-auto">
                            Got a question, some feedback, or just want to tell us about your new job? We're all ears.
                        </Text>
                    </Container>
                </Section>

                <Section className="py-20">
                    <Container>
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
                            <div className="space-y-10">
                                <Heading level="h2">Get in touch</Heading>

                                <div className="space-y-8">
                                    <div className="flex gap-4 items-center">
                                        <div className="w-12 h-12 wobbly-sm bg-accent/10 flex items-center justify-center">
                                            <Mail className="text-accent" />
                                        </div>
                                        <div>
                                            <Heading level="h5">Email us</Heading>
                                            <Text variant="muted">hello@stellapply.ai</Text>
                                        </div>
                                    </div>

                                    <div className="flex gap-4 items-center">
                                        <div className="w-12 h-12 wobbly-sm bg-accent-secondary/10 flex items-center justify-center">
                                            <MessageCircle className="text-accent-secondary" />
                                        </div>
                                        <div>
                                            <Heading level="h5">Live Chat</Heading>
                                            <Text variant="muted">Available Mon-Fri, 9am-5pm EST</Text>
                                        </div>
                                    </div>

                                    <div className="flex gap-4 items-center">
                                        <div className="w-12 h-12 wobbly-sm bg-accent-warning/10 flex items-center justify-center">
                                            <MapPin className="text-accent-warning" />
                                        </div>
                                        <div>
                                            <Heading level="h5">Headquarters</Heading>
                                            <Text variant="muted">Remote-first (But we sketch from Toronto)</Text>
                                        </div>
                                    </div>
                                </div>

                                <div className="relative pt-10">
                                    <HandDrawnArrow direction="right" className="text-accent mb-4" />
                                    <Text variant="accent" className="font-heading italic">We usually reply within 24 hours!</Text>
                                </div>
                            </div>

                            <Card variant="elevated">
                                <CardContent className="space-y-6">
                                    <div>
                                        <label className="block font-heading text-lg mb-2">Your Name</label>
                                        <Input placeholder="John Doe" />
                                    </div>
                                    <div>
                                        <label className="block font-heading text-lg mb-2">Email Address</label>
                                        <Input type="email" placeholder="john@example.com" />
                                    </div>
                                    <div>
                                        <label className="block font-heading text-lg mb-2">Subject</label>
                                        <Input placeholder="How can we help?" />
                                    </div>
                                    <div>
                                        <label className="block font-heading text-lg mb-2">Message</label>
                                        <Textarea placeholder="Sketch out your thoughts here..." />
                                    </div>
                                    <Button size="lg" className="w-full">
                                        Send Message
                                    </Button>
                                </CardContent>
                            </Card>
                        </div>
                    </Container>
                </Section>
            </main>
            <Footer />
        </div>
    );
}
