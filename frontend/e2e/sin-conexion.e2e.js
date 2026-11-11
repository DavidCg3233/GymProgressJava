// Flujo completo sin conexión, en WebKit (T-006-34).
// Spec 006 · CA-006-16a (nada se pierde y llega en orden) · CA-006-17a (abre y registra sin señal).
//
// Usa la cuenta del dueño recién creada, con su contraseña temporal: la prueba
// la cambia (RNF-ACC-09) y sigue. Por eso solo se puede correr una vez por base.

import { execSync } from 'node:child_process'

import { expect, test } from '@playwright/test'

const USUARIO = process.env.E2E_USUARIO ?? 'dueno'
const TEMPORAL = process.env.E2E_CONTRASENA_TEMPORAL
const NUEVA = 'Nueva-de-la-prueba-e2e-9'

/**
 * "Modo avión": el servidor deja de existir para el celular.
 *
 * Se apaga el servidor de verdad (E2E_APAGAR) en lugar de simularlo desde
 * Playwright: en WebKit, tanto `setOffline` como `route` cortan la navegación
 * antes de que el service worker pueda responder, y justo eso es lo que se
 * quiere probar. Al volver (E2E_ENCENDER) se espera a que responda /salud/.
 */
async function modoAvion(request, activo) {
  execSync(activo ? process.env.E2E_APAGAR : process.env.E2E_ENCENDER, { stdio: 'inherit' })
  if (!activo) {
    await expect
      .poll(async () => (await request.get('/salud/').catch(() => null))?.ok() ?? false, { timeout: 60_000 })
      .toBe(true)
  }
}

/** Escribe peso y reps en la fila `numero` (desde 1) y la confirma. */
async function confirmarSerie(pagina, numero, peso, reps) {
  await pagina.getByRole('textbox', { name: 'kg' }).nth(numero - 1).fill(String(peso))
  await pagina.getByRole('textbox', { name: 'reps' }).nth(numero - 1).fill(String(reps))
  await pagina.getByRole('button', { name: `Confirmar serie ${numero}` }).click()
  await expect(pagina.getByRole('button', { name: `Serie ${numero} confirmada` })).toBeVisible()
}

/**
 * RNF-007-02 (T-007-09): todo lo que se toca mide al menos 44 × 44, y dos
 * objetivos vecinos en la misma fila quedan a 8 px o más.
 * Devuelve la lista de problemas: vacía si todo cumple.
 */
async function objetivosPequenos(pagina) {
  return pagina.evaluate(() => {
    const visibles = [...document.querySelectorAll('button, a[href], input, select, textarea, [role="button"]')].filter(
      (el) => el.offsetParent !== null || getComputedStyle(el).position === 'fixed',
    )
    const cajas = visibles.map((el) => ({
      nombre: (el.getAttribute('aria-label') || el.textContent || el.tagName).trim().slice(0, 40),
      caja: el.getBoundingClientRect(),
    }))
    const problemas = []
    for (const { nombre, caja } of cajas) {
      if (caja.width < 44 - 0.5 || caja.height < 44 - 0.5) {
        problemas.push(`"${nombre}" mide ${Math.round(caja.width)} × ${Math.round(caja.height)}`)
      }
    }
    for (const [i, a] of cajas.entries()) {
      for (const b of cajas.slice(i + 1)) {
        const mismaFila = a.caja.top < b.caja.bottom && b.caja.top < a.caja.bottom
        const separacion = Math.max(b.caja.left - a.caja.right, a.caja.left - b.caja.right)
        // La separación cuida a los botones pequeños vecinos (como los +/−). Las áreas
        // grandes contiguas, como las pestañas de la barra (≈ 94 px), no cuentan.
        const pequeno = Math.min(a.caja.width, b.caja.width) < 60
        if (pequeno && mismaFila && separacion >= 0 && separacion < 8 - 0.5) {
          problemas.push(`"${a.nombre}" y "${b.nombre}" quedan a ${separacion.toFixed(1)} px`)
        }
      }
    }
    return problemas
  })
}

const saludo = (pagina) => pagina.getByRole('heading', { name: /^Hola/ })

