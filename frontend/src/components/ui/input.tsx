import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const inputVariants = cva(
    // Base styles
    [
        'flex w-full',
        'font-body text-lg',
        'bg-background-alt text-foreground',
        'placeholder:text-foreground-subtle',
        'border-2 border-border',
        'wobbly-sm',
        'transition-all duration-fast',
        // Focus
        'focus:outline-none focus:border-accent-secondary focus:ring-2 focus:ring-accent-secondary/20',
        // Disabled
        'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-background-muted',
        // File input
        'file:border-0 file:bg-transparent file:text-sm file:font-medium',
    ],
    {
        variants: {
            size: {
                sm: 'h-9 px-3 text-base',
                md: 'h-11 px-4 text-lg',
                lg: 'h-14 px-5 text-xl',
            },
            hasError: {
                true: 'border-error focus:border-error focus:ring-error/20',
                false: '',
            },
        },
        defaultVariants: {
            size: 'md',
            hasError: false,
        },
    }
);

export interface InputProps
    extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'>,
    VariantProps<typeof inputVariants> { }

const Input = React.forwardRef<HTMLInputElement, InputProps>(
    ({ className, type, size, hasError, ...props }, ref) => {
        return (
            <input
                type={type}
                className={cn(inputVariants({ size, hasError, className }))}
                ref={ref}
                {...props}
            />
        );
    }
);
Input.displayName = 'Input';

export { Input, inputVariants };
