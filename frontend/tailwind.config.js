/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Dark Mode ("Fight") - Deep charcoal, neon orange accent
        dark: {
          bg: {
            page: "#0A0A0A",      // Absolute black
            surface: "#141414",   // Elevated surface
            subtle: "#1F1F1F",     // Subtle backgrounds
          },
          text: {
            primary: "#FFFFFF",   // Crisp white
            secondary: "#A3A3A3", // Muted white
            muted: "#525252",     // Very muted
          },
          accent: {
            DEFAULT: "#FF5722",   // Neon orange (parking ticket)
            hover: "#FF7043",     // Lighter orange
            glow: "#FF572240",    // Orange glow (40% opacity)
          },
          border: {
            DEFAULT: "#262626",   // Subtle border
            subtle: "#1F1F1F",    // Very subtle
          },
        },
        // Light Mode ("Paper White") - Clean white, cyan accent
        light: {
          bg: {
            page: "#FAFAFA",      // Paper white
            surface: "#FFFFFF",  // Pure white
            subtle: "#F5F5F5",    // Slightly off-white
          },
          text: {
            primary: "#171717",   // Nearly black
            secondary: "#525252", // Dark grey
            muted: "#A3A3A3",     // Muted grey
          },
          accent: {
            DEFAULT: "#0891B2",   // Cyan blue (professional)
            hover: "#06B6D4",     // Brighter cyan
            glow: "#0891B240",    // Cyan glow (40% opacity)
          },
          border: {
            DEFAULT: "#E5E5E5",   // Light grey
            subtle: "#F5F5F5",    // Very subtle
          },
        },
        // Legacy colors (for backwards compatibility during transition)
        primary: {
          DEFAULT: "#FF5722",
          hover: "#FF7043",
          focus: "#FFAB91",
          muted: "#FBE9E7",
        },
        text: {
          primary: "#171717",
          secondary: "#525252",
          muted: "#A3A3A3",
        },
        bg: {
          page: "#FAFAFA",
          surface: "#FFFFFF",
          subtle: "#F5F5F5",
        },
        success: {
          DEFAULT: "#10B981",
          bg: "#ECFDF5",
          border: "#A7F3D0",
        },
        warning: {
          DEFAULT: "#F59E0B",
          bg: "#FFFBEB",
          border: "#FDE68A",
        },
        error: {
          DEFAULT: "#DC2626",
          bg: "#FEF2F2",
          border: "#FECACA",
        },
        border: {
          DEFAULT: "#E5E5E5",
          subtle: "#F5F5F5",
        },
      },
      fontFamily: {
        sans: ["Inter", "SF Pro Display", "system-ui", "sans-serif"],
      },
      fontSize: {
        "display": ["4rem", { lineHeight: "1.05", fontWeight: "700", letterSpacing: "-0.02em" }],
        "heading-xl": ["2.5rem", { lineHeight: "1.1", fontWeight: "600" }],
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
        touch: "2.75rem",
        "touch-sm": "2.5rem",
        "step": "20rem", // For one-step UI vertical rhythm
      },
      borderRadius: {
        card: "16px",
        input: "12px",
        button: "12px",
      },
      boxShadow: {
        soft: "0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03)",
        subtle: "0 1px 2px rgba(0, 0, 0, 0.04)",
        elevation: "0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)",
        "glow-orange": "0 0 40px -10px #FF572240",
        "glow-cyan": "0 0 40px -10px #0891B240",
        "card-dark": "0 8px 32px rgba(0, 0, 0, 0.4)",
        "card-light": "0 8px 32px rgba(0, 0, 0, 0.08)",
      },
      animation: {
        "fade-in": "fadeIn 0.4s ease-out",
        "slide-up": "slideUp 0.5s ease-out",
        "slide-down": "slideDown 0.4s ease-out",
        "pulse-glow": "pulseGlow 2s ease-in-out infinite",
        "progress": "progress 1s ease-out forwards",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideDown: {
          "0%": { opacity: "0", transform: "translateY(-20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulseGlow: {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" },
        },
        progress: {
          "0%": { width: "0%" },
          "100%": { width: "var(--progress-width, 100%)" },
        },
      },
    },
  },
  plugins: [],
};
