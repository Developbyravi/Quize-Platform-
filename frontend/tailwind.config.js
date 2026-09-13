/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#090d16",
        foreground: "#f3f4f6",
        card: "#111827",
        "card-foreground": "#f9fafb",
        primary: {
          DEFAULT: "#3b82f6",
          hover: "#2563eb",
          foreground: "#ffffff"
        },
        secondary: {
          DEFAULT: "#1f2937",
          foreground: "#9ca3af"
        },
        accent: {
          DEFAULT: "#8b5cf6",
          foreground: "#ffffff"
        },
        success: "#10b981",
        warning: "#f59e0b",
        danger: "#ef4444",
      },
    },
  },
  plugins: [],
};
