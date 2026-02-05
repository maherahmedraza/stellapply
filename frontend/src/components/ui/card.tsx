import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const cardVariants = cva(
    // Base styles
    [
        'relative',
        'bg-background-alt',
        'border-2 border-border',
        'wobbly-md',
        'transition-all duration-fast',
    ],
    {
        variants: {
            variant: {
                default: 'shadow-hand-soft',
                elevated: 'shadow-hand-md hover:shadow-hand-lg hover:-translate-y-1',
                flat: 'shadow-none',
                accent: 'bg-background-accent border-accent-warning shadow-hand-md',
            },
            padding: {
                none: 'p-0',
                sm: 'p-4',
                md: 'p-6',
                lg: 'p-8',
            },
            decoration: {
                none: '',
                tape: 'decoration-tape',
                tack: 'decoration-tack',
            },
        },
        defaultVariants: {
            variant: 'default',
            padding: 'md',
            decoration: 'none',
        },
    }
);

export interface CardProps
    extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> { }

const Card = React.forwardRef<HTMLDivElement, CardProps>(
    ({ className, variant, padding, decoration, ...props }, ref) => (
        <div
            ref={ref}
            className={cn(cardVariants({ variant, padding, decoration, className }))}
            {...props}
        />
    )
);
Card.displayName = 'Card';

const CardHeader = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
    <div
        ref={ref}
        className={cn('flex flex-col space-y-2 pb-4', className)}
        {...props}
    />
));
CardHeader.displayName = 'CardHeader';

const CardTitle = React.forwardRef<
    HTMLHeadingElement,
    React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
    <h3
        ref={ref}
        className={cn('font-heading text-2xl text-foreground', className)}
        {...props}
    />
));
CardTitle.displayName = 'CardTitle';

const CardDescription = React.forwardRef<
    HTMLParagraphElement,
    React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
    <p
        ref={ref}
        className={cn('text-foreground-muted', className)}
        {...props}
    />
));
CardDescription.displayName = 'CardDescription';

const CardContent = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
    <div ref={ref} className={cn('', className)} {...props} />
));
CardContent.displayName = 'CardContent';

const CardFooter = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
    <div
        ref={ref}
        className={cn('flex items-center pt-4', className)}
        {...props}
    />
));
CardFooter.displayName = 'CardFooter';

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent, cardVariants };
