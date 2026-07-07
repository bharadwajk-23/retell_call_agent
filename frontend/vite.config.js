import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

// FastAPI mounts StaticFiles at /index and serves straight out of app/,
// so the build must land there with asset URLs prefixed accordingly.
export default defineConfig({
  plugins: [react()],
  base: '/index/',
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  build: {
    outDir: fileURLToPath(new URL('../app', import.meta.url)),
    emptyOutDir: false,
    assetsDir: 'assets',
  },
  server: {
    port: 5173,
  },
})
