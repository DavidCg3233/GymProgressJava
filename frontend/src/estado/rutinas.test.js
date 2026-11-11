// Editar rutinas y catálogo (T-002-14 a 16 · RNF-002-01).
// Estas acciones requieren conexión: sin ella se avisa y no se cambia nada.

import { IDBFactory } from 'fake-indexeddb'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const servidor = { conectado: true, recibidas: [] }

vi.mock('../datos/api.js', async (original) => {
  const real = await original()
  return {
    ...real,
    pedir: vi.fn(async (metodo, url, cuerpo) => {
      if (!servidor.conectado) throw new real.ErrorDeApi(0, 'Sin conexión.')
      servidor.recibidas.push({ metodo, url, cuerpo })
      if (url === '/api/arranque/') {
        return { sesion_en_curso: null, ultima_vez: {}, catalogo: { grupos: [], ejercicios: [] }, rutinas: [] }
      }
      const id = url.split('/').at(-2)
      if (url.endsWith('/duplicar/')) {
        return { rutina: { id: cuerpo.id_copia, nombre: 'Pecho (copia)', dias: [], ejercicios: [] } }
      }
      if (url.startsWith('/api/rutinas/') && metodo === 'PUT') return { rutina: { id, ...cuerpo, ejercicios: [] } }
      if (url.startsWith('/api/catalogo/ejercicios/') && metodo === 'PUT') return { ejercicio: { id, ...cuerpo } }
      if (url.startsWith('/api/catalogo/ejercicios/') && metodo === 'DELETE') {
        return { rutinas_eliminadas: [{ id: 'r-solo', nombre: 'Solo' }] }
      }
      if (url.startsWith('/api/catalogo/grupos/') && metodo === 'PUT') return { grupo: { id, ...cuerpo } }
      return null
    }),
  }
})

async function abrirApp() {
  vi.resetModules()
  const sesion = await import('./sesion.js')
  await sesion.cargarArranque()
  const rutinas = await import('./rutinas.js')
  return { estado: sesion.estado, ...rutinas }
}

beforeEach(() => {
  globalThis.indexedDB = new IDBFactory()
  servidor.conectado = true
  servidor.recibidas = []
})

describe('rutinas', () => {
  it('guardar una rutina la envía y la deja en el celular', async () => {
    const app = await abrirApp()

    await app.guardarRutina({ id: 'r-1', nombre: 'Pecho', dias: [1], ejercicios: [] })

    expect(servidor.recibidas.at(-1)).toMatchObject({ metodo: 'PUT', url: '/api/rutinas/r-1/' })
    expect(app.estado.rutinas.map((r) => r.nombre)).toEqual(['Pecho'])
  })

  it('volver a guardarla la reemplaza en vez de duplicarla, y la lista queda por nombre', async () => {
    const app = await abrirApp()
    await app.guardarRutina({ id: 'r-2', nombre: 'Pierna', dias: [], ejercicios: [] })
    await app.guardarRutina({ id: 'r-1', nombre: 'Pecho', dias: [], ejercicios: [] })

    await app.guardarRutina({ id: 'r-1', nombre: 'Brazo', dias: [], ejercicios: [] })

    expect(app.estado.rutinas.map((r) => r.nombre)).toEqual(['Brazo', 'Pierna'])
  })

  it('RNF-002-01: sin conexión no se guarda nada y se avisa', async () => {
    const app = await abrirApp()
    servidor.conectado = false

    await expect(app.guardarRutina({ id: 'r-1', nombre: 'Pecho', dias: [], ejercicios: [] })).rejects.toMatchObject({
      sinConexion: true,
    })
    expect(app.estado.rutinas).toEqual([])
  })

  it('eliminar la quita del celular', async () => {
    const app = await abrirApp()
    await app.guardarRutina({ id: 'r-1', nombre: 'Pecho', dias: [], ejercicios: [] })

    await app.eliminarRutina('r-1')

    expect(app.estado.rutinas).toEqual([])
  })

  it('duplicar agrega la copia', async () => {
    const app = await abrirApp()
    await app.guardarRutina({ id: 'r-1', nombre: 'Pecho', dias: [], ejercicios: [] })

    await app.duplicarRutina('r-1')

    expect(app.estado.rutinas.map((r) => r.nombre)).toEqual(['Pecho', 'Pecho (copia)'])
  })

  it('lo guardado sigue ahí al volver a abrir la app sin señal', async () => {
    const antes = await abrirApp()
    await antes.guardarRutina({ id: 'r-1', nombre: 'Pecho', dias: [], ejercicios: [] })

    servidor.conectado = false
    const despues = await abrirApp()

    expect(despues.estado.rutinas.map((r) => r.nombre)).toEqual(['Pecho'])
  })
})

describe('catálogo', () => {
  it('crear un ejercicio lo agrega al catálogo del celular', async () => {
    const app = await abrirApp()

    const ejercicio = await app.guardarEjercicio({ nombre: 'Burpees', grupo: 'g-cardio' })

    expect(app.estado.catalogo.ejercicios).toEqual([ejercicio])
    expect(ejercicio.nombre).toBe('Burpees')
  })

  it('crear un grupo lo agrega al catálogo del celular', async () => {
    const app = await abrirApp()

    await app.guardarGrupo({ nombre: 'Cardio' })

    expect(app.estado.catalogo.grupos.map((g) => g.nombre)).toEqual(['Cardio'])
  })

  it('RF-002-18: eliminar un ejercicio también quita del celular las rutinas que quedaron vacías', async () => {
    const app = await abrirApp()
    await app.guardarRutina({ id: 'r-solo', nombre: 'Solo', dias: [], ejercicios: [] })
    await app.guardarRutina({ id: 'r-otra', nombre: 'Otra', dias: [], ejercicios: [] })
    const ejercicio = await app.guardarEjercicio({ nombre: 'Fondos', grupo: 'g-pecho' })

    await app.eliminarEjercicio(ejercicio.id)

    expect(app.estado.catalogo.ejercicios).toEqual([])
    expect(app.estado.rutinas.map((r) => r.id)).toEqual(['r-otra'])
  })
})
