import type { Config } from 'tailwindcss';

const config: Config = {
    darkMode: 'class',
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            /* ============================================
               COLORS - Mapped to CSS Custom Properties
               ============================================ */
            colors: {
                // Base colors
                background: {
                    DEFAULT: 'rgb(var(--color-background) / <alpha-value>)',
                    alt: 'rgb(var(--color-background-alt) / <alpha-value>)',
                    muted: 'rgb(var(--color-background-muted) / <alpha-value>)',
                    accent: 'rgb(var(--color-background-accent) / <alpha-value>)',
                },
                foreground: {
                    DEFAULT: 'rgb(var(--color-foreground) / <alpha-value>)',
                    muted: 'rgb(var(--color-foreground-muted) / <alpha-value>)',
                    subtle: 'rgb(var(--color-foreground-subtle) / <alpha-value>)',
                },
                accent: {
                    DEFAULT: 'rgb(var(--color-accent-primary) / <alpha-value>)',
                    primary: 'rgb(var(--color-accent-primary) / <alpha-value>)',
                    secondary: 'rgb(var(--color-accent-secondary) / <alpha-value>)',
                    tertiary: 'rgb(var(--color-accent-tertiary) / <alpha-value>)',
                    warning: 'rgb(var(--color-accent-warning) / <alpha-value>)',
                },
                border: {
                    DEFAULT: 'rgb(var(--color-border) / <alpha-value>)',
                    muted: 'rgb(var(--color-border-muted) / <alpha-value>)',
                    accent: 'rgb(var(--color-border-accent) / <alpha-value>)',
                },
                // Semantic colors
                success: 'rgb(var(--color-success) / <alpha-value>)',
                error: 'rgb(var(--color-error) / <alpha-value>)',
                warning: 'rgb(var(--color-warning) / <alpha-value>)',
                info: 'rgb(var(--color-info) / <alpha-value>)',
            },

            /* ============================================
               TYPOGRAPHY
               ============================================ */
            fontFamily: {
                heading: ['var(--font-heading)', 'cursive'],
                body: ['var(--font-body)', 'cursive'],
                mono: ['var(--font-mono)', 'cursive'],
            },
            fontSize: {
                // Slightly larger sizes for hand-drawn readability
                xs: ['0.875rem', { lineHeight: '1.25rem' }],
                sm: ['1rem', { lineHeight: '1.5rem' }],
                base: ['1.125rem', { lineHeight: '1.75rem' }],
                lg: ['1.25rem', { lineHeight: '1.75rem' }],
                xl: ['1.5rem', { lineHeight: '2rem' }],
                '2xl': ['1.875rem', { lineHeight: '2.25rem' }],
                '3xl': ['2.25rem', { lineHeight: '2.5rem' }],
                '4xl': ['3rem', { lineHeight: '1.2' }],
                '5xl': ['3.75rem', { lineHeight: '1.1' }],
                '6xl': ['4.5rem', { lineHeight: '1.1' }],
            },

            /* ============================================
               SPACING
               ============================================ */
            spacing: {
                section: 'var(--spacing-section)',
            },

            /* ============================================
               BORDER RADIUS - Wobbly values
               ============================================ */
            borderRadius: {
                'wobbly-sm': 'var(--radius-wobbly-sm)',
                'wobbly-md': 'var(--radius-wobbly-md)',
                'wobbly-lg': 'var(--radius-wobbly-lg)',
                'wobbly-xl': 'var(--radius-wobbly-xl)',
                'wobbly-circle': 'var(--radius-wobbly-circle)',
                'wobbly-blob': 'var(--radius-wobbly-blob)',
            },

            /* ============================================
               BOX SHADOW - Hard offset shadows
               ============================================ */
            boxShadow: {
                'hand-sm': 'var(--shadow-sm)',
                'hand-md': 'var(--shadow-md)',
                'hand-lg': 'var(--shadow-lg)',
                'hand-xl': 'var(--shadow-xl)',
                'hand-soft': 'var(--shadow-soft-md)',
                'hand-accent': 'var(--shadow-accent)',
                'hand-secondary': 'var(--shadow-secondary)',
                // Pressed state - no shadow
                'hand-none': 'none',
            },

            /* ============================================
               TRANSITIONS
               ============================================ */
            transitionDuration: {
                fast: '100ms',
                normal: '200ms',
                slow: '300ms',
            },
            transitionTimingFunction: {
                bounce: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
            },

            /* ============================================
               Z-INDEX
               ============================================ */
            zIndex: {
                below: '-1',
                above: '10',
                dropdown: '100',
                sticky: '200',
                modal: '300',
                popover: '400',
                tooltip: '500',
                toast: '600',
            },

            /* ============================================
               ROTATE - Playful rotations
               ============================================ */
            rotate: {
                subtle: 'var(--rotate-subtle)',
                medium: 'var(--rotate-medium)',
                playful: 'var(--rotate-playful)',
            },

            /* ============================================
               ANIMATIONS
               ============================================ */
            animation: {
                'bounce-gentle': 'bounce-gentle 3s ease-in-out infinite',
                wiggle: 'wiggle 0.5s ease-in-out',
                float: 'float 4s ease-in-out infinite',
            },
            keyframes: {
                'bounce-gentle': {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                },
                wiggle: {
                    '0%, 100%': { transform: 'rotate(-2deg)' },
                    '50%': { transform: 'rotate(2deg)' },
                },
                float: {
                    '0%, 100%': { transform: 'translateY(0) rotate(0deg)' },
                    '33%': { transform: 'translateY(-5px) rotate(1deg)' },
                    '66%': { transform: 'translateY(3px) rotate(-1deg)' },
                },
            },

            /* ============================================
               BORDER WIDTH
               ============================================ */
            borderWidth: {
                3: '3px',
            },
        },
    },
    plugins: [],
};

export default config;
