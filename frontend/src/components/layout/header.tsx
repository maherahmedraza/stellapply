'use client';

import * as React from 'react';
import Link from 'next/link';
import { Menu, X, Rocket } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { Container } from './container';
import { useAuthStore } from '@/stores/auth.store';

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
                <Button variant="ghost" size="sm" onClick={() => logout()}>
                    Log out
                </Button>
            </div>
        );
    }

    return (
        <div className="flex gap-2">
            <Button variant="outline" size="sm" asChild>
                <Link href="/auth/login">Log in</Link>
            </Button>
            <Button size="sm" asChild>
                if (isAuthenticated) {
        return (
                <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-muted-foreground hidden lg:block">
                        Hi, {user?.fullName?.split(' ')[0] || 'User'}
                    </span>
                    <Button variant="outline" size="sm" asChild>
                        <Link href="/dashboard">Dashboard</Link>
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => logout()}>
                        Log out
                    </Button>
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
                </div>
                );
}

                export function Header() {
    const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

                return (
                <header className="sticky top-0 z-sticky w-full border-b-2 border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
                    <Container>
                        <div className="flex h-16 items-center justify-between">
                            {/* Logo */}
                            <Link href="/" className="flex items-center gap-2 group">
                                <div className="flex h-10 w-10 items-center justify-center rounded-wobbly-circle border-2 border-border bg-accent shadow-hand-sm group-hover:shadow-hand-md transition-all duration-fast group-hover:-rotate-3">
                                    <Rocket className="h-5 w-5 text-background-alt" strokeWidth={2.5} />
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
                </header>
                );
}
