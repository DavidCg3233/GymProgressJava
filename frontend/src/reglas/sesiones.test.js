// Reglas del ciclo de vida de una sesión de entrenamiento.
// Spec 006 · RF-006-08, RF-006-19 · RN-006-06, RN-006-09, RN-006-12.
// Esta copia existe para que el cierre a las 2 horas funcione sin conexión.

import { describe, expect, it } from 'vitest'

import {
  DURACION_MAXIMA_MS,
  debeCerrarse,
  debeDescartarse,
  horaDeCierreAutomatico,
} from './sesiones.js'

// 6:00 p. m. en Bogotá (UTC-5), como en CA-006-08a.
const INICIO = new Date('2026-11-09T18:00:00-05:00')

const despuesDe = ({ horas = 0, minutos = 0, segundos = 0 }) =>
  new Date(INICIO.getTime() + ((horas * 60 + minutos) * 60 + segundos) * 1000)

describe('cierre automático de una sesión (RF-006-08)', () => {
  it('la duración máxima es de dos horas', () => {
    expect(DURACION_MAXIMA_MS).toBe(2 * 60 * 60 * 1000)
  })

  it('RN-006-12: la hora de cierre es el inicio más dos horas', () => {
    expect(horaDeCierreAutomatico(INICIO)).toEqual(new Date('2026-11-09T20:00:00-05:00'))
  })

  it.each([
    ['recién empezada', {}, false],
    ['un segundo antes de las 2 horas', { horas: 1, minutos: 59, segundos: 59 }, false],
    ['justo a las 2 horas', { horas: 2 }, true],
    ['CA-006-08a: 8:01 p. m.', { horas: 2, minutos: 1 }, true],
    ['días después', { horas: 72 }, true],
  ])('%s', (_caso, transcurrido, esperado) => {
    expect(debeCerrarse(INICIO, despuesDe(transcurrido))).toBe(esperado)
  })

  it('no depende de la zona horaria en que se exprese la hora', () => {
    const ochoYUnoEnUtc = new Date('2026-11-10T01:01:00Z')

    expect(debeCerrarse(INICIO, ochoYUnoEnUtc)).toBe(true)
  })

  it('rechaza fechas inválidas en lugar de decidir con ellas', () => {
    expect(() => debeCerrarse(new Date('no es una fecha'), INICIO)).toThrow(TypeError)
    expect(() => debeCerrarse(INICIO, '2026-11-09')).toThrow(TypeError)
  })
})

describe('sesión sin series confirmadas (RF-006-19)', () => {
  it.each([
    ['CA-006-19a: sin series confirmadas', 0, true],
    ['con una serie confirmada', 1, false],
    ['CA-006-08a: con cinco series', 5, false],
  ])('%s', (_caso, seriesConfirmadas, esperado) => {
    expect(debeDescartarse(seriesConfirmadas)).toBe(esperado)
  })

  it('la cantidad de series confirmadas no puede ser negativa ni fraccionaria', () => {
    expect(() => debeDescartarse(-1)).toThrow(RangeError)
    expect(() => debeDescartarse(1.5)).toThrow(RangeError)
  })
})
