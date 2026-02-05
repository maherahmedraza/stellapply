import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { verifyToken } from '@/lib/auth'

<<<<<<< HEAD
const publicPaths = [
    '/',
    '/auth/login',
    '/auth/register',
    '/forgot-password',
    '/features',
    '/pricing',
    '/about',
    '/blog',
    '/privacy',
    '/terms',
    '/support',
    '/contact'
]
=======
const publicPaths = ['/', '/auth/login', '/auth/register', '/forgot-password', '/privacy', '/terms', '/support']
>>>>>>> feature/resume-upload-gdpr-compliance

export async function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl

<<<<<<< HEAD
    // Allow public paths
=======
    // Check authentication
    const token = request.cookies.get('access_token')?.value
    const isAuthPath = pathname === '/auth/login' || pathname === '/auth/register'

    // 1. Redirect authenticated users away from public auth pages
    if (token && isAuthPath) {
        return NextResponse.redirect(new URL('/dashboard', request.url))
    }

    // 2. Allow other public paths (Home, etc.) OR auth paths for unauthenticated users
>>>>>>> feature/resume-upload-gdpr-compliance
    if (publicPaths.some(path => pathname === path)) {
        return NextResponse.next()
    }

    // 3. Protect all other routes
    if (!token) {
        return NextResponse.redirect(new URL('/auth/login', request.url))
    }

    try {
        if (!token) throw new Error("No token")
        return NextResponse.next()
    } catch {
        return NextResponse.redirect(new URL('/auth/login', request.url))
    }
}

export const config = {
    matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
