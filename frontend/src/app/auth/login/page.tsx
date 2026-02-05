"use client";

import Link from "next/link";
import { useState } from "react";
import { Rocket, Mail, Lock, ArrowRight, Github } from "lucide-react";
import { SketchButton, SketchCard, SketchInput } from "@/components/ui/hand-drawn";
import { useAuthStore } from "@/stores/auth.store";

export default function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        try {
            const res = await fetch("http://localhost:8000/api/v1/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username: email, password }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Login failed");

            const { setUser, setTokens } = useAuthStore.getState();

            // Decode JWT payload (base64) to get user info
            const payload = data.access_token.split('.')[1];
            const decoded = JSON.parse(atob(payload));

            setUser({
                id: decoded.sub,
                email: decoded.email || '',
                fullName: decoded.name || decoded.preferred_username || 'User',
                tier: 'free'
            });

            setTokens(data.access_token, data.refresh_token || "");

            localStorage.setItem("access_token", data.access_token);
            // Set cookie for middleware
            document.cookie = `access_token=${data.access_token}; path=/; max-age=3600; SameSite=Lax`;
            window.location.href = "/dashboard";
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-paper-bg dark:bg-background flex flex-col items-center justify-center p-6 relative overflow-hidden">
            {/* Decorative Doodles */}
            <div className="absolute top-10 left-10 opacity-20 hidden md:block rotate-12">
                <svg width="100" height="100" viewBox="0 0 100 100" className="stroke-pencil-black dark:stroke-white">
                    <circle cx="50" cy="50" r="40" strokeWidth="2" strokeDasharray="5 5" fill="none" />
                </svg>
            </div>
            <div className="absolute bottom-20 right-10 opacity-20 hidden md:block -rotate-6">
                <svg width="120" height="40" viewBox="0 0 120 40" className="stroke-marker-red">
                    <path d="M10 20 Q 40 10, 60 30 T 110 20" strokeWidth="4" strokeLinecap="round" fill="none" />
                </svg>
            </div>

            <div className="w-full max-w-md relative">
                <Link href="/" className="flex items-center gap-2 mb-8 justify-center group">
                    <div className="w-12 h-12 wobble bg-ink-blue flex items-center justify-center shadow-sketch-sm group-hover:rotate-6 transition-transform">
                        <Rocket className="w-7 h-7 text-white" strokeWidth={3} />
                    </div>
                    <span className="text-3xl font-marker text-pencil-black dark:text-white">Stellapply</span>
                </Link>

                <SketchCard decoration="tack" className="px-8 py-10 rotate-1 shadow-sketch-lg">
                    <div className="text-center mb-8">
                        <h1 className="text-4xl font-marker mb-2">Welcome Back!</h1>
                        <p className="text-xl font-handwritten text-pencil-black/60 dark:text-white/60">Keep sketching your career path.</p>
                    </div>

                    <form onSubmit={handleLogin} className="space-y-6">
                        {error && (
                            <div className="bg-marker-red/10 border-2 border-marker-red p-4 wobble text-marker-red font-bold">
                                {error}
                            </div>
                        )}
                        <div>
                            <label className="block text-xl font-bold mb-2 ml-2">Email Address</label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-pencil-black/40" />
                                <SketchInput
                                    type="email"
                                    placeholder="name@example.com"
                                    className="pl-12 w-full"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <div className="flex justify-between items-center mb-2 ml-2">
                                <label className="text-xl font-bold">Password</label>
                                <Link href="#" className="text-lg font-handwritten text-ink-blue hover:underline">Forgot?</Link>
                            </div>
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

                        <SketchButton
                            type="submit"
                            variant="accent"
                            className="w-full text-2xl py-4 mt-4"
                            disabled={isLoading}
                        >
                            {isLoading ? "Signing in..." : "Log In"}
                            <ArrowRight className="w-6 h-6 ml-2" strokeWidth={3} />
                        </SketchButton>

                        <div className="relative py-4">
                            <div className="absolute inset-0 flex items-center">
                                <div className="w-full border-t-2 border-dashed border-pencil-black/20"></div>
                            </div>
                            <div className="relative flex justify-center text-sm">
                                <span className="px-2 bg-card-bg text-pencil-black/40 dark:text-pencil-black/60 font-bold uppercase tracking-widest transition-colors">Or continue with</span>
                            </div>
                        </div>

                        <button type="button" className="w-full wobble border-2 border-pencil-black dark:border-white py-3 flex items-center justify-center gap-3 hover:bg-zinc-50 dark:hover:bg-white/5 transition-colors font-bold text-lg shadow-sketch-sm dark:shadow-none active:shadow-none translate-x-0 active:translate-x-[2px] active:translate-y-[2px]">
                            <Github className="w-6 h-6" />
                            Github
                        </button>
                    </form>
                </SketchCard>

                <p className="text-center mt-8 font-handwritten text-xl">
                    New here? <Link href="/auth/register" className="text-marker-red font-bold hover:underline">Start sketching free</Link>
                </p>
            </div>
        </div>
    );
}