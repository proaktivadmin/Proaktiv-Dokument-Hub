import type { MetadataRoute } from 'next';

/**
 * Web App Manifest for PWA Support
 * 
 * Enables "Add to Home Screen" functionality for the Proaktiv Admin app.
 * Real estate brokers who use the app frequently can install it for
 * quick access without browser chrome.
 * 
 * @see https://nextjs.org/docs/app/guides/progressive-web-apps
 * @see https://web.dev/add-manifest/
 */
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Proaktiv Admin',
    short_name: 'Proaktiv',
    description: 'Administrasjon for Proaktiv dokumentmaler - Vitec Next integrasjon',
    start_url: '/',
    display: 'standalone',
    background_color: '#ffffff',
    theme_color: '#272630', // Proaktiv brand dark color
    orientation: 'portrait-primary',
    scope: '/',
    lang: 'nb-NO',
    categories: ['business', 'productivity'],
    icons: [
      {
        src: '/favicon.png',
        sizes: '192x192',
        type: 'image/png',
        purpose: 'any',
      },
      {
        src: '/favicon.png',
        sizes: '512x512',
        type: 'image/png',
        purpose: 'any',
      },
      {
        src: '/favicon.png',
        sizes: '192x192',
        type: 'image/png',
        purpose: 'maskable',
      },
    ],
    screenshots: [],
    shortcuts: [
      {
        name: 'Maler',
        short_name: 'Maler',
        description: 'Se alle dokumentmaler',
        url: '/templates',
      },
      {
        name: 'Ansatte',
        short_name: 'Ansatte',
        description: 'Administrer ansatte',
        url: '/employees',
      },
      {
        name: 'Kontorer',
        short_name: 'Kontorer',
        description: 'Administrer kontorer',
        url: '/offices',
      },
    ],
  };
}
