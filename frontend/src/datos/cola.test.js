// Cola de pendientes (T-006-31 · RF-006-16, RF-006-18, RNF-ACC-02, RNF-006-07).
//
// Cada cambio hecho en el celular entra a la cola y sale cuando el servidor lo
// acepta. Sin conexión, espera. Nada se pierde al cerrar la app.

import { describe, expect, it, vi } from 'vitest'

import { ErrorDeApi } from './api.js'
import { crearCola } from './cola.js'

function almacenEnMemoria() {
  const datos = new Map()
  return {
    leer: async (clave) => structuredClone(datos.get(clave) ?? null),
    guardar: async (clave, valor) => void datos.set(clave, structuredClone(valor)),
    borrarTodo: async () => datos.clear(),
  }
}

const op = (url, cuerpo = {}, metodo = 'PUT') => ({ metodo, url, cuerpo })
const sinConexion = () => new ErrorDeApi(0, 'Sin conexión.')
const rechazo = (estado, mensaje = 'No.') => new ErrorDeApi(estado, mensaje)

function servidor() {
  const recibidas = []
  let falla = null
  const enviar = vi.fn(async (operacion) => {
    if (falla) throw falla(operacion)
    recibidas.push(operacion)
  })
  return {
    enviar,
    recibidas,
    caer: () => (falla = sinConexion),
    fallarCon: (crear) => (falla = crear),
    volver: () => (falla = null),
  }
}

describe('con conexión', () => {
  it('envía en el orden en que se hicieron los cambios', async () => {
    const srv = servidor()
    const cola = crearCola({ almacen: almacenEnMemoria(), enviar: srv.enviar })

    await cola.agregar(op('/sesion'))
    await cola.agregar(op('/ejercicio'))
    await cola.agregar(op('/serie'))
    const resultado = await cola.procesar()

    expect(srv.recibidas.map((o) => o.url)).toEqual(['/sesion', '/ejercicio', '/serie'])
    expect(resultado).toEqual({ pendientes: 0, detenida: null, rechazos: [] })
    expect(await cola.pendientes()).toBe(0)
  })

  it('si se procesa dos veces a la vez, no envía nada repetido', async () => {
    const srv = servidor()
    const cola = crearCola({ almacen: almacenEnMemoria(), enviar: srv.enviar })
    await cola.agregar(op('/a'))
    await cola.agregar(op('/b'))

    await Promise.all([cola.procesar(), cola.procesar(), cola.procesar()])

    expect(srv.enviar).toHaveBeenCalledTimes(2)
  })

  it('lo que se agrega mientras se envía también sale en la misma vuelta', async () => {
    const srv = servidor()
    const cola = crearCola({ almacen: almacenEnMemoria(), enviar: srv.enviar })
    await cola.agregar(op('/a'))

    const procesando = cola.procesar()
    await cola.agregar(op('/b'))
    await procesando

    expect(srv.recibidas.map((o) => o.url)).toEqual(['/a', '/b'])
  })
})

