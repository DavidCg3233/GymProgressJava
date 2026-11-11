// Pruebas de flujo completo (T-006-34 · plan 006, sección 2).
//
// Corren contra la app de producción ya construida (Django sirviendo la pantalla
// y su service worker), con el motor WebKit, el mismo de Safari en el iPhone.
// En las revisiones automáticas la URL y la cuenta las pone el trabajo
// "Imagen de producción"; en tu equipo, ver las notas técnicas de la 006.

import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  // `.e2e.js` y no `.test.js`, para que Vitest no las tome como suyas.
  testMatch: '**/*.e2e.js',
  timeout: 90_000,
  expect: { timeout: 15_000 },
  retries: 0,
  // En GitHub, los errores salen como anotaciones: se ven sin iniciar sesión.
  reporter: process.env.CI ? [['github'], ['list']] : [['list']],
  use: {
    baseURL: process.env.E2E_URL ?? 'http://localhost:8000',
    trace: 'retain-on-failure',
    // Que use el service worker de la app, como el iPhone.
    serviceWorkers: 'allow',
  },
  projects: [{ name: 'iphone', use: { ...devices['iPhone 13'] } }],
})
