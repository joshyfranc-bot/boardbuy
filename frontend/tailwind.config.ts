import type { Config } from "tailwindcss";

export default {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: { DEFAULT: "#4f7cff", gold: "#d4a017" },
        surface: { DEFAULT: "#171a21", 2: "#1e2230" },
      },
    },
  },
  plugins: [],
} satisfies Config;
