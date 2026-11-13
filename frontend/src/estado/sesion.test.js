// La sesión en curso, con y sin conexión (T-006-30 a T-006-33).
// Spec 006 · RF-006-08, 16, 17, 18 · RNF-006-05, 06 · CA-006-03b, 16a, 17a.
//
// El servidor es falso y controlable: puede estar arriba o "sin señal".
// El almacén del celular es un IndexedDB simulado que persiste entre "aperturas".

import { IDBFactory } from 'fake-indexeddb'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ErrorDeApi } from '../datos/api.js'
import { fechaLocal, rutinasHechasHoy } from '../reglas/progreso.js'

const servidor = {
  conectado: true,
  recibidas: [],
  sesionEnCurso: null,
  ultimaVez: {},
  catalogo: { grupos: [], ejercicios: [] },
  rutinas: [],
  recientes: [],
  hechasHoy: null,
}

vi.mock('../datos/api.js', async (original) => {
  const real = await original()
  return {
    ...real,
    pedir: vi.fn(async (metodo, url, cuerpo) => {
      if (!servidor.conectado) throw new real.ErrorDeApi(0, 'Sin conexión.')
      if (url === '/api/arranque/') {
        return {
          sesion_en_curso: servidor.sesionEnCurso,
          ultima_vez: servidor.ultimaVez,
          catalogo: servidor.catalogo,
          rutinas: servidor.rutinas,
          recientes: servidor.recientes,
          hechas_hoy: servidor.hechasHoy,
        }
      }
      servidor.recibidas.push({ metodo, url, cuerpo })
      return metodo === 'DELETE' ? null : {}
    }),
  }
})

const ULTIMA_VEZ = {
  'press inclinado': {
    nombre: 'Press inclinado',
    grupo: 'Pecho',
    nota: '',
    series: [
      { numero: 1, peso: 30, reps: 10 },
      { numero: 2, peso: 32.5, reps: 8 },
    ],
  },
}

const CATALOGO = {
  grupos: [
    { id: 'g-pecho', nombre: 'Pecho' },
    { id: 'g-pierna', nombre: 'Pierna' },
  ],
  ejercicios: [{ id: 'e-press', nombre: 'Press inclinado', grupo: 'g-pecho' }],
}

const PECHO = {
  id: 'rutina-pecho',
  nombre: 'Pecho',
  dias: [1],
  ejercicios: [
    { ejercicio: 'e-press', nombre: 'Press inclinado', grupo: 'Pecho', series: 2, reps: 10, peso: 30 },
    { ejercicio: 'e-aperturas', nombre: 'Aperturas', grupo: 'Pecho', series: 1, reps: 12, peso: 12 },
  ],
}

/** Simula cerrar y volver a abrir la app: el código se carga de nuevo; el almacén sigue. */
async function abrirApp() {
  vi.resetModules()
  const modulo = await import('./sesion.js')
  await modulo.cargarArranque()
  return modulo
}

beforeEach(() => {
  globalThis.indexedDB = new IDBFactory()
  Object.assign(servidor, {
    conectado: true,
    recibidas: [],
    sesionEnCurso: null,
    ultimaVez: ULTIMA_VEZ,
    catalogo: CATALOGO,
    rutinas: [PECHO],
    recientes: [],
    hechasHoy: null,
  })
})

describe('arrancar', () => {
  it('con conexión trae la última vez del servidor', async () => {
    const { estado } = await abrirApp()

    expect(estado.ultimaVez).toEqual(ULTIMA_VEZ)
    expect(estado.sinConexion).toBe(false)
  })

  it('sin conexión y sin nada guardado, arranca vacía y avisa, sin fallar', async () => {
    servidor.conectado = false

    const { estado } = await abrirApp()

    expect(estado.sesion).toBeNull()
    expect(estado.sinConexion).toBe(true)
    expect(estado.cargando).toBe(false)
  })
})

describe('CA-006-17a: empezar y registrar sin conexión', () => {
  it('con lo que el celular trajo la última vez que tuvo señal, la serie viene precargada', async () => {
    await abrirApp() // ayer, con conexión

    servidor.conectado = false
    const app = await abrirApp() // hoy, en modo avión
    app.empezarSesionLibre()
    await app.agregarEjercicio('Press inclinado', 'Pecho')

    const serie = app.estado.sesion.ejercicios[0].series[0]
    // RF-008-04: el récord (32,5 × 8, sale de la última vez guardada) y la última vez como pista.
    expect(serie).toMatchObject({ peso: 32.5, reps: 8, origen: 'record', pista: { peso: 30, reps: 10 } })
  })
})

