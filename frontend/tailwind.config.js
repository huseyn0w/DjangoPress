/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "../templates/**/*.html",
    "../apps/**/templates/**/*.html",
    "./src/**/*.{js,ts}",
  ],
  theme: {
    extend: {
      colors: {
        // Warm editorial palette — restrained and expensive-feeling.
        paper: "#f6f4ef",
        ink: "#1a1a18",
        accent: "#c0492b",
      },
      fontFamily: {
        sans: [
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Inter",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};
