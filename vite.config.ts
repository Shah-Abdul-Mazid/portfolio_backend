import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'Portfolio Admin',
        short_name: 'Admin',
        description: 'Manage your professional portfolio with ease.',
        theme_color: '#0b1120',
        background_color: '#030712',
        display: 'standalone',
        start_url: '/login/admin',
        scope: '/',
        icons: [
          {
            src: '/admin-pwa-192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/admin-pwa-512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ]
      }
    })
  ],
  server: {
    host: true,
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true
      }
    }
  }
})
