import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

/**
 * Vite configuration for the ReqEngine frontend.
 * Enables React plugin and sets the dev server port to 5173 on all interfaces.
 * usePolling ensures reliable HMR when running inside Docker with bind-mounted volumes.
 */
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    watch: { usePolling: true },
  },
})
