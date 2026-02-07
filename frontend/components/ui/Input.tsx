"use client";

import { InputHTMLAttributes, forwardRef } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  success?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, success, className = "", id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");

    const stateStyles = error
      ? "border-error focus:border-error focus:ring-error/20"
      : success
        ? "border-success focus:border-success focus:ring-success/20"
        : "border-border focus:border-primary focus:ring-primary/20";

    return (
      <div className="space-y-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-body-sm font-medium text-text-secondary"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={`
            w-full px-4 py-3 bg-bg-surface border rounded-input
            text-text-primary placeholder-text-muted
            focus:outline-none focus:ring-2
            transition-all duration-200
            min-h-touch
            ${stateStyles}
            ${className}
          `}
          {...props}
        />
        {error && (
          <p className="text-caption text-error animate-fade-in">{error}</p>
        )}
        {hint && !error && (
          <p className="text-caption text-text-muted">{hint}</p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";
