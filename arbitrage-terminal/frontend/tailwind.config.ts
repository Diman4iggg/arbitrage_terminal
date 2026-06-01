import type { Config } from "tailwindcss"

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        terminal: {
          950: "#09090b",
          900: "#101114",
          800: "#191b20",
          700: "#272a31",
        },
      },
    },
  },
  plugins: [],
} satisfies Config

