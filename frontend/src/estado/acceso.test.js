// Acceso sin conexión (RF-006-17, CA-006-17a).
// Abrir la app en el gimnasio sin señal no puede terminar en una pantalla de error.

import { IDBFactory } from 'fake-indexeddb'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const servidor = { conectado: true, cuenta: { usuario: 'davidc', correo: 'd@e.com', nombre: 'David', debe_cambiar_contrasena: false } }

vi.mock('../datos/api.js', async (original) => {
  const real = await original()
  return {
    ...real,
    pedir: vi.fn(async (metodo, url) => {
      if (!servidor.conectado) throw new real.ErrorDeApi(0, 'Sin conexión.')
      if (url === '/api/acceso/') return { autenticado: Boolean(servidor.cuenta), cuenta: servidor.cuenta }
      if (url === '/api/acceso/salir/') return null
      return { cuenta: servidor.cuenta }
    }),
  }
})

async function abrirApp() {
  vi.resetModules()
  const modulo = await import('./acceso.js')
  await modulo.cargarAcceso()
  return modulo
}

beforeEach(() => {
  globalThis.indexedDB = new IDBFactory()
  servidor.conectado = true
  servidor.cuenta = { usuario: 'davidc', correo: 'd@e.com', nombre: 'David', debe_cambiar_contrasena: false }
})

describe('abrir la app sin señal', () => {
  it('si ya había entrado en este celular, sigue dentro con la cuenta que conocía', async () => {
    await abrirApp() // ayer, con señal

    servidor.conectado = false
    const { acceso } = await abrirApp() // hoy, en el gimnasio

    expect(acceso.cuenta?.nombre).toBe('David')
    expect(acceso.cargando).toBe(false)
  })

  it('si nunca había entrado en este celular, pide entrar (no hay nada que mostrar)', async () => {
    servidor.conectado = false

    const { acceso } = await abrirApp()

    expect(acceso.cuenta).toBeNull()
    expect(acceso.cargando).toBe(false)
  })

  it('con señal, el servidor manda: si el acceso venció, hay que volver a entrar', async () => {
    await abrirApp()

    servidor.cuenta = null // el acceso venció en el servidor
    const { acceso } = await abrirApp()

    expect(acceso.cuenta).toBeNull()
  })

  it('al salir, el celular olvida la cuenta: sin señal ya no se puede entrar', async () => {
    const app = await abrirApp()
    await app.salir()

    servidor.conectado = false
    const { acceso } = await abrirApp()

    expect(acceso.cuenta).toBeNull()
  })
})
