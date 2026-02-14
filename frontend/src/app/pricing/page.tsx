import React from "react";
import { Navbar, Footer, Container, Section } from "@/components/layout";
import { Heading, Text, Card, CardContent, Button, Badge } from "@/components/ui";
import { SquigglyLine, PostItTag } from "@/components/decorations/hand-drawn-elements";
import { Check } from "lucide-react";
import Link from "next/link";

export default function PricingPage() {
    const plans = [
        {
            name: "Free Sketch",
            price: "$0",
            description: "Perfect for testing the waters and seeing the AI magic.",
            features: ["3 Tailored Resumes", "5 AI Cover Letters", "Basic Interview Points", "Public Dashboard"],
            cta: "Grab a pencil",
            variant: "default" as const,
        },
        {
            name: "Pro Artist",
            price: "$19",
            description: "Everything you need for a serious job hunt.",
            features: ["Unlimited Resumes", "Unlimited Letters", "Advanced Talking Points", "Priority Support", "Private Dashboard"],
            cta: "Master your craft",
            variant: "elevated" as const,
            popular: true,
        },
        {
            name: "Stellar Studio",
            price: "$49",
            description: "Hands-on coaching and automated application prep.",
            features: ["Everything in Pro", "1-on-1 Profile Review", "Automated Form Filling", "Early Feature Access"],
            cta: "Launch to orbit",
            variant: "default" as const,
        },
    ];

    return (
        <div className="flex flex-col min-h-screen">
            <Navbar />
            <main className="flex-grow">
                <Section background="alt" className="pt-20 pb-16 relative">
                    <Container className="text-center relative">
                        <SquigglyLine className="absolute -top-10 left-1/2 -track-x-1/2 w-48 text-accent/20" />
                        <Heading level="h1" className="mb-6">Pricing Plans</Heading>
                        <Text size="xl" variant="muted" className="max-w-2xl mx-auto">
                            Simple, transparent pricing to help you find your worth. No hidden sketchiness.
                        </Text>
                    </Container>
                </Section>

                <Section className="py-20">
                    <Container size="lg">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
                            {plans.map((plan, i) => (
                                <Card key={i} variant={plan.variant} className={plan.popular ? "-mt-4 mb-4 md:-mt-8 md:mb-8 md:z-10" : ""}>
                                    <CardContent className="pt-10 flex flex-col items-center">
                                        {plan.popular && (
                                            <div className="mb-4">
                                                <PostItTag rotation={2} className="bg-accent text-background-alt font-bold">
                                                    MOST POPULAR
                                                </PostItTag>
                                            </div>
                                        )}
                                        <Heading level="h3" className="mb-2">{plan.name}</Heading>
                                        <div className="flex items-baseline gap-1 mb-6">
                                            <span className="text-4xl font-bold">{plan.price}</span>
                                            <span className="text-foreground-muted">/month</span>
                                        </div>
                                        <Text variant="muted" className="text-center mb-8">{plan.description}</Text>

                                        <div className="w-full space-y-4 mb-10">
                                            {plan.features.map((feature, j) => (
                                                <div key={j} className="flex items-center gap-3">
                                                    <Check className="w-5 h-5 text-accent" strokeWidth={3} />
                                                    <Text size="sm">{feature}</Text>
                                                </div>
                                            ))}
                                        </div>

                                        <Button size="lg" variant={plan.popular ? "default" : "outline"} className="w-full" asChild>
                                            <Link href="/auth/register">{plan.cta}</Link>
                                        </Button>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    </Container>
                </Section>

                <Section background="muted" className="py-20 border-t-2 border-border border-dashed text-center">
                    <Container size="sm">
                        <Heading level="h3" className="mb-4">Need a student discount?</Heading>
                        <Text className="mb-8">We believe everyone deserves a chance to launch. Reach out to us if you're a student or between roles.</Text>
                        <Button variant="ghost" asChild>
                            <Link href="/contact">Contact Support</Link>
                        </Button>
                    </Container>
                </Section>
            </main>
            <Footer />
        </div>
    );
}
