"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Rocket, Menu, X, PencilLine } from "lucide-react";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { SketchButton } from "@/components/ui/hand-drawn";

export default function Navbar() {
    const [isScrolled, setIsScrolled] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const pathname = usePathname();

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 20);
        };
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const navLinks = [
        { name: "Features", href: "/#features" },
        { name: "Resumes", href: "/dashboard/resumes" },
        { name: "Applications", href: "/dashboard/applications" },
        { name: "Privacy", href: "/dashboard/settings/privacy" },
    ];

    const isAuthPage = pathname.startsWith("/auth");

    if (isAuthPage) return null;

    return (
        <nav
            className={cn(
                "fixed top-0 left-0 right-0 z-50 transition-all duration-300 px-6 py-4",
                isScrolled
                    ? "bg-paper-bg/90 dark:bg-background/90 backdrop-blur-sm border-b-2 border-dashed border-pencil-black py-3"
                    : "bg-transparent"
            )}
        >
            <div className="max-w-5xl mx-auto flex items-center justify-between">
                <Link href="/" className="flex items-center gap-2 group">
                    <div className="relative">
                        <div className="w-10 h-10 wobble bg-ink-blue flex items-center justify-center shadow-sketch-sm group-hover:rotate-6 transition-transform">
                            <Rocket className="w-6 h-6 text-white" strokeWidth={3} />
                        </div>
                        {/* Scribbled decoration */}
                        <div className="absolute -top-1 -right-1 w-3 h-3 bg-marker-red rounded-full border border-pencil-black" />
                    </div>
                    <span className="text-2xl font-marker tracking-tighter text-pencil-black">
                        Stellapply
                    </span>
                </Link>

                {/* Desktop Links */}
                <div className="hidden md:flex items-center gap-8">
                    {navLinks.map((link) => (
                        <Link
                            key={link.name}
                            href={link.href}
                            className="relative group p-1"
                        >
                            <span className="text-lg font-bold text-pencil-black/80 hover:text-pencil-black transition-colors">
                                {link.name}
                            </span>
                            <div className="absolute -bottom-1 left-0 w-0 h-0.5 bg-marker-red transition-all duration-200 group-hover:w-full rotate-1" />
                        </Link>
                    ))}
                </div>

                <div className="hidden md:flex items-center gap-6">
                    <Link
                        href="/auth/login"
                        className="text-lg font-bold text-pencil-black hover:text-ink-blue transition-colors relative"
                    >
                        Log in
                        <PencilLine className="w-4 h-4 absolute -right-5 top-0 text-marker-red opacity-0 group-hover:opacity-100 transition-opacity" />
                    </Link>
                    <SketchButton variant="primary" className="scale-90">
                        Get Started
                    </SketchButton>
                </div>

                {/* Mobile Toggle */}
                <button
                    className="md:hidden p-2 text-pencil-black border-2 border-pencil-black wobble"
                    onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                >
                    {mobileMenuOpen ? <X /> : <Menu />}
                </button>
            </div>

            {/* Mobile Menu */}
            {mobileMenuOpen && (
                <div className="md:hidden absolute top-full left-4 right-4 mt-2 bg-paper-bg dark:bg-background border-[3px] border-pencil-black wobble-md p-8 flex flex-col gap-6 shadow-sketch animate-in slide-in-from-top-4 duration-200">
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-20 h-6 bg-zinc-400/20 -rotate-1 border border-black/5" />
                    {navLinks.map((link) => (
                        <Link
                            key={link.name}
                            href={link.href}
                            onClick={() => setMobileMenuOpen(false)}
                            className="text-2xl font-marker text-pencil-black border-b border-dashed border-pencil-black/20 pb-2"
                        >
                            {link.name}
                        </Link>
                    ))}
                    <div className="flex flex-col gap-4 pt-4">
                        <Link
                            href="/auth/login"
                            className="flex justify-center text-xl font-bold p-4 border-2 border-pencil-black wobble"
                        >
                            Log in
                        </Link>
                        <SketchButton variant="accent" className="w-full text-xl py-4">
                            Get Started
                        </SketchButton>
                    </div>
                </div>
            )}
        </nav>
    );
}
