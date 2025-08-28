import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../utils';

const inputVariants = cva(
  'block w-full rounded-lg border transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-0 disabled:cursor-not-allowed disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'border-gray-300 bg-white text-gray-900 placeholder-gray-400 focus:border-brand-500 focus:ring-brand-500',
        error: 'border-red-300 bg-white text-gray-900 placeholder-gray-400 focus:border-red-500 focus:ring-red-500',
        success: 'border-green-300 bg-white text-gray-900 placeholder-gray-400 focus:border-green-500 focus:ring-green-500',
      },
      size: {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-3 py-2 text-sm',
        lg: 'px-4 py-3 text-base',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  }
);

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement>,
    VariantProps<typeof inputVariants> {
  label?: string;
  error?: string;
  helpText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  leftElement?: React.ReactNode;
  rightElement?: React.ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({
    className,
    variant,
    size,
    label,
    error,
    helpText,
    leftIcon,
    rightIcon,
    leftElement,
    rightElement,
    id,
    ...props
  }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    const hasError = !!error;
    const effectiveVariant = hasError ? 'error' : variant;

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-gray-700 mb-1">
            {label}
          </label>
        )}
        
        <div className="relative">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="text-gray-400">{leftIcon}</span>
            </div>
          )}
          
          {leftElement && (
            <div className="absolute inset-y-0 left-0 flex items-center">
              {leftElement}
            </div>
          )}
          
          <input
            id={inputId}
            ref={ref}
            className={cn(
              inputVariants({ variant: effectiveVariant, size }),
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              leftElement && 'pl-12',
              rightElement && 'pr-12',
              className
            )}
            {...props}
          />
          
          {rightIcon && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <span className="text-gray-400">{rightIcon}</span>
            </div>
          )}
          
          {rightElement && (
            <div className="absolute inset-y-0 right-0 flex items-center">
              {rightElement}
            </div>
          )}
        </div>
        
        {error && (
          <p className="mt-1 text-sm text-red-600" role="alert">
            {error}
          </p>
        )}
        
        {helpText && !error && (
          <p className="mt-1 text-sm text-gray-500">
            {helpText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input, inputVariants };