describe('RF-006-16: sin conexión', () => {
  it('nada se envía y todo queda pendiente, en orden', async () => {
    const srv = servidor()
    srv.caer()
    const cola = crearCola({ almacen: almacenEnMemoria(), enviar: srv.enviar })
    await cola.agregar(op('/sesion'))
    await cola.agregar(op('/serie'))

    const resultado = await cola.procesar()

    expect(resultado).toMatchObject({ pendientes: 2, detenida: 'sin-conexion' })
    // Se detiene en el primero: no tiene sentido intentar el resto.
    expect(srv.enviar).toHaveBeenCalledTimes(1)
  })

  it('al volver la conexión se envía todo, en el orden original', async () => {
    const srv = servidor()
    srv.caer()
    const cola = crearCola({ almacen: almacenEnMemoria(), enviar: srv.enviar })
    for (const url of ['/sesion', '/ejercicio', '/serie-1', '/serie-2']) await cola.agregar(op(url))
    await cola.procesar()

    srv.volver()
    await cola.procesar()

    expect(srv.recibidas.map((o) => o.url)).toEqual(['/sesion', '/ejercicio', '/serie-1', '/serie-2'])
    expect(await cola.pendientes()).toBe(0)
  })

  it('RNF-006-06: lo pendiente sobrevive a cerrar y abrir la app', async () => {
    const almacen = almacenEnMemoria()
    const srv = servidor()
    srv.caer()
    const antes = crearCola({ almacen, enviar: srv.enviar })
    await antes.agregar(op('/sesion'))
    await antes.agregar(op('/serie'))

    srv.volver()
    const despues = crearCola({ almacen, enviar: srv.enviar }) // la app se volvió a abrir
    expect(await despues.pendientes()).toBe(2)
    await despues.procesar()

    expect(srv.recibidas.map((o) => o.url)).toEqual(['/sesion', '/serie'])
  })

  it('un error del servidor (5xx) se trata como pasajero: se reintenta después', async () => {
    const srv = servidor()
    srv.fallarCon(() => rechazo(502))
    const cola = crearCola({ almacen: almacenEnMemoria(), enviar: srv.enviar })
    await cola.agregar(op('/serie'))

    expect(await cola.procesar()).toMatchObject({ pendientes: 1, detenida: 'sin-conexion' })
  })
})

describe('el mismo dato cambiado varias veces sin conexión', () => {
  it('dos cambios seguidos sobre el mismo dato se fusionan: solo viaja el último', async () => {
    const srv = servidor()
    srv.caer()
    const cola = crearCola({ almacen: almacenEnMemoria(), enviar: srv.enviar })
    await cola.agregar(op('/serie-1', { peso: 30 }))
    await cola.agregar(op('/serie-1', { peso: 32.5 })) // corregí de inmediato

    srv.volver()
    await cola.procesar()

    expect(srv.recibidas.map((o) => [o.url, o.cuerpo.peso])).toEqual([['/serie-1', 32.5]])
  })

  it('si hay otros cambios en medio, se conservan los dos y en orden', async () => {
    const srv = servidor()
    srv.caer()
    const cola = crearCola({ almacen: almacenEnMemoria(), enviar: srv.enviar })
    await cola.agregar(op('/ejercicio'))
    await cola.agregar(op('/serie-1', { peso: 30 }))
    await cola.agregar(op('/serie-2', { peso: 30 }))
    await cola.agregar(op('/serie-1', { peso: 32.5 }))

    srv.volver()
    await cola.procesar()

    expect(srv.recibidas.map((o) => [o.url, o.cuerpo.peso])).toEqual([
      ['/ejercicio', undefined],
      ['/serie-1', 30],
      ['/serie-2', 30],
      ['/serie-1', 32.5],
    ])
  })

  it('el cierre de una sesión viaja después de sus series, nunca en el lugar de su inicio', async () => {
    // Si el cierre se adelantara, el servidor vería una sesión terminada sin series,
    // la descartaría, y luego rechazaría todas las series: se perdería el entrenamiento.
    const srv = servidor()
    srv.caer()
    const cola = crearCola({ almacen: almacenEnMemoria(), enviar: srv.enviar })
    await cola.agregar(op('/sesion', { fin: null }))
    await cola.agregar(op('/ejercicio'))
    await cola.agregar(op('/serie-1'))
    await cola.agregar(op('/sesion', { fin: '20:00' }))

    srv.volver()
    await cola.procesar()

    expect(srv.recibidas.map((o) => o.url)).toEqual(['/sesion', '/ejercicio', '/serie-1', '/sesion'])
    expect(srv.recibidas.at(-1).cuerpo.fin).toBe('20:00')
  })

  it('confirmar y luego quitar una serie se envían las dos cosas', async () => {
    const srv = servidor()
    const cola = crearCola({ almacen: almacenEnMemoria(), enviar: srv.enviar })
    await cola.agregar(op('/serie-1'))
    await cola.agregar(op('/serie-1', {}, 'DELETE'))

    await cola.procesar()

    expect(srv.recibidas.map((o) => o.metodo)).toEqual(['PUT', 'DELETE'])
  })

  it('si un dato cambia mientras se está enviando, la versión nueva también se envía', async () => {
    const almacen = almacenEnMemoria()
    let soltar
    const enviar = vi.fn()
    enviar.mockImplementationOnce(() => new Promise((resolver) => (soltar = resolver)))
    enviar.mockResolvedValue(undefined)
    const cola = crearCola({ almacen, enviar })
    await cola.agregar(op('/serie-1', { peso: 30 }))

    const procesando = cola.procesar()
    await vi.waitFor(() => expect(soltar).toBeTypeOf('function'))
    await cola.agregar(op('/serie-1', { peso: 32.5 }))
    soltar()
    await procesando

    expect(enviar.mock.calls.map(([o]) => o.cuerpo.peso)).toEqual([30, 32.5])
    expect(await cola.pendientes()).toBe(0)
  })
})

