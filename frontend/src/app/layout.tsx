import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Providers } from '@/components/providers'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'StellarApply.ai - Your AI-Powered Job Search Assistant',
  description: 'Stop searching, start working. StellarApply.ai automates your job search with AI-powered matching, resume optimization, and auto-apply.',
  keywords: ['job search', 'AI resume', 'auto apply', 'career'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
