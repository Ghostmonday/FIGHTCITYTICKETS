/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary colors
        primary: {
          DEFAULT: "#DC2626", // red-600 - Primary CTA, key accents
          hover: "#B91C1C", // red-700 - Hover state
          focus: "#FCA5A5", // red-300 - Focus ring
          muted: "#FEE2E2", // red-100 - Muted backgrounds
        },
        // Text colors
        text: {
          primary: "#111827", // gray-900 - Headings, primary text
          secondary: "#6B7280", // gray-500 - Secondary text
          muted: "#9CA3AF", // gray-400 - Muted text
        },
        // Background colors
        bg: {
          page: "#F9FAFB", // gray-50 - Page background
          surface: "#FFFFFF", // white - Card/input backgrounds
          subtle: "#F3F4F6", // gray-100 - Subtle backgrounds
        },
        // State colors
        success: {
          DEFAULT: "#10B981", // emerald-500 - Success states
          bg: "#ECFDF5", // emerald-50 - Success background
          border: "#A7F3D0", // emerald-200 - Success border
        },
        warning: {
          DEFAULT: "#F59E0B", // amber-500 - Warning states
          bg: "#FFFBEB", // amber-50 - Warning background
          border: "#FDE68A", // amber-200 - Warning border
        },
        error: {
          DEFAULT: "#DC2626", // red-600 - Error states
          bg: "#FEF2F2", // red-50 - Error background
          border: "#FECACA", // red-200 - Error border
        },
        // Border color
        border: {
          DEFAULT: "#E5E7EB", // gray-200 - Default borders
          subtle: "#F3F4F6", // gray-100 - Subtle borders
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      fontSize: {
        "heading-xl": ["2.25rem", { lineHeight: "1.1", fontWeight: "600" }],
        "heading-lg": ["1.875rem", { lineHeight: "1.2", fontWeight: "600" }],
        "heading-md": ["1.5rem", { lineHeight: "1.25", fontWeight: "600" }],
        "heading-sm": ["1.25rem", { lineHeight: "1.4", fontWeight: "500" }],
        "body-lg": ["1.125rem", { lineHeight: "1.6" }],
        body: ["1rem", { lineHeight: "1.6" }],
        "body-sm": ["0.875rem", { lineHeight: "1.5" }],
        caption: ["0.8125rem", { lineHeight: "1.5" }],
        tiny: ["0.75rem", { lineHeight: "1.5" }],
      },
      spacing: {
        touch: "2.75rem", // 44px - Minimum touch target
        "touch-sm": "2.5rem", // 40px - Small touch target
      },
      borderRadius: {
        card: "12px",
        input: "8px",
        button: "8px",
      },
      boxShadow: {
        soft: "0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03)",
        subtle: "0 1px 2px rgba(0, 0, 0, 0.04)",
        elevation:
          "0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)",
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.4s ease-out",
        "slide-down": "slideDown 0.3s ease-out",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideDown: {
          "0%": { opacity: "0", transform: "translateY(-10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
