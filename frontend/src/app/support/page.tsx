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
        </div>
    );
}
