"use client";

import Link from "next/link";
import { SketchCard, SketchButton } from "@/components/ui/hand-drawn";
import { ArrowLeft, Shield } from "lucide-react";

export default function PrivacyPage() {
    return (
        <div className="min-h-screen bg-paper-bg p-8 md:p-16">
            <div className="max-w-4xl mx-auto">
                <Link href="/">
                    <SketchButton variant="secondary" className="mb-12 flex items-center gap-2">
                        <ArrowLeft className="w-5 h-5" /> Back to Home
                    </SketchButton>
                </Link>

                <SketchCard decoration="tape" className="bg-white p-10 md:p-16 space-y-8">
                    <div className="flex items-center gap-4 mb-8">
                        <div className="w-16 h-16 wobble bg-ink-blue/10 flex items-center justify-center">
                            <Shield className="w-10 h-10 text-ink-blue" strokeWidth={3} />
                        </div>
                        <h1 className="text-5xl md:text-6xl font-marker -rotate-1">Privacy Policy</h1>
                    </div>

                    <div className="prose prose-xl font-handwritten text-pencil-black/90 space-y-6">
                        <p className="text-2xl italic mb-8">
                            At Stellapply, we value your privacy (mostly because we don't want the paperwork either).
                            Here's how we handle your cosmic data.
                        </p>

                        <section className="space-y-4">
                            <h2 className="text-3xl font-marker border-b-2 border-dashed border-pencil-black/20 pb-2">1. Data Collection</h2>
                            <p>
                                We collect your name, email, and resume details. Why? So the AI can actually
                                help you get a job. If we didn't, you'd just be talking to a blank piece of paper.
                            </p>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-3xl font-marker border-b-2 border-dashed border-pencil-black/20 pb-2">2. How We Use It</h2>
                            <p>
                                Your data stays within the asteroid belt of our systems. We use it to tailor your
                                applications and automate the boring stuff. We don't sell it to space pirates.
                            </p>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-3xl font-marker border-b-2 border-dashed border-pencil-black/20 pb-2">3. Security</h2>
                            <p>
                                We use top-tier encryption (and some hand-drawn wards) to keep your passwords safe.
                                We promise to treat your data better than we treat our own sketches.
                            </p>
                        </section>

                        <div className="pt-12 text-center text-pencil-black/40">
                            <p>Last updated: February 2026 (or whenever the ink dries)</p>
                        </div>
                    </div>
                </SketchCard>
            </div>
        </div>
    );
}
