import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    // Optimize for faster startup
    hmr: {
      overlay: false // Disable error overlay for faster startup
    }
  },
  // Optimize build and dev performance
  optimizeDeps: {
    // Pre-bundle these dependencies for faster startup
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'socket.io-client'
    ],
    // Exclude heavy dependencies from pre-bundling
    exclude: [
      'express' // Server-side only
    ]
  },
  // Reduce processing during dev
  esbuild: {
    // Skip type checking during dev for faster startup
    logOverride: { 'this-is-undefined-in-esm': 'silent' }
  },
  // Disable source maps in dev for faster startup
  build: {
    sourcemap: false
  }
})
