import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { verifyToken } from '@/lib/auth'

const publicPaths = ['/', '/auth/login', '/auth/register', '/forgot-password', '/privacy', '/terms', '/support']

export async function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl

    // Check authentication
    const token = request.cookies.get('access_token')?.value
    const isAuthPath = pathname === '/auth/login' || pathname === '/auth/register'

    // 1. Redirect authenticated users away from public auth pages
    if (token && isAuthPath) {
        return NextResponse.redirect(new URL('/dashboard', request.url))
    }

    // 2. Allow other public paths (Home, etc.) OR auth paths for unauthenticated users
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
