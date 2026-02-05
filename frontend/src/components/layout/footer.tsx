import Link from 'next/link';
import { Rocket, Heart } from 'lucide-react';
import { Container } from './container';
import { cn } from '@/lib/utils';

const footerLinks = {
    product: [
        { label: 'Features', href: '/features' },
        { label: 'Pricing', href: '/pricing' },
        { label: 'Changelog', href: '/changelog' },
        { label: 'Roadmap', href: '/roadmap' },
    ],
    company: [
        { label: 'About', href: '/about' },
        { label: 'Blog', href: '/blog' },
        { label: 'Careers', href: '/careers' },
        { label: 'Contact', href: '/contact' },
    ],
    legal: [
        { label: 'Privacy', href: '/privacy' },
        { label: 'Terms', href: '/terms' },
        { label: 'GDPR', href: '/gdpr' },
    ],
};

export function Footer() {
    return (
        <footer className="border-t-2 border-border bg-background-alt">
            <Container>
                <div className="py-12 md:py-16">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                        {/* Brand */}
                        <div className="col-span-2 md:col-span-1">
                            <Link href="/" className="flex items-center gap-2 mb-4">
                                <div className="flex h-10 w-10 items-center justify-center rounded-wobbly-circle border-2 border-border bg-accent shadow-hand-sm">
                                    <Rocket className="h-5 w-5 text-background-alt" strokeWidth={2.5} />
                                </div>
                                <span className="font-heading text-xl text-foreground">
                                    StellarApply
                                </span>
                            </Link>
                            <p className="text-foreground-muted text-base">
                                Launch your career to new heights with AI-powered job applications.
                            </p>
                        </div>

                        {/* Product Links */}
                        <div>
                            <h4 className="font-heading text-lg text-foreground mb-4 wavy-underline inline-block">
                                Product
                            </h4>
                            <ul className="space-y-2">
                                {footerLinks.product.map((link) => (
                                    <li key={link.href}>
                                        <Link
                                            href={link.href}
                                            className={cn(
                                                'text-foreground-muted hover:text-foreground',
                                                'transition-colors duration-fast',
                                                'hover:line-through decoration-accent decoration-2'
                                            )}
                                        >
                                            {link.label}
                                        </Link>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        {/* Company Links */}
                        <div>
                            <h4 className="font-heading text-lg text-foreground mb-4 wavy-underline inline-block">
                                Company
                            </h4>
                            <ul className="space-y-2">
                                {footerLinks.company.map((link) => (
                                    <li key={link.href}>
                                        <Link
                                            href={link.href}
                                            className={cn(
                                                'text-foreground-muted hover:text-foreground',
                                                'transition-colors duration-fast',
                                                'hover:line-through decoration-accent decoration-2'
                                            )}
                                        >
                                            {link.label}
                                        </Link>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        {/* Legal Links */}
                        <div>
                            <h4 className="font-heading text-lg text-foreground mb-4 wavy-underline inline-block">
                                Legal
                            </h4>
                            <ul className="space-y-2">
                                {footerLinks.legal.map((link) => (
                                    <li key={link.href}>
                                        <Link
                                            href={link.href}
                                            className={cn(
                                                'text-foreground-muted hover:text-foreground',
                                                'transition-colors duration-fast',
                                                'hover:line-through decoration-accent decoration-2'
                                            )}
                                        >
                                            {link.label}
                                        </Link>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>

                {/* Copyright */}
                <div className="border-t-2 border-dashed border-border py-6">
                    <p className="text-center text-foreground-muted text-base flex items-center justify-center gap-1">
                        Made with <Heart className="h-4 w-4 text-accent fill-accent" strokeWidth={2.5} /> by the StellarApply team
                        <span className="mx-2">•</span>
                        © {new Date().getFullYear()}
                    </p>
                </div>
            </Container>
        </footer>
    );
}
