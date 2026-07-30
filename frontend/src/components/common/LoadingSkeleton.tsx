export function LoadingSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={`animate-pulse bg-slate-200 dark:bg-slate-800 rounded-md ${className}`}></div>
  );
}

export function CardSkeleton() {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 w-full">
      <div className="flex justify-between items-start mb-4">
        <LoadingSkeleton className="h-4 w-24" />
        <LoadingSkeleton className="h-8 w-8 rounded-lg" />
      </div>
      <div className="flex items-end justify-between">
        <LoadingSkeleton className="h-8 w-16" />
        <LoadingSkeleton className="h-4 w-12" />
      </div>
    </div>
  );
}
