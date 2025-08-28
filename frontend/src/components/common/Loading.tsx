import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../utils';

const loadingVariants = cva(
  'animate-spin rounded-full border-2 border-solid border-current border-r-transparent',
  {
    variants: {
      size: {
        xs: 'h-3 w-3',
        sm: 'h-4 w-4',
        md: 'h-6 w-6',
        lg: 'h-8 w-8',
        xl: 'h-12 w-12',
      },
      variant: {
        default: 'text-brand-600',
        light: 'text-white',
        dark: 'text-gray-900',
        muted: 'text-gray-400',
      },
    },
    defaultVariants: {
      size: 'md',
      variant: 'default',
    },
  }
);

export interface LoadingProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof loadingVariants> {
  text?: string;
  overlay?: boolean;
}

const Loading = React.forwardRef<HTMLDivElement, LoadingProps>(
  ({ className, size, variant, text, overlay, ...props }, ref) => {
    const spinner = (
      <div className={cn(loadingVariants({ size, variant }), className)} />
    );

    if (overlay) {
      return (
        <div
          ref={ref}
          className="fixed inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm"
          {...props}
        >
          <div className="flex flex-col items-center space-y-3">
            {spinner}
            {text && (
              <p className="text-sm font-medium text-gray-700">{text}</p>
            )}
          </div>
        </div>
      );
    }

    if (text) {
      return (
        <div
          ref={ref}
          className="flex items-center space-x-2"
          {...props}
        >
          {spinner}
          <span className="text-sm font-medium text-gray-700">{text}</span>
        </div>
      );
    }

    return (
      <div ref={ref} {...props}>
        {spinner}
      </div>
    );
  }
);

Loading.displayName = 'Loading';

// Skeleton component for content loading
export const Skeleton: React.FC<{
  className?: string;
  lines?: number;
}> = ({ className, lines = 1 }) => {
  return (
    <div className="animate-pulse">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={cn(
            'h-4 bg-gray-200 rounded mb-2 last:mb-0',
            i === lines - 1 && lines > 1 && 'w-3/4', // Last line shorter
            className
          )}
        />
      ))}
    </div>
  );
};

// Card skeleton for loading cards
export const CardSkeleton: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <div className={cn('card p-6 animate-pulse', className)}>
      <div className="flex items-center space-x-4 mb-4">
        <div className="h-10 w-10 bg-gray-200 rounded-full" />
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-gray-200 rounded w-3/4" />
          <div className="h-3 bg-gray-200 rounded w-1/2" />
        </div>
      </div>
      <div className="space-y-2">
        <div className="h-3 bg-gray-200 rounded" />
        <div className="h-3 bg-gray-200 rounded" />
        <div className="h-3 bg-gray-200 rounded w-5/6" />
      </div>
    </div>
  );
};

// Table skeleton for loading tables
export const TableSkeleton: React.FC<{ 
  rows?: number; 
  columns?: number;
  className?: string;
}> = ({ rows = 5, columns = 4, className }) => {
  return (
    <div className={cn('animate-pulse', className)}>
      {/* Header */}
      <div className="flex space-x-4 mb-4 pb-2 border-b border-gray-200">
        {Array.from({ length: columns }).map((_, i) => (
          <div key={i} className="flex-1 h-4 bg-gray-200 rounded" />
        ))}
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex space-x-4 mb-3">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <div key={colIndex} className="flex-1 h-3 bg-gray-200 rounded" />
          ))}
        </div>
      ))}
    </div>
  );
};

export { Loading, loadingVariants };