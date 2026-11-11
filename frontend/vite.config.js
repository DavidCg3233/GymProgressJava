import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

// En desarrollo, la pantalla (puerto 5173) le pasa al servidor de Django (puerto 8000)
// todo lo que no es suyo. Así ambos se ven como un solo sitio, igual que en producción,
// y la cookie de acceso y la protección CSRF funcionan sin configuración especial.
const SERVIDOR_LOCAL = 'http://127.0.0.1:8000'

// Rutas que son del servidor: el service worker nunca las responde desde su copia.
const RUTAS_DEL_SERVIDOR = [/^\/api\//, /^\/panel\//, /^\/static\//, /^\/salud\//]

export default defineConfig({
  plugins: [
    vue(),
    // RNF-PLA-03 y RNF-006-05: app instalable en la pantalla de inicio que abre sin señal.
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['apple-touch-icon.png'],
      manifest: {
        name: 'GymProgress',
        short_name: 'GymProgress',
        description: 'Registro de sesiones de gimnasio, serie por serie.',
        lang: 'es',
        start_url: '/',
        scope: '/',
        display: 'standalone',
        orientation: 'portrait',
        // Fondo de la pantalla de carga al abrir la app instalada (fichas.css, tema claro).
        background_color: '#F6F6F3',
        theme_color: '#F6F6F3',
        icons: [
          { src: 'icono-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icono-512.png', sizes: '512x512', type: 'image/png' },
          { src: 'icono-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        // Se guarda la app completa (pantallas, estilos, íconos), nunca los datos:
        // los datos viven en IndexedDB y en el servidor.
        globPatterns: ['**/*.{js,css,html,png,svg,webmanifest}'],
        navigateFallback: '/index.html',
        navigateFallbackDenylist: RUTAS_DEL_SERVIDOR,
        cleanupOutdatedCaches: true,
      },
    }),
  ],
  server: {
    proxy: {
      '/api': SERVIDOR_LOCAL,
      '/panel': SERVIDOR_LOCAL,
      '/static': SERVIDOR_LOCAL,
    },
  },
  test: {
    include: ['src/**/*.test.js'],
  },
})
