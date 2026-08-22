import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/empresas': 'http://localhost:8000',
      '/espacios': 'http://localhost:8000',
      '/insumos': 'http://localhost:8000',
      '/servicios': 'http://localhost:8000',
    },
  },
})