describe('CA-006-16a: confirmar sin señal, cerrar, abrir y recuperar la señal', () => {
  it('nada se pierde y todo llega al servidor en orden', async () => {
    servidor.conectado = false
    const antes = await abrirApp()
    await antes.empezarSesionLibre()
    await antes.agregarEjercicio('Press inclinado', 'Pecho')
    const ejercicio = antes.estado.sesion.ejercicios[0]
    await antes.confirmarSerie(ejercicio, ejercicio.series[0], { peso: 30, reps: 10 })
    antes.agregarSerie(ejercicio)
    await antes.confirmarSerie(ejercicio, ejercicio.series[1], { peso: 32.5, reps: 8 })

    // RF-006-18: sin señal se ve cuántos cambios faltan por enviar.
    expect(antes.estado.pendientes).toBe(4)
    expect(servidor.recibidas).toHaveLength(0)

    // Cierro la app y la abro, todavía sin señal.
    const despues = await abrirApp()
    const recuperada = despues.estado.sesion
    expect(recuperada.ejercicios[0].series.map((s) => [s.peso, s.reps, s.confirmada])).toEqual([
      [30, 10, true],
      [32.5, 8, true],
    ])
    expect(despues.estado.pendientes).toBe(4)

    // Vuelve la señal.
    servidor.conectado = true
    await despues.sincronizar()

    expect(servidor.recibidas.map((o) => o.url.split('/')[2])).toEqual(['sesiones', 'sesiones', 'series', 'series'])
    expect(servidor.recibidas[2].cuerpo).toMatchObject({ peso: 30, reps: 10, confirmada: true })
    expect(despues.estado.pendientes).toBe(0)
  })

  it('mientras haya cambios sin enviar, la sesión del celular manda sobre la del servidor', async () => {
    servidor.conectado = false
    const antes = await abrirApp()
    await antes.empezarSesionLibre()
    await antes.agregarEjercicio('Press inclinado', 'Pecho')

    // Hay señal pero el servidor aún no sabe de esta sesión cuando se pide el arranque.
    servidor.conectado = true
    servidor.recibidas = []
    const despues = await abrirApp()

    expect(despues.estado.sesion?.ejercicios[0].nombre).toBe('Press inclinado')
  })
})

describe('RF-006-08: cierre a las 2 horas sin conexión', () => {
  it('una sesión olvidada se termina sola al abrir la app, con fin a las 2 horas', async () => {
    servidor.conectado = false
    const antes = await abrirApp()
    await antes.empezarSesionLibre()
    await antes.agregarEjercicio('Press inclinado', 'Pecho')
    const ejercicio = antes.estado.sesion.ejercicios[0]
    await antes.confirmarSerie(ejercicio, ejercicio.series[0], { peso: 30, reps: 10 })
    const inicio = new Date(antes.estado.sesion.inicio)

    vi.useFakeTimers({ now: inicio.getTime() + 3 * 60 * 60 * 1000, toFake: ['Date'] })
    try {
      const despues = await abrirApp()

      expect(despues.estado.sesion).toBeNull()
      servidor.conectado = true
      await despues.sincronizar()
      const cierre = servidor.recibidas.at(-1)
      expect(cierre.cuerpo.fin).toBe(new Date(inicio.getTime() + 2 * 60 * 60 * 1000).toISOString())
    } finally {
      vi.useRealTimers()
    }
  })
})

describe('salir de la cuenta', () => {
  it('borra del celular la sesión y los pendientes', async () => {
    servidor.conectado = false
    const app = await abrirApp()
    await app.empezarSesionLibre()

    await app.olvidarDatosLocales()

    expect(app.estado.sesion).toBeNull()
    expect(app.estado.pendientes).toBe(0)
    const otra = await abrirApp()
    expect(otra.estado.sesion).toBeNull()
  })
})

describe('T-002-12: catálogo y rutinas guardados en el celular', () => {
  it('con conexión, el arranque trae el catálogo y las rutinas', async () => {
    const { estado } = await abrirApp()

    expect(estado.catalogo).toEqual(CATALOGO)
    expect(estado.rutinas).toEqual([PECHO])
  })

  it('sin señal siguen disponibles los que trajo la última vez', async () => {
    await abrirApp()

    servidor.conectado = false
    const { estado } = await abrirApp()

    expect(estado.rutinas.map((r) => r.nombre)).toEqual(['Pecho'])
    expect(estado.catalogo.grupos).toHaveLength(2)
  })
})

