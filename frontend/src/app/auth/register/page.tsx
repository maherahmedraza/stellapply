"use client";

import Link from "next/link";
import { useState } from "react";
import { Rocket, Mail, Lock, User, CheckCircle2, ArrowRight } from "lucide-react";
import { SketchButton, SketchCard, SketchInput, SketchCheckbox } from "@/components/ui/hand-drawn";

export default function RegisterPage() {
    const [full_name, setFullName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [marketingConsent, setMarketingConsent] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        try {
            const res = await fetch("http://localhost:8000/api/v1/auth/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password, full_name }),
            });
            const data = await res.json();
            if (!res.ok) {
                const detail = Array.isArray(data.detail) ? data.detail[0].msg : data.detail;
                throw new Error(detail || "Registration failed");
            }
            window.location.href = "/auth/login";
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-paper-bg dark:bg-background flex flex-col md:flex-row relative overflow-hidden">
            {/* Hand-drawn connection squiggle between sides (mobile only) */}
            <div className="md:hidden absolute top-[30%] left-0 w-full h-8 bg-zinc-400/10 -rotate-2 border-y border-dashed border-pencil-black/20" />

            {/* Hero Side */}
            <div className="flex-1 bg-ink-blue/5 dark:bg-pencil-black/20 p-8 md:p-20 flex flex-col justify-center border-b-4 md:border-b-0 md:border-r-4 border-dashed border-pencil-black/20 dark:border-white/10">
                <Link href="/" className="flex items-center gap-2 mb-12 group self-start">
                    <div className="w-12 h-12 wobble bg-pencil-black flex items-center justify-center shadow-sketch-sm group-hover:rotate-6 transition-transform">
                        <Rocket className="w-7 h-7 text-white" strokeWidth={3} />
                    </div>
                    <span className="text-3xl font-marker text-pencil-black">Stellapply</span>
                </Link>

                <h1 className="text-5xl md:text-7xl font-marker text-pencil-black dark:text-white mb-8 leading-none -rotate-1">
                    Start your <span className="text-marker-red underline decoration-dashed underline-offset-8">career sketch</span> today.
                </h1>

                <p className="text-2xl font-handwritten text-pencil-black/80 dark:text-white/80 mb-12 max-w-lg leading-relaxed">
                    Join 5,000+ candidates who stopped applying manually and started sketching their future with AI.
                </p>

                <div className="space-y-6">
                    {[
                        "AI Tailored Resumes",
                        "Automated App Tracking",
                        "ATS Filter Cracking"
                    ].map((text, i) => (
                        <div key={i} className="flex items-center gap-4 group">
                            <div className="w-8 h-8 wobble border-2 border-pencil-black dark:border-white bg-white dark:bg-pencil-black flex items-center justify-center shadow-sketch-sm group-hover:scale-110 transition-transform">
                                <CheckCircle2 className="w-5 h-5 text-ink-blue" strokeWidth={3} />
                            </div>
                            <span className="text-2xl font-handwritten font-bold text-pencil-black/90 dark:text-white/90">{text}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Form Side */}
            <div className="flex-1 p-8 md:p-20 flex items-center justify-center bg-paper-bg relative">
                {/* Sketchy Tape decoration */}
                <div className="absolute top-10 right-10 w-32 h-12 bg-zinc-400/10 rotate-12 border border-pencil-black/10 hidden lg:block" />

                <div className="w-full max-w-md">
                    <SketchCard decoration="none" className="rotate-1 shadow-sketch-lg px-8 py-10">
                        <div className="text-center mb-10">
                            <h2 className="text-4xl font-marker mb-2">Create Account</h2>
                            <p className="text-xl font-handwritten text-pencil-black/60">It only takes a pencil stroke.</p>
                        </div>

                        <form onSubmit={handleRegister} className="space-y-6" noValidate>
                            {error && (
                                <div className="bg-marker-red/10 border-2 border-marker-red p-4 wobble text-marker-red font-bold">
                                    {error}
                                </div>
                            )}
                            <div>
                                <label className="block text-xl font-bold mb-2 ml-2">Full Name</label>
                                <div className="relative">
                                    <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-pencil-black/40" />
                                    <SketchInput
                                        type="text"
                                        placeholder="Leonardo da Vinci"
                                        className="pl-12 w-full"
                                        value={full_name}
                                        onChange={(e) => setFullName(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-xl font-bold mb-2 ml-2">Email Address</label>
                                <div className="relative">
                                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-pencil-black/40" />
                                    <SketchInput
                                        type="email"
                                        placeholder="leo@sketch.ai"
                                        className="pl-12 w-full"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-xl font-bold mb-2 ml-2">Password</label>
                                <div className="relative">
                                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-pencil-black/40" />
                                    <SketchInput
                                        type="password"
                                        placeholder="••••••••"
                                        className="pl-12 w-full"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>

                            <div className="space-y-4 py-4 border-y border-dashed border-pencil-black/10 dark:border-white/10">
                                <SketchCheckbox
                                    label="Allow AI to generate resumes and cover letters (Required)"
                                    checked={true}
                                    onChange={() => { }}
                                />
                                <SketchCheckbox
                                    label="Automate my job applications (Required)"
                                    checked={true}
                                    onChange={() => { }}
                                />
                                <SketchCheckbox
                                    label="I'd love to get marketing tips & career sketches"
                                    checked={marketingConsent}
                                    onChange={setMarketingConsent}
                                />
                            </div>

                            <SketchButton
                                type="submit"
                                variant="accent"
                                className="w-full text-2xl py-4 mt-4"
                                disabled={isLoading}
                            >
                                {isLoading ? "Joining..." : "Join Now"}
                                <ArrowRight className="w-6 h-6 ml-2" strokeWidth={3} />
                            </SketchButton>
                        </form>

                        <p className="text-center mt-6 font-handwritten text-lg text-pencil-black/60 leading-tight">
                            By signing up, you agree to our <Link href="#" className="underline font-bold">Terms</Link> and <Link href="#" className="underline font-bold">Privacy</Link>. (Drawn with care).
                        </p>
                    </SketchCard>

                    <p className="text-center mt-8 font-handwritten text-xl">
                        Already a member? <Link href="/auth/login" className="text-ink-blue font-bold hover:underline">Log in here</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}