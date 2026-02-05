import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

// Heading component
const headingVariants = cva('font-heading text-foreground', {
    variants: {
        level: {
            h1: 'text-5xl md:text-6xl',
            h2: 'text-4xl md:text-5xl',
            h3: 'text-3xl md:text-4xl',
            h4: 'text-2xl md:text-3xl',
            h5: 'text-xl md:text-2xl',
            h6: 'text-lg md:text-xl',
        },
        decoration: {
            none: '',
            underline: 'wavy-underline',
            rotate: 'inline-block rotate-subtle',
        },
    },
    defaultVariants: {
        level: 'h1',
        decoration: 'none',
    },
});

type HeadingLevel = 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';

export interface HeadingProps
    extends React.HTMLAttributes<HTMLHeadingElement>,
    VariantProps<typeof headingVariants> {
    as?: HeadingLevel;
}

const Heading = React.forwardRef<HTMLHeadingElement, HeadingProps>(
    ({ className, level = 'h1', as, decoration, children, ...props }, ref) => {
        const Component = as || level || 'h1';
        return (
            <Component
                ref={ref}
                className={cn(headingVariants({ level, decoration, className }))}
                {...props}
            >
                {children}
            </Component>
        );
    }
);
Heading.displayName = 'Heading';

// Text/Paragraph component
const textVariants = cva('font-body', {
    variants: {
        variant: {
            default: 'text-foreground',
            muted: 'text-foreground-muted',
            subtle: 'text-foreground-subtle',
            accent: 'text-accent',
        },
        size: {
            sm: 'text-base',
            md: 'text-lg',
            lg: 'text-xl',
            xl: 'text-2xl',
        },
        leading: {
            tight: 'leading-tight',
            normal: 'leading-normal',
            relaxed: 'leading-relaxed',
        },
    },
    defaultVariants: {
        variant: 'default',
        size: 'md',
        leading: 'normal',
    },
});

export interface TextProps
    extends React.HTMLAttributes<HTMLParagraphElement>,
    VariantProps<typeof textVariants> {
    as?: 'p' | 'span' | 'div';
}

const Text = React.forwardRef<HTMLParagraphElement, TextProps>(
    ({ className, variant, size, leading, as = 'p', ...props }, ref) => {
        const Component = as;
        return (
            <Component
                ref={ref}
                className={cn(textVariants({ variant, size, leading, className }))}
                {...props}
            />
        );
    }
);
Text.displayName = 'Text';

export { Heading, headingVariants, Text, textVariants };
