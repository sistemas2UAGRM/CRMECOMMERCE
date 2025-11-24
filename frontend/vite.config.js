import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  darkMode: 'class',
  theme: {
    extend: {},
  },
  plugins: [react(),
    tailwindcss()
  ],
  host: true,
    port: 4000,
    allowedHosts: true, // Permite entrar desde nip.io
    hmr: {
        host: 'localhost', // <--- ESTO SE CAMBIA AL DESPLEGAR
        clientPort: 4000,
    },
})