test('CA-006-16a y 17a: en modo avión se registra, se cierra, se abre y todo llega al volver la señal', async ({
  context,
  page,
  request,
}) => {
  test.skip(
    !TEMPORAL || !process.env.E2E_APAGAR || !process.env.E2E_ENCENDER,
    'Faltan E2E_CONTRASENA_TEMPORAL, E2E_APAGAR o E2E_ENCENDER: ver las notas técnicas de la spec 006.',
  )

  // --- Con señal: entrar y cambiar la contraseña temporal ---------------------
  await page.goto('/')
  await page.getByLabel('Usuario o correo').fill(USUARIO)
  await page.getByLabel('Contraseña', { exact: true }).fill(TEMPORAL)
  await page.getByRole('button', { name: 'Entrar' }).click()

  await page.getByLabel('Contraseña temporal').fill(TEMPORAL)
  await page.getByLabel('Contraseña nueva (mínimo 10 caracteres)').fill(NUEVA)
  await page.getByLabel('Repite la contraseña nueva').fill(NUEVA)
  await page.locator('form button[type="submit"]').click()
  await expect(saludo(page)).toBeVisible()

  // RNF-007-02 en el Inicio, con la barra inferior (T-007-09).
  expect(await objetivosPequenos(page)).toEqual([])

  // El service worker guarda la app; desde la siguiente carga, él la sirve.
  await page.evaluate(() => navigator.serviceWorker.ready)
  await page.reload()
  await expect.poll(() => page.evaluate(() => Boolean(navigator.serviceWorker.controller))).toBe(true)
  await expect(saludo(page)).toBeVisible()

  // --- CA-006-17a: modo avión. La app abre y deja registrar -------------------
  await modoAvion(request, true)
  await page.reload()
  await expect(saludo(page)).toBeVisible()
  await expect(page.getByText('Sin conexión.')).toBeVisible()

  await page.getByRole('button', { name: 'Empezar sesión libre' }).click()
  await page.getByRole('button', { name: '+ Ejercicio' }).click()
  await page.getByLabel('Nombre').fill('Sentadilla')
  await page.getByLabel('Grupo muscular').selectOption('Pierna')
  await page.getByRole('button', { name: 'Agregar', exact: true }).click()

  // Un ejercicio sin "última vez" llega vacío: se escribe peso y reps.
  await confirmarSerie(page, 1, 60, 8)
  await expect(page.getByText(/guardados en el celular/)).toBeVisible()

  // --- CA-006-16a: cerrar la app y volver a abrirla, todavía sin señal --------
  await page.close()
  const despues = await context.newPage()
  await despues.goto('/')
  // La app puede volver directo a la sesión o mostrar "Continuar sesión" en el inicio.
  const continuar = despues.getByRole('button', { name: /^Continuar sesión/ })
  await expect(despues.getByRole('heading', { name: 'Sesión en curso' }).or(continuar)).toBeVisible()
  if (await continuar.isVisible()) {
    await continuar.click()
  }
  await expect(despues.getByRole('button', { name: 'Serie 1 confirmada' })).toBeVisible()

  await despues.getByRole('button', { name: '+ Serie' }).click()
  await confirmarSerie(despues, 2, 62.5, 6)

  // --- Vuelve la señal: la cola se envía sola, en orden ----------------------
  await modoAvion(request, false)
  // El iPhone avisa "online" al recuperar señal; aquí se avisa a mano.
  await despues.evaluate(() => window.dispatchEvent(new Event('online')))
  await expect(despues.getByText(/guardados en el celular|Enviando/)).toBeHidden()

  await despues.getByRole('button', { name: 'Terminar sesión' }).click()
  await despues.getByRole('button', { name: 'Terminar', exact: true }).click()
  await expect(saludo(despues)).toBeVisible()

  // El servidor tiene la sesión con sus dos series: nada se perdió.
  await expect
    .poll(async () => {
      const respuesta = await despues.request.get('/api/sesiones/')
      const { sesiones } = await respuesta.json()
      return sesiones.map((sesion) => [sesion.ejercicios, sesion.series])
    })
    .toEqual([[1, 2]])
})
