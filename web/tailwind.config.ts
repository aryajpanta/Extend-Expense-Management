import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1B2330",
        fog: "#F4F6F8",
        pine: "#1C6E5B",
        rust: "#B55D2C",
        sand: "#E9DDC7",
        slate: "#607284"
      },
      boxShadow: {
        card: "0 18px 40px rgba(17, 24, 39, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;

