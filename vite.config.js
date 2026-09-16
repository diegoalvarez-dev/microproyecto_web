import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Config de Vite. El proxy de /api solo se usa si corres el frontend
// con `npm run dev` Y la API Flask por separado con `python api/index.py`.
// Si usas `vercel dev`, no necesitas el proxy (Vercel ya rutea /api).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:5000',
    },
  },
})
