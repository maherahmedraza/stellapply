import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
    // Base styles - applied to all buttons
    [
        // Layout
        'inline-flex items-center justify-center gap-2',
        // Typography
        'font-body text-lg font-normal',
        // Borders - always wobbly
        'border-2 border-border',
        // Transitions
        'transition-all duration-fast',
        // Focus
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-secondary focus-visible:ring-offset-2',
        // Disabled
        'disabled:pointer-events-none disabled:opacity-50',
        // Default wobbly radius
        'wobbly-sm',
    ],
    {
        variants: {
            variant: {
                // Primary - fills with accent on hover
                default: [
                    'bg-background-alt text-foreground',
                    'shadow-hand-md',
                    'hover:bg-accent hover:text-background-alt hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-hand-lg',
                    'active:translate-x-1 active:translate-y-1 active:shadow-hand-none',
                ],
                // Secondary - muted background
                secondary: [
                    'bg-background-muted text-foreground',
                    'shadow-hand-md',
                    'hover:bg-accent-secondary hover:text-background-alt hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-hand-lg',
                    'active:translate-x-1 active:translate-y-1 active:shadow-hand-none',
                ],
                // Destructive - for dangerous actions
                destructive: [
                    'bg-error/10 text-error border-error',
                    'shadow-[4px_4px_0px_0px_rgb(var(--color-error))]',
                    'hover:bg-error hover:text-background-alt hover:-translate-x-0.5 hover:-translate-y-0.5',
                    'active:translate-x-1 active:translate-y-1 active:shadow-hand-none',
                ],
                // Outline - transparent background
                outline: [
                    'bg-transparent text-foreground',
                    'shadow-hand-sm',
                    'hover:bg-background-muted hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-hand-md',
                    'active:translate-x-1 active:translate-y-1 active:shadow-hand-none',
                ],
                // Ghost - no border or shadow
                ghost: [
                    'border-transparent bg-transparent text-foreground',
                    'shadow-none',
                    'hover:bg-background-muted hover:border-border',
                    'active:bg-background-muted/80',
                ],
                // Link - text only
                link: [
                    'border-transparent bg-transparent text-accent-secondary',
                    'shadow-none underline-offset-4',
                    'hover:underline hover:text-accent',
                    'active:text-accent/80',
                ],
            },
            size: {
                sm: 'h-9 px-3 text-base',
                md: 'h-11 px-5 text-lg',
                lg: 'h-14 px-8 text-xl',
                xl: 'h-16 px-10 text-2xl',
                icon: 'h-10 w-10 p-0',
                'icon-sm': 'h-8 w-8 p-0',
                'icon-lg': 'h-12 w-12 p-0',
            },
        },
        defaultVariants: {
            variant: 'default',
            size: 'md',
        },
    }
);

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
    asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant, size, asChild = false, ...props }, ref) => {
        const Comp = asChild ? Slot : 'button';
        return (
            <Comp
                className={cn(buttonVariants({ variant, size, className }))}
                ref={ref}
                {...props}
            />
        );
    }
);
Button.displayName = 'Button';

export { Button, buttonVariants };
