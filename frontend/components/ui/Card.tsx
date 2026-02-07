"use client";

import { HTMLAttributes, forwardRef } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "elevated" | "outlined";
  padding?: "none" | "sm" | "md" | "lg";
  hover?: boolean;
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      variant = "default",
      padding = "md",
      hover = false,
      children,
      className = "",
      ...props
    },
    ref
  ) => {
    const variantStyles = {
      default: "bg-bg-surface border border-border",
      elevated: "bg-bg-surface shadow-elevation",
      outlined: "bg-bg-surface border-2 border-border",
    };

    const paddingStyles = {
      none: "",
      sm: "p-4",
      md: "p-6",
      lg: "p-8",
    };

    return (
      <div
        ref={ref}
        className={`
          rounded-card
          ${variantStyles[variant]}
          ${paddingStyles[padding]}
          ${hover ? "hover:shadow-elevation hover:border-border-subtle transition-all duration-200 cursor-pointer" : ""}
          ${className}
        `}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = "Card";
