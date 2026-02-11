import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      borderRadius: {
        lg: "0.75rem",
        md: "0.5rem",
        sm: "0.375rem"
      },
      colors: {
        background: "#0f1115",
        foreground: "#e5e7eb",
        panel: "#171a21",
        border: "#2a2f3a",
        muted: "#9ca3af",
        accent: "#10a37f"
      }
    }
  },
  plugins: []
};

export default config;
