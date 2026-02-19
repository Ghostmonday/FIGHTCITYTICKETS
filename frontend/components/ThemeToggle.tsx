"use client";

import { useTheme } from "@/app/lib/theme-context";

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="relative w-14 h-8 rounded-full transition-all duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-[var(--accent)]"
      style={{
        backgroundColor: theme === "dark" ? "#262626" : "#E5E5E5",
      }}
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
    >
      {/* Track */}
      <span
        className="absolute inset-1 rounded-full transition-colors duration-300"
        style={{
          backgroundColor: theme === "dark" ? "#1F1F1F" : "#FFFFFF",
        }}
      />
      
      {/* Thumb */}
      <span
        className="absolute top-1 w-6 h-6 rounded-full transition-all duration-300 shadow-md"
        style={{
          backgroundColor: theme === "dark" ? "#FF5722" : "#0891B2",
          left: theme === "dark" ? "28px" : "4px",
        }}
      />
      
      {/* Icons */}
      <span className="absolute inset-0 flex items-center justify-between px-1.5">
        {/* Sun icon (for dark mode - shows when switching to light) */}
        <svg
          className={`w-3.5 h-3.5 transition-all duration-300 ${
            theme === "dark" ? "opacity-30" : "opacity-100"
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          style={{ color: theme === "dark" ? "#A3A3A3" : "#171717" }}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
          />
        </svg>
        
        {/* Moon icon (for light mode - shows when switching to dark) */}
        <svg
          className={`w-3.5 h-3.5 transition-all duration-300 ${
            theme === "dark" ? "opacity-100" : "opacity-30"
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          style={{ color: theme === "dark" ? "#FF5722" : "#171717" }}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
          />
        </svg>
      </span>
    </button>
  );
}
