import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const textareaVariants = cva(
    [
        'flex w-full min-h-[120px]',
        'font-body text-lg',
        'bg-background-alt text-foreground',
        'placeholder:text-foreground-subtle',
        'border-2 border-border',
        'wobbly-md',
        'resize-none',
        'transition-all duration-fast',
        'focus:outline-none focus:border-accent-secondary focus:ring-2 focus:ring-accent-secondary/20',
        'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-background-muted',
    ],
    {
        variants: {
            size: {
                sm: 'p-3 text-base',
                md: 'p-4 text-lg',
                lg: 'p-5 text-xl',
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

export interface TextareaProps
    extends React.TextareaHTMLAttributes<HTMLTextAreaElement>,
    VariantProps<typeof textareaVariants> { }

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
    ({ className, size, hasError, ...props }, ref) => {
        return (
            <textarea
                className={cn(textareaVariants({ size, hasError, className }))}
                ref={ref}
                {...props}
            />
        );
    }
);
Textarea.displayName = 'Textarea';

export { Textarea, textareaVariants };
