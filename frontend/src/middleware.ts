import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { verifyToken } from '@/lib/auth'

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

export async function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl

    // Allow public paths
    if (publicPaths.some(path => pathname === path)) {
        return NextResponse.next()
    }

    // Check authentication
    const token = request.cookies.get('access_token')?.value

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
