/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx}",
    "./components/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: "#f6f3ef",
        ink: "#171717",
        slate: "#5d6671",
        mist: "#e6e1db",
        steel: "#d1d9de",
        accent: "#27556f",
        accentSoft: "#d7e8ef",
        copper: "#9b5e2f",
      },
      fontFamily: {
        heading: ["var(--font-plus-jakarta-sans)"],
        body: ["var(--font-inter)"],
      },
      boxShadow: {
        editorial: "0 24px 60px rgba(23, 23, 23, 0.08)",
      },
      letterSpacing: {
        tightest: "-0.06em",
      },
    },
  },
  plugins: [],
};
