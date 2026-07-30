import type { Config } from "tailwindcss"
const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: { colors: { acid: "#d4ff4f", violet: "#8b5cf6", bg: "#050507" } } },
  plugins: []
}
export default config
