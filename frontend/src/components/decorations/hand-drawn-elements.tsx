import * as React from 'react';
import { cn } from '@/lib/utils';

// Squiggly line SVG path
export function SquigglyLine({
    className,
    color = 'currentColor'
}: {
    className?: string;
    color?: string;
}) {
    return (
        <svg
            className={cn('overflow-visible', className)}
            viewBox="0 0 200 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            preserveAspectRatio="none"
        >
            <path
                d="M0 10 Q 25 0, 50 10 T 100 10 T 150 10 T 200 10"
                stroke={color}
                strokeWidth="2"
                strokeLinecap="round"
                strokeDasharray="4 4"
                className="stroke-current"
            />
        </svg>
    );
}

// Hand-drawn arrow
export function HandDrawnArrow({
    className,
    direction = 'right',
}: {
    className?: string;
    direction?: 'left' | 'right' | 'up' | 'down';
}) {
    const rotations = {
        right: 'rotate-0',
        down: 'rotate-90',
        left: 'rotate-180',
        up: '-rotate-90',
    };

    return (
        <svg
            className={cn('overflow-visible', rotations[direction], className)}
            width="60"
            height="30"
            viewBox="0 0 60 30"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
        >
            <path
                d="M2 15 Q 10 13, 20 15 T 40 14 L 52 14 M 45 8 L 55 14 L 45 20"
                className="stroke-foreground"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeDasharray="4 2"
            />
        </svg>
    );
}

// Decorative star/sparkle
export function Sparkle({
    className,
    size = 24,
}: {
    className?: string;
    size?: number;
}) {
    return (
        <svg
            className={cn('animate-float', className)}
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
        >
            <path
                d="M12 2 L14 9 L21 12 L14 15 L12 22 L10 15 L3 12 L10 9 Z"
                className="fill-accent-warning stroke-foreground"
                strokeWidth="1.5"
                strokeLinejoin="round"
            />
        </svg>
    );
}

// Tape strip decoration
export function TapeStrip({
    className,
    rotation = -2,
}: {
    className?: string;
    rotation?: number;
}) {
    return (
        <div
            className={cn(
                'absolute w-16 h-5 bg-foreground/10 rounded-sm',
                className
            )}
            style={{ transform: `rotate(${rotation}deg)` }}
        />
    );
}

// Thumbtack decoration
export function Thumbtack({
    className,
    color = 'accent',
}: {
    className?: string;
    color?: 'accent' | 'secondary' | 'tertiary';
}) {
    const colorClasses = {
        accent: 'bg-accent',
        secondary: 'bg-accent-secondary',
        tertiary: 'bg-accent-tertiary',
    };

    return (
        <div
            className={cn(
                'w-4 h-4 rounded-full shadow-hand-sm',
                colorClasses[color],
                className
            )}
        />
    );
}

// Corner frame marks (for images/containers)
export function CornerMarks({
    className,
}: {
    className?: string;
}) {
    return (
        <>
            {/* Top Left */}
            <div className={cn('absolute -top-2 -left-2', className)}>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path
                        d="M2 18 V2 H18"
                        className="stroke-foreground"
                        strokeWidth="2"
                        strokeLinecap="round"
                    />
                </svg>
            </div>
            {/* Top Right */}
            <div className={cn('absolute -top-2 -right-2', className)}>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path
                        d="M2 2 H18 V18"
                        className="stroke-foreground"
                        strokeWidth="2"
                        strokeLinecap="round"
                    />
                </svg>
            </div>
            {/* Bottom Left */}
            <div className={cn('absolute -bottom-2 -left-2', className)}>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path
                        d="M2 2 V18 H18"
                        className="stroke-foreground"
                        strokeWidth="2"
                        strokeLinecap="round"
                    />
                </svg>
            </div>
            {/* Bottom Right */}
            <div className={cn('absolute -bottom-2 -right-2', className)}>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path
                        d="M18 2 V18 H2"
                        className="stroke-foreground"
                        strokeWidth="2"
                        strokeLinecap="round"
                    />
                </svg>
            </div>
        </>
    );
}

// Dashed circle highlight
export function DashedCircle({
    className,
    size = 100,
}: {
    className?: string;
    size?: number;
}) {
    return (
        <div
            className={cn(
                'absolute rounded-full border-2 border-dashed border-accent pointer-events-none',
                className
            )}
            style={{
                width: size,
                height: size,
            }}
        />
    );
}

// Post-it style tag
export function PostItTag({
    children,
    className,
    rotation = -3,
}: {
    children: React.ReactNode;
    className?: string;
    rotation?: number;
}) {
    return (
        <div
            className={cn(
                'inline-block px-3 py-1',
                'bg-background-accent border-2 border-border',
                'font-heading text-sm',
                'shadow-hand-sm',
                className
            )}
            style={{
                transform: `rotate(${rotation}deg)`,
                borderRadius: 'var(--radius-wobbly-sm)',
            }}
        >
            {children}
        </div>
    );
}
