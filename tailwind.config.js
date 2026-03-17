/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        igss: {
          primary: '#003876',
          secondary: '#005DA8',
          accent: '#0078D4',
          light: '#E8F1FA',
          dark: '#002347',
          green: '#2E7D32',
          gold: '#C5960C',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
