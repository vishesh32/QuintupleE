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
        "background": "#E8E4E6",
        "primary": "#004643",
        "secondary": "#ffffff",
      },
      boxShadow: {
        "info-box": "0px 8px 54.7px 0px rgba(0, 0, 0, 0.38)",
      }
    },
  },
  plugins: [],
};
export default config;
