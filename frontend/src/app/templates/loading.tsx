import { Skeleton } from '@/components/ui/skeleton';

/**
 * Loading state for the templates page.
 * Shows skeleton cards for the template shelf view.
 */
export default function TemplatesLoading() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header skeleton */}
      <div className="border-b bg-white">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Skeleton className="h-8 w-32" />
              <div className="hidden md:flex items-center gap-2">
                <Skeleton className="h-8 w-20" />
                <Skeleton className="h-8 w-20" />
                <Skeleton className="h-8 w-20" />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Skeleton className="h-9 w-24" />
              <Skeleton className="h-9 w-9 rounded-full" />
            </div>
          </div>
        </div>
      </div>

      <main className="container mx-auto px-6 py-8">
        {/* Page header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <Skeleton className="h-8 w-32 mb-2" />
            <Skeleton className="h-4 w-48" />
          </div>
          <div className="flex items-center gap-1 p-1 bg-gray-100 rounded-lg">
            <Skeleton className="h-8 w-16" />
            <Skeleton className="h-8 w-16" />
          </div>
        </div>

        {/* Template shelf skeleton */}
        <div className="bg-white rounded-md p-6 border" style={{ minHeight: '60vh' }}>
          {/* Shelf group */}
          {[1, 2].map((shelf) => (
            <div key={shelf} className="mb-8">
              {/* Shelf header */}
              <div className="flex items-center gap-3 mb-4">
                <Skeleton className="h-6 w-6 rounded" />
                <Skeleton className="h-6 w-40" />
                <Skeleton className="h-4 w-12 rounded-full" />
              </div>
              
              {/* Template cards in horizontal scroll */}
              <div className="flex gap-4 overflow-hidden">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div
                    key={i}
                    className="flex-shrink-0 w-48 bg-white rounded-lg border p-4"
                  >
                    {/* Thumbnail */}
                    <Skeleton className="h-32 w-full mb-3 rounded" />
                    {/* Title */}
                    <Skeleton className="h-4 w-3/4 mb-2" />
                    {/* Meta */}
                    <div className="flex items-center gap-2">
                      <Skeleton className="h-3 w-12" />
                      <Skeleton className="h-3 w-16" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
