import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ivory: {
          50: "#fdfcf8",
          100: "#faf8f0",
          200: "#f5f0e4",
          300: "#ede5d0",
        },
        stone: {
          850: "#2a2522",
        },
        amber: {
          muted: "#b8860b",
        },
      },
      fontFamily: {
        serif: ["Newsreader", "Georgia", "serif"],
        sans: ["Manrope", "system-ui", "sans-serif"],
      },
      typography: {
        DEFAULT: {
          css: {
            fontFamily: "Manrope, system-ui, sans-serif",
          },
        },
      },
    },
  },
  plugins: [],
};

export default config;
