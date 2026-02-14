import React from "react";
import { Navbar, Footer, Container, Section } from "@/components/layout";
import { Heading, Text, Card, CardContent, Badge } from "@/components/ui";
import { SquigglyLine, Sparkle } from "@/components/decorations/hand-drawn-elements";
import Link from "next/link";

export default function BlogPage() {
    const posts = [
        {
            title: "How AI is changing the 'Sketch' of the Job Market",
            excerpt: "The lines between human and machine are blurring. Here's how to keep your personal touch.",
            date: "Oct 12, 2026",
            tag: "Insights",
            rotation: -1,
        },
        {
            title: "5 Eraser-Free Ways to Fix Your Resume",
            excerpt: "Don't just delete experience—refine it. Learn the art of the perfect career pivot.",
            date: "Oct 08, 2026",
            tag: "Tips",
            rotation: 1,
        },
        {
            title: "The Anatomy of a Perfect Cover Letter",
            excerpt: "Why the 'To Whom It May Concern' is the quickest way to the recycle bin.",
            date: "Sep 29, 2026",
            tag: "Guide",
            rotation: -0.5,
        },
        {
            title: "Navigating ATS Filters Without a Map",
            excerpt: "The corporate logic is weird. We draw a path through the maze of automated recruitment.",
            date: "Sep 22, 2026",
            tag: "Technical",
            rotation: 0.5,
        },
    ];

    return (
        <div className="flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-grow">
                <Section background="alt" className="pt-20 pb-16 relative">
                    <Sparkle className="absolute top-10 left-[10%] text-accent-warning" size={32} />
                    <Container className="text-center">
                        <Heading level="h1" decoration="underline" className="mb-6">
                            The Stellar Scribbles
                        </Heading>
                        <Text size="xl" variant="muted" className="max-w-2xl mx-auto">
                            Tips, tricks, and deep dives into the art of the modern job hunt.
                        </Text>
                    </Container>
                </Section>

                <Section className="py-20">
                    <Container>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                            {posts.map((post, i) => (
                                <Link key={i} href="#" className="group block">
                                    <Card
                                        variant="elevated"
                                        className="h-full transition-transform group-hover:-translate-y-2"
                                        style={{ transform: `rotate(${post.rotation}deg)` }}
                                    >
                                        <CardContent className="pt-10">
                                            <div className="flex justify-between items-start mb-4">
                                                <Badge variant="secondary" size="sm">{post.tag}</Badge>
                                                <Text variant="subtle" size="sm">{post.date}</Text>
                                            </div>
                                            <Heading level="h3" className="mb-4 group-hover:text-accent transition-colors">
                                                {post.title}
                                            </Heading>
                                            <Text variant="muted" className="mb-6">{post.excerpt}</Text>
                                            <div className="flex items-center gap-2 text-accent font-bold">
                                                Read Scribble <span className="group-hover:translate-x-1 transition-transform">→</span>
                                            </div>
                                        </CardContent>
                                    </Card>
                                </Link>
                            ))}
                        </div>

                        <div className="mt-20 text-center">
                            <SquigglyLine className="mx-auto w-32 mb-8 text-accent/20" />
                            <Heading level="h4">Want these in your inbox?</Heading>
                            <Text variant="muted" className="mb-8">No spam, just pure signal once a week.</Text>
                            <div className="max-w-md mx-auto flex gap-2">
                                <div className="flex-grow p-3 wobbly-sm border-2 border-border bg-background-alt">
                                    <input
                                        type="email"
                                        placeholder="your@email.com"
                                        className="w-full bg-transparent focus:outline-none font-body"
                                    />
                                </div>
                                <button className="px-6 py-2 wobbly-sm bg-accent text-background-alt font-bold hover:shadow-hand-md transition-all">
                                    Subscribe
                                </button>
                            </div>
                        </div>
                    </Container>
                </Section>
            </main>
            <Footer />
        </div>
    );
}
