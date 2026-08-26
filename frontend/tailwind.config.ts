import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Stitch "Corporate Modern" palette — anchored on professional blue
        primary: {
          DEFAULT: "#0284C7", // primary action / active nav / key data
          hover: "#0369A1", // secondary — hovered states / emphasized stats
          50: "#F0F9FF",
          100: "#E0F2FE",
          200: "#BAE6FD",
          300: "#7DD3FC",
          400: "#38BDF8",
          500: "#0EA5E9",
          600: "#0284C7",
          700: "#0369A1",
          800: "#075985",
          900: "#0C4A6E",
        },
        surface: {
          DEFAULT: "#F8FAFC", // canvas — reduce eye strain (Slate-50)
          card: "#FFFFFF", // Level 1 cards/containers
        },
        ink: {
          DEFAULT: "#0F172A", // Slate-900 high-contrast typography
          soft: "#475569", // Slate-600
          muted: "#64748B", // Slate-500 — section headers / labels
          faint: "#94A3B8", // Slate-400 — sidebar nav text
          ondark: "#E2E8F0", // Slate-200 — text on sidebar
        },
        line: {
          DEFAULT: "#E2E8F0", // Slate-200 structural division
          strong: "#CBD5E1", // Slate-300 hover border
        },
        sidebar: {
          bg: "#0F172A", // Slate-900 dark theme sidebar
          text: "#94A3B8", // Slate-400
          active: "#0284C7", // primary active bar
          hover: "#1E293B", // Slate-800
        },
        semantic: {
          success: "#10B981", // Emerald — positive YoY
          warning: "#F59E0B", // Amber
          danger: "#F43F5E", // Rose — negative YoY
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains)", "JetBrains Mono", "monospace"],
      },
      fontSize: {
        // Stitch typography scale
        "display-lg": ["36px", { lineHeight: "44px", letterSpacing: "-0.02em", fontWeight: "700" }],
        "headline-md": ["24px", { lineHeight: "32px", letterSpacing: "-0.01em", fontWeight: "600" }],
        "headline-sm": ["18px", { lineHeight: "28px", fontWeight: "600" }],
        "body-lg": ["16px", { lineHeight: "24px", fontWeight: "400" }],
        "body-md": ["14px", { lineHeight: "20px", fontWeight: "400" }],
        "body-sm": ["12px", { lineHeight: "18px", fontWeight: "400" }],
        "data-tabular": ["13px", { lineHeight: "16px" }],
        "label-caps": ["11px", { lineHeight: "16px", letterSpacing: "0.05em", fontWeight: "700" }],
      },
      borderRadius: {
        sm: "0.125rem", // 2px
        DEFAULT: "0.25rem", // 4px — buttons, inputs, checkboxes
        md: "0.375rem", // 6px
        lg: "0.5rem", // 8px — cards, modals, dropdowns
        xl: "0.75rem", // 12px
        full: "9999px",
      },
      boxShadow: {
        // Single subtle shadow definition for card lift
        card: "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)",
      },
      spacing: {
        "sidebar-width": "260px",
        gutter: "1.5rem",
        "section-gap": "2rem",
        "component-sm": "0.75rem",
        "component-md": "1.25rem",
      },
      maxWidth: {
        container: "1440px",
      },
    },
  },
  plugins: [],
};

export default config;