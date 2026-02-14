"use client";

import React from "react";
import Link from "next/link";
import { Rocket } from "lucide-react";
import { useAuthStore } from "@/stores/auth.store";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { SketchButton } from "@/components/ui";

/**
 * Public navigation bar for marketing / unauthenticated pages.
 * Shows logo, nav links, and login/register CTAs.
 * This is distinct from the dashboard Header which requires a user session.
 */
export function Navbar() {
    const { isAuthenticated, isLoading } = useAuthStore();

    return (
        <header className="sticky top-0 z-50 h-16 bg-background/95 backdrop-blur-sm border-b-3 border-pencil-black flex items-center justify-between px-6">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2 group">
                <div className="flex h-10 w-10 items-center justify-center rounded-wobbly-circle border-2 border-border bg-accent shadow-hand-sm group-hover:rotate-12 transition-transform">
                    <Rocket className="h-5 w-5 text-background-alt" strokeWidth={2.5} />
                </div>
                <span className="font-heading text-xl text-foreground hidden sm:block">
                    StellarApply
                </span>
            </Link>

            {/* Actions */}
            <div className="flex items-center gap-4">
                <ThemeToggle />

                {/* Show auth-aware buttons only after hydration */}
                {!isLoading && (
                    isAuthenticated ? (
                        <Link href="/dashboard">
                            <SketchButton variant="accent" className="text-base py-2 px-5">
                                Dashboard
                            </SketchButton>
                        </Link>
                    ) : (
                        <div className="flex items-center gap-3">
                            <Link
                                href="/auth/login"
                                className="font-handwritten text-lg hover:text-accent transition-colors hidden sm:block"
                            >
                                Log in
                            </Link>
                            <Link href="/auth/register">
                                <SketchButton variant="accent" className="text-base py-2 px-5">
                                    Sign Up
                                </SketchButton>
                            </Link>
                        </div>
                    )
                )}
            </div>
        </header>
    );
}
