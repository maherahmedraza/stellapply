'use client';

import * as React from 'react';
import { useTheme } from 'next-themes';
import { Moon, Sun } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ThemeToggleProps {
    className?: string;
    size?: 'sm' | 'md' | 'lg';
}

export function ThemeToggle({ className, size = 'md' }: ThemeToggleProps) {
    const { theme, setTheme, resolvedTheme } = useTheme();
    const [mounted, setMounted] = React.useState(false);

    // Prevent hydration mismatch
    React.useEffect(() => {
        setMounted(true);
    }, []);

    const toggleTheme = () => {
        setTheme(resolvedTheme === 'dark' ? 'light' : 'dark');
    };

    const sizeClasses = {
        sm: 'h-8 w-8',
        md: 'h-10 w-10',
        lg: 'h-12 w-12',
    };

    const iconSizes = {
        sm: 16,
        md: 20,
        lg: 24,
    };

    // Show placeholder during SSR to prevent layout shift
    if (!mounted) {
        return (
            <div
                className={cn(
                    sizeClasses[size],
                    'rounded-wobbly-sm bg-background-muted animate-pulse',
                    className
                )}
            />
        );
    }

    const isDark = resolvedTheme === 'dark';

    return (
        <button
            onClick={toggleTheme}
            className={cn(
                // Base styles
                sizeClasses[size],
                'relative flex items-center justify-center',
                // Hand-drawn styling
                'border-2 border-border bg-background-alt',
                'shadow-hand-md',
                // Wobbly border
                'wobbly-sm',
                // Interactive states
                'transition-all duration-fast',
                'hover:bg-background-muted hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-hand-lg',
                'active:translate-x-1 active:translate-y-1 active:shadow-hand-none',
                // Focus
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-secondary focus-visible:ring-offset-2',
                className
            )}
            aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
        >
            {/* Sun icon - visible in dark mode */}
            <Sun
                size={iconSizes[size]}
                className={cn(
                    'absolute transition-all duration-300',
                    isDark
                        ? 'rotate-0 scale-100 opacity-100'
                        : 'rotate-90 scale-0 opacity-0'
                )}
                strokeWidth={2.5}
            />

            {/* Moon icon - visible in light mode */}
            <Moon
                size={iconSizes[size]}
                className={cn(
                    'absolute transition-all duration-300',
                    isDark
                        ? '-rotate-90 scale-0 opacity-0'
                        : 'rotate-0 scale-100 opacity-100'
                )}
                strokeWidth={2.5}
            />
        </button>
    );
}

// Alternative: Switch-style toggle
export function ThemeSwitch({ className }: { className?: string }) {
    const { resolvedTheme, setTheme } = useTheme();
    const [mounted, setMounted] = React.useState(false);

    React.useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) {
        return (
            <div
                className={cn(
                    'h-8 w-16 rounded-wobbly-lg bg-background-muted animate-pulse',
                    className
                )}
            />
        );
    }

    const isDark = resolvedTheme === 'dark';

    return (
        <button
            role="switch"
            aria-checked={isDark}
            onClick={() => setTheme(isDark ? 'light' : 'dark')}
            className={cn(
                // Track
                'relative h-8 w-16 rounded-wobbly-lg',
                'border-2 border-border',
                'transition-colors duration-normal',
                isDark ? 'bg-accent-secondary' : 'bg-background-muted',
                // Focus
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-secondary focus-visible:ring-offset-2',
                className
            )}
            aria-label="Toggle dark mode"
        >
            {/* Thumb */}
            <span
                className={cn(
                    'absolute top-1 left-1',
                    'flex h-6 w-6 items-center justify-center',
                    'rounded-wobbly-circle bg-background-alt border-2 border-border',
                    'shadow-hand-sm',
                    'transition-transform duration-normal ease-bounce',
                    isDark ? 'translate-x-8' : 'translate-x-0'
                )}
            >
                {isDark ? (
                    <Moon size={14} strokeWidth={2.5} />
                ) : (
                    <Sun size={14} strokeWidth={2.5} />
                )}
            </span>
        </button>
    );
}
