<<<<<<< HEAD
'use client';

import * as React from 'react';
import Link from 'next/link';
import { Menu, X, Rocket } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { Container } from './container';
import { useAuthStore } from '@/stores/auth.store';
import { SketchButton } from '@/components/ui/hand-drawn';

interface NavItem {
    label: string;
    href: string;
}

const navItems: NavItem[] = [
    { label: 'Features', href: '/features' },
    { label: 'Pricing', href: '/pricing' },
    { label: 'About', href: '/about' },
    { label: 'Blog', href: '/blog' },
];

function AuthButtons() {
    const { isAuthenticated, user, logout } = useAuthStore();
    const [mounted, setMounted] = React.useState(false);

    React.useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) {
        // Return consistent placeholder to avoid hydration mismatch
        return (
            <div className="flex gap-2 opacity-0">
                <Button variant="outline" size="sm">Log in</Button>
                <Button size="sm">Get Started</Button>
            </div>
        )
    }

    if (isAuthenticated) {
        return (
            <div className="flex items-center gap-3">
                <span className="text-sm font-medium text-muted-foreground hidden lg:block">
                    Hi, {user?.fullName?.split(' ')[0] || 'User'}
                </span>
                <Button variant="outline" size="sm" asChild>
                    <Link href="/dashboard">Dashboard</Link>
                </Button>
                <SketchButton
                    variant="secondary"
                    className="text-sm px-4 py-1"
                    onClick={() => logout()}
                >
                    Log out
                </SketchButton>
            </div>
        );
    }

    return (
        <div className="flex gap-2">
            <Button variant="outline" size="sm" asChild>
                <Link href="/auth/login">Log in</Link>
            </Button>
            <Button size="sm" asChild>
                <Link href="/auth/register">Get Started</Link>
            </Button>
=======
"use client";

import { useState, useRef, useEffect } from "react";
import { User, Settings, LogOut, ChevronDown } from "lucide-react";
import Link from "next/link";
import { logout } from "@/lib/auth";

import { ThemeToggle } from "@/components/ui/theme-toggle";

interface UserInfo {
    name?: string | null;
    email?: string | null;
    image?: string | null;
}

function UserMenu({ user }: { user: UserInfo }) {
    const [isOpen, setIsOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    // Close menu when clicking outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleLogout = async () => {
        await logout();
    };

    return (
        <div ref={menuRef} className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-3 py-2 wobble border-2 border-pencil-black bg-white dark:bg-muted-paper hover:bg-ink-blue hover:text-white transition-all group"
            >
                <div className="w-8 h-8 wobble bg-ink-blue/20 flex items-center justify-center text-ink-blue group-hover:bg-white/20 group-hover:text-white">
                    <User className="w-5 h-5" strokeWidth={2.5} />
                </div>
                <span className="font-handwritten text-lg hidden sm:block">
                    {user?.name || "Space Cadet"}
                </span>
                <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? "rotate-180" : ""}`} />
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-56 wobble border-3 border-pencil-black bg-white dark:bg-muted-paper shadow-sketch-lg z-50 animate-in fade-in slide-in-from-top-2 duration-200">
                    <div className="p-4 border-b-2 border-dashed border-pencil-black/20">
                        <p className="font-marker text-lg truncate">{user?.name || "Space Cadet"}</p>
                        <p className="font-handwritten text-sm text-pencil-black/60 truncate">
                            {user?.email || "cadet@stellapply.ai"}
                        </p>
                    </div>

                    <div className="p-2">
                        <Link
                            href="/dashboard/settings"
                            onClick={() => setIsOpen(false)}
                            className="flex items-center gap-3 px-3 py-2 font-handwritten text-lg hover:bg-ink-blue hover:text-white transition-colors wobble"
                        >
                            <Settings className="w-5 h-5" />
                            Settings
                        </Link>

                        <button
                            onClick={handleLogout}
                            className="w-full flex items-center gap-3 px-3 py-2 font-handwritten text-lg text-marker-red hover:bg-marker-red hover:text-white transition-colors wobble"
                        >
                            <LogOut className="w-5 h-5" />
                            Logout
                        </button>
                    </div>
                </div>
            )}
>>>>>>> feature/resume-upload-gdpr-compliance
        </div>
    );
}

<<<<<<< HEAD
export function Header() {
    const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

    return (
        <header className="sticky top-0 z-sticky w-full border-b-2 border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
            <Container>
                <div className="flex h-16 items-center justify-between">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2 group">
                        <div className="flex h-10 w-10 items-center justify-center rounded-wobbly-circle border-2 border-pencil-black bg-accent shadow-hand-sm group-hover:shadow-hand-md transition-all duration-fast group-hover:-rotate-3">
                            <Rocket className="h-5 w-5 text-ink-blue" strokeWidth={2.5} />
                        </div>
                        <span className="font-heading text-2xl text-foreground hidden sm:block">
                            StellarApply
                        </span>
                    </Link>

                    {/* Desktop Navigation */}
                    <nav className="hidden md:flex items-center gap-1">
                        {navItems.map((item) => (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    'px-4 py-2 font-body text-lg text-foreground',
                                    'rounded-wobbly-sm transition-all duration-fast',
                                    'hover:bg-background-muted hover:rotate-subtle',
                                    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-secondary'
                                )}
                            >
                                {item.label}
                            </Link>
                        ))}
                    </nav>

                    {/* Desktop Actions */}
                    <div className="hidden md:flex items-center gap-3">
                        <ThemeToggle size="sm" />
                        <AuthButtons />
                    </div>

                    {/* Mobile Menu Button */}
                    <div className="flex md:hidden items-center gap-2">
                        <ThemeToggle size="sm" />
                        <Button
                            variant="ghost"
                            size="icon-sm"
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
                        >
                            {mobileMenuOpen ? (
                                <X className="h-5 w-5" strokeWidth={2.5} />
                            ) : (
                                <Menu className="h-5 w-5" strokeWidth={2.5} />
                            )}
                        </Button>
                    </div>
                </div>

                {/* Mobile Navigation */}
                {mobileMenuOpen && (
                    <div className="md:hidden border-t-2 border-dashed border-border py-4">
                        <nav className="flex flex-col gap-2">
                            {navItems.map((item) => (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={cn(
                                        'px-4 py-3 font-body text-lg text-foreground',
                                        'rounded-wobbly-sm transition-all duration-fast',
                                        'hover:bg-background-muted'
                                    )}
                                >
                                    {item.label}
                                </Link>
                            ))}
                            <div className="flex flex-col gap-2 pt-4 border-t-2 border-dashed border-border mt-2">
                                <div className="flex justify-center">
                                    <AuthButtons />
                                </div>
                            </div>
                        </nav>
                    </div>
                )}
            </Container>
=======
export function Header({ user }: { user: UserInfo }) {
    return (
        <header className="h-16 bg-paper-bg border-b-3 border-pencil-black flex items-center justify-between px-6">
            <div className="flex items-center gap-4">
                <span className="font-marker text-xl text-pencil-black">
                    Welcome, <span className="text-ink-blue">{user?.name || "Space Cadet"}</span>
                </span>
            </div>

            <div className="flex items-center gap-4">
                <ThemeToggle />
                <UserMenu user={user} />
            </div>
>>>>>>> feature/resume-upload-gdpr-compliance
        </header>
    );
}
