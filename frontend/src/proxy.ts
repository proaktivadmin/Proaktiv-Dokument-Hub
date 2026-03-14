/**
 * Next.js Proxy for Route Protection
 *
 * Provides server-side authentication checks for protected routes.
 * This is an optimistic check using the session cookie - the actual
 * JWT validation happens on the backend API.
 *
 * Note: Renamed from middleware.ts per Next.js 16 convention.
 *
 * @see https://nextjs.org/docs/messages/middleware-to-proxy
 */

import { NextRequest, NextResponse } from 'next/server';

// Routes that require authentication
const PROTECTED_ROUTES = [
  '/templates',
  '/employees',
  '/offices',
  '/storage',
  '/categories',
  '/flettekoder',
  '/mottakere',
  '/territories',
  '/sync',
  '/sanitizer',
];

// Routes that are always public
const PUBLIC_ROUTES = ['/login'];

// Session cookie name (must match backend)
const SESSION_COOKIE = 'session';

function isProtectedRoute(pathname: string): boolean {
  if (pathname === '/') return true;
  return PROTECTED_ROUTES.some((route) =>
    pathname === route || pathname.startsWith(`${route}/`)
  );
}

function isPublicRoute(pathname: string): boolean {
  return PUBLIC_ROUTES.includes(pathname);
}

export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.includes('.')
  ) {
    return NextResponse.next();
  }

  const sessionCookie = request.cookies.get(SESSION_COOKIE)?.value;
  const hasSession = Boolean(sessionCookie);

  if (isProtectedRoute(pathname) && !hasSession) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('returnTo', pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (isPublicRoute(pathname) && hasSession) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|favicon.png|.*\\.png$|.*\\.jpg$|.*\\.svg$).*)',
  ],
};
