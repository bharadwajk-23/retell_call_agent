import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

// Standalone SPA: built independently of the backend and served by its own
// static server (see frontend/serve.py, run via uvicorn). No coupling to
// the backend FastAPI app's paths.
export default defineConfig({
  plugins: [react()],
  // Read env vars (VITE_*) from the single project-root .env instead of a
  // frontend-local one — see ../.env / ../.env.example.
  envDir: fileURLToPath(new URL('..', import.meta.url)),
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
  server: {
    port: 8005,
  },
  preview: {
    port: 8005,
  },
})
