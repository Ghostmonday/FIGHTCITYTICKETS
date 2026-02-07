"use client";

import { HTMLAttributes } from "react";

interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  variant?: "success" | "error" | "warning" | "info";
  title?: string;
  dismissible?: boolean;
  onDismiss?: () => void;
}

export function Alert({
  variant = "info",
  title,
  children,
  className = "",
  dismissible = false,
  onDismiss,
  ...props
}: AlertProps) {
  const variantStyles = {
    success: "bg-success-bg border-success-border text-success",
    error: "bg-error-bg border-error-border text-error",
    warning: "bg-warning-bg border-warning-border text-warning",
    info: "bg-bg-subtle border-border text-text-secondary",
  };

  const iconPaths = {
    success: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
    error:
      "M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z",
    warning:
      "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z",
    info: "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
  };

  const iconColors = {
    success: "text-success",
    error: "text-error",
    warning: "text-warning",
    info: "text-text-secondary",
  };

  return (
    <div
      className={`
        rounded-lg border p-4 animate-fade-in
        ${variantStyles[variant]}
        ${className}
      `}
      role="alert"
      {...props}
    >
      <div className="flex items-start gap-3">
        <svg
          className={`w-5 h-5 flex-shrink-0 mt-0.5 ${iconColors[variant]}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d={iconPaths[variant]}
          />
        </svg>
        <div className="flex-1">
          {title && (
            <h4 className="font-medium text-text-primary mb-1">{title}</h4>
          )}
          <div className={title ? "text-sm" : "text-sm"}>{children}</div>
        </div>
        {dismissible && onDismiss && (
          <button
            onClick={onDismiss}
            className={`flex-shrink-0 p-1 rounded hover:bg-black/5 ${iconColors[variant]}`}
            aria-label="Dismiss"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