describe('rechazos del servidor', () => {
  it('un dato inválido se saca de la cola y se informa, sin bloquear lo demás', async () => {
    const srv = servidor()
    const cola = crearCola({ almacen: almacenEnMemoria(), enviar: srv.enviar })
    srv.enviar.mockRejectedValueOnce(rechazo(400, 'El peso va de a 0,5 kg.'))
    await cola.agregar(op('/serie-1'))
    await cola.agregar(op('/serie-2'))

    const resultado = await cola.procesar()

    expect(resultado.pendientes).toBe(0)
    expect(resultado.rechazos).toEqual([{ operacion: op('/serie-1'), mensaje: 'El peso va de a 0,5 kg.' }])
    expect(srv.recibidas.map((o) => o.url)).toEqual(['/serie-2'])
  })

  it('quitar algo que el servidor ya no tiene (404) cuenta como hecho', async () => {
    const srv = servidor()
    const cola = crearCola({ almacen: almacenEnMemoria(), enviar: srv.enviar })
    srv.enviar.mockRejectedValueOnce(rechazo(404))
    await cola.agregar(op('/serie-1', {}, 'DELETE'))

    expect(await cola.procesar()).toEqual({ pendientes: 0, detenida: null, rechazos: [] })
  })

  it('RNF-ACC-02: si venció el acceso (401), la cola se conserva entera', async () => {
    const srv = servidor()
    srv.fallarCon(() => rechazo(401))
    const cola = crearCola({ almacen: almacenEnMemoria(), enviar: srv.enviar })
    await cola.agregar(op('/sesion'))
    await cola.agregar(op('/serie'))

    expect(await cola.procesar()).toMatchObject({ pendientes: 2, detenida: 'acceso' })

    srv.volver() // volvió a entrar
    await cola.procesar()
    expect(srv.recibidas).toHaveLength(2)
  })

  it('con la protección CSRF vencida (403) también espera, en vez de descartar', async () => {
    const srv = servidor()
    srv.fallarCon(() => rechazo(403))
    const cola = crearCola({ almacen: almacenEnMemoria(), enviar: srv.enviar })
    await cola.agregar(op('/serie'))

    expect(await cola.procesar()).toMatchObject({ pendientes: 1, detenida: 'acceso' })
  })
})

describe('RF-006-18: avisar cuántos cambios faltan por enviar', () => {
  it('avisa cada vez que cambia la cantidad de pendientes', async () => {
    const avisos = []
    const srv = servidor()
    const cola = crearCola({ almacen: almacenEnMemoria(), enviar: srv.enviar, alCambiar: (n) => avisos.push(n) })

    await cola.agregar(op('/a'))
    await cola.agregar(op('/b'))
    await cola.procesar()

    expect(avisos).toEqual([1, 2, 1, 0])
  })

  it('vaciar la cola (al salir de la cuenta) deja cero pendientes', async () => {
    const srv = servidor()
    srv.caer()
    const cola = crearCola({ almacen: almacenEnMemoria(), enviar: srv.enviar })
    await cola.agregar(op('/a'))

    await cola.vaciar()

    expect(await cola.pendientes()).toBe(0)
  })
})
