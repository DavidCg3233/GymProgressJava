import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// En desarrollo, la pantalla (puerto 5173) le pasa al servidor de Django (puerto 8000)
// todo lo que no es suyo. Así ambos se ven como un solo sitio, igual que en producción,
// y la cookie de acceso y la protección CSRF funcionan sin configuración especial.
const SERVIDOR_LOCAL = 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [vue()],
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
