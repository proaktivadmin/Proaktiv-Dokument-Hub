'use client';

/**
 * Web Vitals Analytics Component
 * 
 * Reports Core Web Vitals metrics for performance monitoring.
 * When deployed on Vercel, these metrics are automatically collected
 * in the Speed Insights dashboard.
 * 
 * Metrics tracked:
 * - LCP (Largest Contentful Paint) - Loading performance
 * - FID (First Input Delay) - Interactivity  
 * - CLS (Cumulative Layout Shift) - Visual stability
 * - TTFB (Time to First Byte) - Server response time
 * - FCP (First Contentful Paint) - Initial render time
 * - INP (Interaction to Next Paint) - Responsiveness
 * 
 * @see https://nextjs.org/docs/app/guides/analytics
 * @see https://web.dev/vitals/
 */

import { useReportWebVitals } from 'next/web-vitals';

export function WebVitals() {
  useReportWebVitals((metric) => {
    // Log to console in development for debugging
    if (process.env.NODE_ENV === 'development') {
      console.log(`[Web Vital] ${metric.name}:`, {
        value: metric.value,
        rating: metric.rating, // 'good', 'needs-improvement', or 'poor'
        delta: metric.delta,
        id: metric.id,
      });
    }

    // Send to analytics endpoint (optional - Vercel collects automatically)
    // You can also send to your own analytics service here
    // Uncomment to send to your own analytics endpoint:
    // const body = JSON.stringify({
    //   name: metric.name,
    //   value: metric.value,
    //   rating: metric.rating,
    //   delta: metric.delta,
    //   id: metric.id,
    //   page: window.location.pathname,
    // });
    // navigator.sendBeacon?.('/api/analytics/vitals', body);
  });

  return null;
}
