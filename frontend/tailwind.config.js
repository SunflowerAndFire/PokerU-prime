/** @type {import('tailwindcss').Config} */
module.exports = {
  // NOTE: Update this to include the paths to all files that contain Nativewind classes.
  content: ["./app/index.tsx", "./components/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        primary: "#ffffff",
        secondary: "#151312",
        accent: "#a503c1",
        light: {
          100: "#d6c6ff",
          200: "#a8b5db",
          300: "#9ca4ab",
        },
        dark: {
          100: "#221f3d",
          200: "#0f0d23",
        },
      }
    },
  },
  plugins: [],
}