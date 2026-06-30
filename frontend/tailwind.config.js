/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        school: {
          navy: '#1e3a8a',
          gold: '#b45309',
          slate: '#334155',
        }
      }
    },
  },
  plugins: [],
}