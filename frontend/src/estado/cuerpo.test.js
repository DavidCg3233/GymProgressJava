// Estado del peso corporal en el celular (T-003-09 · RF-003-02 · RNF-003-02).

import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ErrorDeApi } from '../datos/api.js'
import { ErrorDeValidacion } from '../reglas/errores.js'
import { fechaLocal } from '../reglas/progreso.js'

const servidor = { respuestas: [], recibidas: [] }

vi.mock('../datos/api.js', async (original) => {
  const real = await original()
  return {
    ...real,
    pedir: vi.fn(async (metodo, url, cuerpo) => {
      servidor.recibidas.push({ metodo, url, cuerpo })
      const siguiente = servidor.respuestas.shift()
      if (siguiente instanceof Error) throw siguiente
      return siguiente ?? null
    }),
  }
})

const { mensajeDePeso, registrarPeso } = await import('./cuerpo.js')

const HOY = fechaLocal(new Date())

beforeEach(() => {
  servidor.respuestas = []
  servidor.recibidas = []
})

describe('registrar el peso', () => {
  it('envía la fecha en la dirección y el peso validado', async () => {
    servidor.respuestas = [{ registro: { fecha: HOY, peso: 79.5 } }]

    const resultado = await registrarPeso({ fecha: HOY, peso: '79,5' })

    expect(resultado).toEqual({ registro: { fecha: HOY, peso: 79.5 } })
    expect(servidor.recibidas).toEqual([{ metodo: 'PUT', url: `/api/peso/${HOY}/`, cuerpo: { peso: 79.5, reemplazar: false } }])
  })

  it('CA-003-02a: si ya hay un peso ese día, pide confirmar en lugar de fallar', async () => {
    servidor.respuestas = [new ErrorDeApi(409, 'Ya registraste 79,0 kg ese día.', { peso: 79 })]

    const resultado = await registrarPeso({ fecha: HOY, peso: 78.5 })

    expect(resultado).toEqual({ confirmar: 'Ya registraste 79,0 kg ese día.' })
  })

  it('al confirmar, reenvía con reemplazar', async () => {
    servidor.respuestas = [{ registro: { fecha: HOY, peso: 78.5 } }]

    await registrarPeso({ fecha: HOY, peso: 78.5, reemplazar: true })

    expect(servidor.recibidas[0].cuerpo).toEqual({ peso: 78.5, reemplazar: true })
  })

  it('un peso fuera de rango se rechaza sin esperar a la red', async () => {
    await expect(registrarPeso({ fecha: HOY, peso: 19.9 })).rejects.toBeInstanceOf(ErrorDeValidacion)
    expect(servidor.recibidas).toEqual([])
  })

  it('una fecha futura se rechaza sin esperar a la red', async () => {
    await expect(registrarPeso({ fecha: '2999-01-01', peso: 79 })).rejects.toThrow('La fecha no puede ser futura.')
    expect(servidor.recibidas).toEqual([])
  })
})

describe('RNF-003-02: sin conexión se dice y no se pierde lo escrito', () => {
  it.each([[0], [502]])('estado %i: pide conexión y avisa que lo escrito sigue ahí', (estado) => {
    expect(mensajeDePeso(new ErrorDeApi(estado, 'x'))).toBe(
      'Para guardar tu peso necesitas conexión. Lo que escribiste sigue aquí.',
    )
  })

  it('un error del servidor con motivo se muestra tal cual', () => {
    expect(mensajeDePeso(new ErrorDeApi(400, 'La fecha no puede ser futura.'))).toBe('La fecha no puede ser futura.')
  })
})
