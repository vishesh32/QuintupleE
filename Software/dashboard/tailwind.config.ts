import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "background": "#141414",
        "big-card": "#242629",
        "small-card": "#16161A",
        "primary": "#2CB67D",
        "secondary": "#FFFFFF",
      },
      boxShadow: {
        "card": "0px 4px 12px 0px rgba(0, 0, 0, 0.25);",
      },
      keyframes: {
        ttb: {
          "from": {
            transfrom: 'translateY(-100%)',
            opacity: "0"
          },
          "to": {
            transfrom: 'translateY(0)',
            opacity: "1"
          },
        },
      },
      animation: {
        "ttb": "ttb 0.7s ease-in-out",
        "ttb-fast": "ttb 0.25s ease-in-out"
      },
    },
  },
  plugins: [],
};
export default config;
