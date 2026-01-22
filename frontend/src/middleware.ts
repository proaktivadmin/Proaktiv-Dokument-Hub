/**
 * Next.js Middleware for Route Protection
 * 
 * Provides server-side authentication checks for protected routes.
 * This is an optimistic check using the session cookie - the actual
 * JWT validation happens on the backend API.
 * 
 * Benefits:
 * - Faster redirects (no client-side JS execution needed)
 * - Better SEO (authenticated pages don't flash)
 * - Defense in depth (multiple layers of protection)
 * 
 * Note: This is a lightweight check. Full auth validation still
 * happens via the AuthProvider and backend API.
 * 
 * @see https://nextjs.org/docs/app/guides/authentication
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

/**
 * Check if the path matches a protected route prefix
 */
function isProtectedRoute(pathname: string): boolean {
  // Dashboard (root) is protected
  if (pathname === '/') {
    return true;
  }
  
  return PROTECTED_ROUTES.some((route) => 
    pathname === route || pathname.startsWith(`${route}/`)
  );
}

/**
 * Check if the path is a public route
 */
function isPublicRoute(pathname: string): boolean {
  return PUBLIC_ROUTES.includes(pathname);
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Skip middleware for static files, API routes, and Next.js internals
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.includes('.') // Static files (images, fonts, etc.)
  ) {
    return NextResponse.next();
  }

  // Check for session cookie
  const sessionCookie = request.cookies.get(SESSION_COOKIE)?.value;
  const hasSession = Boolean(sessionCookie);

  // Redirect logic for protected routes
  if (isProtectedRoute(pathname) && !hasSession) {
    // User is not authenticated - redirect to login
    const loginUrl = new URL('/login', request.url);
    // Optionally add return URL for post-login redirect
    loginUrl.searchParams.set('returnTo', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Redirect authenticated users away from login page
  if (isPublicRoute(pathname) && hasSession) {
    // User is already authenticated - redirect to dashboard
    return NextResponse.redirect(new URL('/', request.url));
  }

  return NextResponse.next();
}

// Configure which paths the middleware should run on
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico, favicon.png (favicon files)
     * - public folder files
     */
    '/((?!_next/static|_next/image|favicon.ico|favicon.png|.*\\.png$|.*\\.jpg$|.*\\.svg$).*)',
  ],
};
