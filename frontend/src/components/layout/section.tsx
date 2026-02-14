import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const sectionVariants = cva('w-full', {
    variants: {
        padding: {
            none: 'py-0',
            sm: 'py-8 md:py-12',
            md: 'py-12 md:py-16',
            lg: 'py-16 md:py-20',
            xl: 'py-20 md:py-24',
        },
        background: {
            transparent: 'bg-transparent',
            default: 'bg-background',
            alt: 'bg-background-alt',
            muted: 'bg-background-muted',
            accent: 'bg-background-accent',
        },
    },
    defaultVariants: {
        padding: 'lg',
        background: 'transparent',
    },
});

export interface SectionProps
    extends React.HTMLAttributes<HTMLElement>,
    VariantProps<typeof sectionVariants> {
    as?: 'section' | 'div' | 'article' | 'main' | 'aside';
}

const Section = React.forwardRef<HTMLElement, SectionProps>(
    ({ className, padding, background, as = 'section', ...props }, ref) => {
        const Component = as;
        return (
            <Component
                ref={ref as React.Ref<HTMLDivElement>}
                className={cn(sectionVariants({ padding, background, className }))}
                {...props}
            />
        );
    }
);
Section.displayName = 'Section';

export { Section, sectionVariants };
