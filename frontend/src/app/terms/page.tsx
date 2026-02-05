"use client";

import Link from "next/link";
import { SketchCard, SketchButton } from "@/components/ui/hand-drawn";
import { ArrowLeft, Scale } from "lucide-react";

export default function TermsPage() {
    return (
        <div className="min-h-screen bg-paper-bg p-8 md:p-16">
            <div className="max-w-4xl mx-auto">
                <Link href="/">
                    <SketchButton variant="secondary" className="mb-12 flex items-center gap-2">
                        <ArrowLeft className="w-5 h-5" /> Back to Home
                    </SketchButton>
                </Link>

                <SketchCard decoration="tack" color="white" className="p-10 md:p-16 space-y-8">
                    <div className="flex items-center gap-4 mb-8">
                        <div className="w-16 h-16 wobble bg-marker-red/10 flex items-center justify-center">
                            <Scale className="w-10 h-10 text-marker-red" strokeWidth={3} />
                        </div>
                        <h1 className="text-5xl md:text-6xl font-marker rotate-1">Terms of Service</h1>
                    </div>

                    <div className="prose prose-xl font-handwritten text-pencil-black/90 space-y-6">
                        <p className="text-2xl italic mb-8 underline decoration-marker-red decoration-wavy underline-offset-8">
                            By using Stellapply, you agree to these rules. They're like gravity—you can't ignore them.
                        </p>

                        <section className="space-y-4">
                            <h2 className="text-3xl font-marker border-b-2 border-dashed border-pencil-black/20 pb-2">1. The Basics</h2>
                            <p>
                                You must be human (or a very advanced robot with permission).
                                You are responsible for any job offers you get (and the celebrations that follow).
                            </p>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-3xl font-marker border-b-2 border-dashed border-pencil-black/20 pb-2">2. Prohibited Acts</h2>
                            <p>
                                Don't try to hack our sketches. Don't use the AI to apply for jobs you definitely
                                aren't qualified for (like "King of Mars" or "Dragon Tamer").
                            </p>
                        </section>

                        <section className="space-y-4">
                            <h2 className="text-3xl font-marker border-b-2 border-dashed border-pencil-black/20 pb-2">3. Limitation of Liability</h2>
                            <p>
                                We provide the tools, you provide the talent. We aren't responsible if you
                                accidentally get hired by a company you don't like. Choose wisely!
                            </p>
                        </section>

                        <div className="pt-12 text-center text-pencil-black/40">
                            <p>Agreement effective: Upon your first doodle.</p>
                        </div>
                    </div>
                </SketchCard>
            </div>
        </div>
    );
}
