import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
    // Base styles
    `inline-flex items-center justify-center gap-2
     font-heading font-bold
     border-[3px] border-border
     transition-all duration-100
     focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/50
     disabled:pointer-events-none disabled:opacity-50
     active:translate-x-[4px] active:translate-y-[4px] active:shadow-none`,
    {
        variants: {
            variant: {
                default: `
                    bg-background-alt text-foreground
                    shadow-hand-md
                    hover:bg-accent hover:text-white hover:border-accent
                    hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-hand-sm
                `,
                primary: `
                    bg-accent text-white border-accent
                    shadow-hand-md
                    hover:bg-accent-hover
                    hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-hand-sm
                `,
                secondary: `
                    bg-background-muted text-foreground
                    shadow-hand-md
                    hover:bg-accent-secondary hover:text-white hover:border-accent-secondary
                    hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-hand-sm
                `,
                outline: `
                    bg-transparent text-foreground
                    shadow-none border-dashed
                    hover:bg-background-muted hover:border-solid
                `,
                ghost: `
                    bg-transparent text-foreground
                    border-transparent shadow-none
                    hover:bg-background-muted hover:border-border-muted
                `,
                destructive: `
                    bg-error text-white border-error
                    shadow-hand-md
                    hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-hand-sm
                `,
            },
            size: {
                default: "h-12 px-6 py-2 text-lg",
                sm: "h-9 px-4 py-1 text-base",
                lg: "h-14 px-8 py-3 text-xl",
                icon: "h-10 w-10 p-0",
            },
        },
        defaultVariants: {
            variant: "default",
            size: "default",
        },
    }
)

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
    asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant, size, asChild = false, ...props }, ref) => {
        const Comp = asChild ? Slot : "button"

        return (
            <Comp
                className={cn(buttonVariants({ variant, size }), "wobbly-button", className)}
                ref={ref}
                {...props}
            />
        )
    }
)
Button.displayName = "Button"

export { Button, buttonVariants };
