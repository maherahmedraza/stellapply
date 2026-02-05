import type { Metadata } from 'next';
import { Kalam, Patrick_Hand, Caveat } from 'next/font/google';
import { ThemeProvider } from '@/components/providers/theme-provider';
import './globals.css';

// Heading font - thick marker style
const kalam = Kalam({
  weight: ['400', '700'],
  subsets: ['latin'],
  variable: '--font-heading',
  display: 'swap',
});

// Body font - legible handwriting
const patrickHand = Patrick_Hand({
  weight: ['400'],
  subsets: ['latin'],
  variable: '--font-body',
  display: 'swap',
});

// Accent font - for special elements
const caveat = Caveat({
  weight: ['400', '700'],
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'StellarApply.ai - Launch Your Career to New Heights',
  description: 'AI-powered job search and application automation platform',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${kalam.variable} ${patrickHand.variable} ${caveat.variable}`}
    >
      <body className="min-h-screen font-body antialiased">
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
