import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        base: "#12161B",
        panel: "#181D24",
        border: "#262D36",
        ink: "#E7E5E0",
        muted: "#8B94A0",
        accent: "#E8A33D",
        "accent-dim": "#7A5B26",
      },
      fontFamily: {
        display: ["var(--font-display)"],
        body: ["var(--font-body)"],
        mono: ["var(--font-mono)"],
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        blink: {
          "0%, 80%, 100%": { opacity: "0.25" },
          "40%": { opacity: "1" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.25s ease-out",
        blink: "blink 1.4s infinite",
      },
    },
  },
  plugins: [],
};

export default config;
