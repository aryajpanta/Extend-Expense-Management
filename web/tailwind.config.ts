import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "rgb(var(--color-ink) / <alpha-value>)",
        fog: "rgb(var(--color-fog) / <alpha-value>)",
        pine: "rgb(var(--color-pine) / <alpha-value>)",
        rust: "rgb(var(--color-rust) / <alpha-value>)",
        sand: "rgb(var(--color-sand) / <alpha-value>)",
        slate: "rgb(var(--color-slate) / <alpha-value>)",
        card: "rgb(var(--color-card) / <alpha-value>)"
      },
      boxShadow: {
        card: "0 18px 40px rgba(17, 24, 39, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