describe('T-002-13: empezar una sesión desde una rutina, también sin señal', () => {
  it('CA-006-17a: en modo avión se empieza con la rutina guardada y todo queda pendiente en orden', async () => {
    await abrirApp() // ayer, con señal
    servidor.conectado = false
    const app = await abrirApp() // hoy, en modo avión

    await app.empezarSesionDesdeRutina(app.estado.rutinas[0])

    const sesion = app.estado.sesion
    expect(sesion.nombre).toBe('Pecho')
    expect(sesion.ejercicios.map((e) => e.series.length)).toEqual([2, 1])
    // RF-008-03: la referencia (el récord 32,5 × 8 supera lo previsto 30 × 10).
    expect(sesion.ejercicios[0].series[0]).toMatchObject({ peso: 32.5, reps: 8, origen: 'record' })
    expect(app.estado.pendientes).toBe(3) // la sesión y sus dos ejercicios

    servidor.conectado = true
    await app.sincronizar()

    const [inicio, ...ejercicios] = servidor.recibidas
    expect(inicio.cuerpo).toMatchObject({ nombre: 'Pecho', rutina: 'rutina-pecho', fin: null })
    expect(ejercicios.map((o) => o.cuerpo.nombre)).toEqual(['Press inclinado', 'Aperturas'])
  })

  it('cerrar y abrir la app a mitad de una sesión de rutina la conserva', async () => {
    await abrirApp()
    servidor.conectado = false
    const antes = await abrirApp()
    await antes.empezarSesionDesdeRutina(PECHO)

    const despues = await abrirApp()

    expect(despues.estado.sesion?.rutina).toBe('rutina-pecho')
    expect(despues.estado.sesion.ejercicios).toHaveLength(2)
  })

  it('no se puede empezar otra con una sesión en curso', async () => {
    const app = await abrirApp()
    await app.empezarSesionLibre()

    expect(() => app.empezarSesionDesdeRutina(PECHO)).toThrow('Ya tienes una sesión en curso.')
  })
})

describe('T-004-11: recientes y rutinas hechas hoy, también sin señal (RF-004-07, 10 · RNF-004-01)', () => {
  const hoy = () => fechaLocal(new Date())
  const RECIENTE = (n) => ({ id: `s-${n}`, nombre: `Sesión ${n}`, inicio: '2026-11-09T18:00:00-05:00', rutina: null })

  async function hacerSerie(app) {
    const ejercicio = app.estado.sesion.ejercicios[0]
    await app.confirmarSerie(ejercicio, ejercicio.series[0], { peso: 30, reps: 10 })
  }

  it('con conexión, el arranque trae las recientes y las hechas hoy', async () => {
    servidor.recientes = [RECIENTE(1)]
    servidor.hechasHoy = { fecha: hoy(), rutinas: ['rutina-pecho'] }

    const { estado } = await abrirApp()

    expect(estado.recientes).toEqual([RECIENTE(1)])
    expect(estado.hechasHoy).toEqual({ fecha: hoy(), rutinas: ['rutina-pecho'] })
  })

  it('al terminar una sesión de rutina sin señal, queda primera en recientes y su rutina como hecha', async () => {
    servidor.recientes = [RECIENTE(1), RECIENTE(2), RECIENTE(3)]
    await abrirApp()
    servidor.conectado = false
    const app = await abrirApp()
    await app.empezarSesionDesdeRutina(PECHO)
    await hacerSerie(app)

    await app.terminarSesion('', '')

    expect(app.estado.recientes.map((s) => s.nombre)).toEqual(['Pecho', 'Sesión 1', 'Sesión 2'])
    expect(app.estado.recientes[0]).toMatchObject({ rutina: 'rutina-pecho' })
    expect(rutinasHechasHoy(app.estado.hechasHoy, hoy())).toEqual(['rutina-pecho'])

    const reabierta = await abrirApp() // sigue sin señal
    expect(reabierta.estado.recientes[0].nombre).toBe('Pecho')
    expect(rutinasHechasHoy(reabierta.estado.hechasHoy, hoy())).toEqual(['rutina-pecho'])
  })

  it('una lista de hechas de ayer se reemplaza por la de hoy', async () => {
    servidor.hechasHoy = { fecha: '2020-01-01', rutinas: ['vieja'] }
    await abrirApp()
    servidor.conectado = false
    const app = await abrirApp()
    await app.empezarSesionDesdeRutina(PECHO)
    await hacerSerie(app)

    await app.terminarSesion('', '')

    expect(app.estado.hechasHoy).toEqual({ fecha: hoy(), rutinas: ['rutina-pecho'] })
  })

  it('una sesión vacía que se descarta no entra en recientes', async () => {
    const app = await abrirApp()
    await app.empezarSesionLibre()

    await app.terminarSesion('', '')

    expect(app.estado.recientes).toEqual([])
  })

  it('una sesión libre no marca ninguna rutina', async () => {
    const app = await abrirApp()
    await app.empezarSesionLibre()
    app.agregarEjercicio('Sentadilla', 'Pierna')
    await hacerSerie(app)

    await app.terminarSesion('', '')

    expect(app.estado.recientes[0]).toMatchObject({ nombre: 'Sesión libre', rutina: null })
    expect(rutinasHechasHoy(app.estado.hechasHoy, hoy())).toEqual([])
  })

  it('al salir de la cuenta se olvidan', async () => {
    servidor.recientes = [RECIENTE(1)]
    const app = await abrirApp()

    await app.olvidarDatosLocales()

    expect(app.estado.recientes).toEqual([])
    expect(app.estado.hechasHoy).toBeNull()
  })
})
