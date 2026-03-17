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
          primary: '#1B5E20',     // Verde oscuro (hojas del árbol, vestido)
          secondary: '#2E7D32',   // Verde medio
          accent: '#388E3C',      // Verde claro para hover/focus
          light: '#E8F5E9',       // Verde muy claro (fondos)
          dark: '#0D3B0F',        // Verde muy oscuro
          red: '#C62828',         // Rojo IGSS (texto del logo)
          gold: '#B8960C',        // Dorado (banner del logo)
          golddark: '#8B6F00',    // Dorado oscuro
          brown: '#5D4037',       // Café (tronco del árbol)
          green: '#2E7D32',       // Verde éxito
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
