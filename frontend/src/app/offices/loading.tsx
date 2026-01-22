import { Skeleton } from '@/components/ui/skeleton';

/**
 * Loading state for the offices page.
 * Shows skeleton cards for office grid with banner images.
 */
export default function OfficesLoading() {
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
        <div className="mb-8">
          <Skeleton className="h-8 w-32 mb-2" />
          <Skeleton className="h-4 w-72" />
        </div>

        {/* Toolbar */}
        <div className="flex items-center justify-between mb-6">
          <Skeleton className="h-4 w-24" />
          <div className="flex gap-2">
            <Skeleton className="h-9 w-28" />
            <Skeleton className="h-9 w-24" />
          </div>
        </div>

        {/* Office grid skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-white rounded-lg border overflow-hidden">
              {/* Banner image */}
              <Skeleton className="h-32 w-full" />
              
              <div className="p-4">
                {/* Office name */}
                <Skeleton className="h-6 w-40 mb-2" />
                
                {/* Address */}
                <Skeleton className="h-4 w-48 mb-3" />
                
                {/* Stats */}
                <div className="flex items-center gap-4 mb-4">
                  <div className="flex items-center gap-1">
                    <Skeleton className="h-4 w-4" />
                    <Skeleton className="h-4 w-16" />
                  </div>
                  <div className="flex items-center gap-1">
                    <Skeleton className="h-4 w-4" />
                    <Skeleton className="h-4 w-20" />
                  </div>
                </div>
                
                {/* Employee avatars */}
                <div className="flex -space-x-2">
                  {Array.from({ length: 4 }).map((_, j) => (
                    <Skeleton key={j} className="h-8 w-8 rounded-full border-2 border-white" />
                  ))}
                  <Skeleton className="h-8 w-8 rounded-full border-2 border-white" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
