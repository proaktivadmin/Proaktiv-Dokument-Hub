import { FileQuestion, Home, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

/**
 * Custom 404 page for the application.
 * Displayed when a user navigates to a route that doesn't exist.
 */
export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background px-4">
      <div className="mx-auto max-w-md text-center">
        <div className="mb-6 flex justify-center">
          <div className="rounded-full bg-muted p-4">
            <FileQuestion className="h-12 w-12 text-muted-foreground" />
          </div>
        </div>
        
        <h1 className="mb-2 text-6xl font-bold text-foreground">
          404
        </h1>
        
        <h2 className="mb-2 text-xl font-semibold text-foreground">
          Siden ble ikke funnet
        </h2>
        
        <p className="mb-8 text-muted-foreground">
          Beklager, vi fant ikke siden du leter etter. Den kan ha blitt flyttet eller slettet.
        </p>

        <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Button asChild variant="default" className="gap-2">
            <Link href="/">
              <Home className="h-4 w-4" />
              Gå til forsiden
            </Link>
          </Button>
          
          <Button asChild variant="outline" className="gap-2">
            <Link href="/templates">
              <ArrowLeft className="h-4 w-4" />
              Se alle maler
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
