/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",             // tu archivo raíz de Vite
    "./src/**/*.{js,ts,jsx,tsx}" // todos tus componentes React
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          light: '#3ABEF9',
          DEFAULT: '#0EA5E9',
          dark: '#0369A1'
        }
      }
    },
  },
  plugins: [],
}
