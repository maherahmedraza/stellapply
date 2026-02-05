import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
    ({ className, type, ...props }, ref) => {
        return (
            <input
                type={type}
                className={cn(
                    `flex h-12 w-full
                     bg-background-alt
                     border-2 border-border
                     px-4 py-2
                     font-body text-lg text-foreground
                     placeholder:text-foreground-subtle
                     wobbly-input
                     transition-all duration-200
                     focus:border-accent-secondary focus:ring-2 focus:ring-accent-secondary/20
                     focus-visible:outline-none
                     disabled:cursor-not-allowed disabled:opacity-50`,
                    className
                )}
                ref={ref}
                {...props}
            />
        )
    }
)
Input.displayName = "Input"

export { Input };
