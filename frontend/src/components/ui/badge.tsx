import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
    [
        'inline-flex items-center justify-center',
        'font-body text-sm font-normal',
        'border-2',
        'wobbly-sm',
        'whitespace-nowrap',
    ],
    {
        variants: {
            variant: {
                default: 'border-border bg-background-muted text-foreground',
                primary: 'border-accent bg-accent/10 text-accent',
                secondary: 'border-accent-secondary bg-accent-secondary/10 text-accent-secondary',
                success: 'border-success bg-success/10 text-success',
                warning: 'border-warning bg-warning/10 text-warning',
                error: 'border-error bg-error/10 text-error',
                outline: 'border-border bg-transparent text-foreground',
            },
            size: {
                sm: 'h-5 px-2 text-xs',
                md: 'h-6 px-3 text-sm',
                lg: 'h-7 px-4 text-base',
            },
        },
        defaultVariants: {
            variant: 'default',
            size: 'md',
        },
    }
);

export interface BadgeProps
    extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> { }

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
    ({ className, variant, size, ...props }, ref) => {
        return (
            <div
                ref={ref}
                className={cn(badgeVariants({ variant, size, className }))}
                {...props}
            />
        );
    }
);
Badge.displayName = 'Badge';

export { Badge, badgeVariants };
