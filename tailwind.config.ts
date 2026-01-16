import type { Config } from "tailwindcss";
import typography from "@tailwindcss/typography";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        surface: "#0b0f14",
        panel: "#0f1621",
        accent: "#4f46e5"
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(79, 70, 229, 0.35), 0 20px 60px rgba(79, 70, 229, 0.2)"
      }
    }
  },
  plugins: [typography]
};

export default config;
