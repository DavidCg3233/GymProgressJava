// Cómo habla la pantalla con el servidor.

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { ErrorDeApi, pedir } from './api.js'

function respuesta(estado, cuerpo) {
  return {
    ok: estado >= 200 && estado < 300,
    status: estado,
    json: async () => {
      if (cuerpo === undefined) throw new SyntaxError('sin cuerpo')
      return cuerpo
    },
  }
}

beforeEach(() => {
  vi.stubGlobal('document', { cookie: 'otra=1; csrftoken=TOKEN123; mas=2' })
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('peticiones', () => {
  it('una consulta devuelve los datos del servidor', async () => {
    const fetch = vi.fn().mockResolvedValue(respuesta(200, { autenticado: true }))
    vi.stubGlobal('fetch', fetch)

    expect(await pedir('GET', '/api/acceso/')).toEqual({ autenticado: true })
    expect(fetch).toHaveBeenCalledWith('/api/acceso/', expect.objectContaining({ method: 'GET', credentials: 'same-origin' }))
  })

  it('una escritura envía el cuerpo como JSON y el token de protección CSRF', async () => {
    const fetch = vi.fn().mockResolvedValue(respuesta(200, {}))
    vi.stubGlobal('fetch', fetch)

    await pedir('PUT', '/api/series/1/', { peso: 30 })

    const [, opciones] = fetch.mock.calls[0]
    expect(opciones.body).toBe('{"peso":30}')
    expect(opciones.headers['Content-Type']).toBe('application/json')
    expect(opciones.headers['X-CSRFToken']).toBe('TOKEN123')
  })

  it('una consulta no envía el token ni cuerpo', async () => {
    const fetch = vi.fn().mockResolvedValue(respuesta(200, {}))
    vi.stubGlobal('fetch', fetch)

    await pedir('GET', '/api/arranque/')

    const [, opciones] = fetch.mock.calls[0]
    expect(opciones.headers['X-CSRFToken']).toBeUndefined()
    expect(opciones.body).toBeUndefined()
  })

  it('una respuesta sin contenido devuelve nada', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respuesta(204)))

    expect(await pedir('POST', '/api/acceso/salir/')).toBeNull()
  })
})

describe('errores', () => {
  it('un rechazo del servidor trae su mensaje, su campo y su código', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respuesta(400, { mensaje: 'El peso va de a 0,5 kg.', campo: 'peso' })))

    const error = await pedir('PUT', '/api/series/1/', {}).catch((e) => e)

    expect(error).toBeInstanceOf(ErrorDeApi)
    expect(error).toMatchObject({ estado: 400, mensaje: 'El peso va de a 0,5 kg.', campo: 'peso' })
  })

  it('conserva los datos extra del rechazo', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respuesta(409, { mensaje: 'Ya tienes una sesión en curso.', sesion_en_curso: 'abc' })))

    const error = await pedir('PUT', '/api/sesiones/x/', {}).catch((e) => e)

    expect(error.datos.sesion_en_curso).toBe('abc')
  })

  it('si el servidor falla sin explicar, se muestra un mensaje genérico y nunca detalles técnicos', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respuesta(500)))

    const error = await pedir('GET', '/api/arranque/').catch((e) => e)

    expect(error.estado).toBe(500)
    expect(error.mensaje).toBe('Algo salió mal. Inténtalo de nuevo.')
  })

  it('sin conexión se avisa con estado 0, para que quien llame pueda reintentar después', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    const error = await pedir('GET', '/api/arranque/').catch((e) => e)

    expect(error).toBeInstanceOf(ErrorDeApi)
    expect(error.estado).toBe(0)
    expect(error.sinConexion).toBe(true)
    expect(error.mensaje).toBe('Sin conexión.')
  })

  it('un rechazo del servidor no se confunde con falta de conexión', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respuesta(401, { mensaje: 'Entra con tu cuenta para continuar.' })))

    const error = await pedir('GET', '/api/arranque/').catch((e) => e)

    expect(error.sinConexion).toBe(false)
  })
})
