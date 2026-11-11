// Validaciones del cuerpo en el celular (T-003-02).
// Espejo de backend/tests/reglas/test_cuerpo.py en lo que aplica: mismos casos, mismos mensajes.

import { describe, expect, it } from 'vitest'

import { validarEstatura, validarFechaDePeso, validarPesoCorporal } from './cuerpo.js'
import { ErrorDeValidacion } from './errores.js'

const HOY = '2026-11-11'

function falla(accion) {
  try {
    accion()
  } catch (error) {
    expect(error).toBeInstanceOf(ErrorDeValidacion)
    return [error.campo, error.mensaje]
  }
  throw new Error('Se esperaba un error de validación y no ocurrió.')
}

describe('peso (RN-003-03)', () => {
  it.each([
    ['20.0', 20],
    ['300.0', 300],
    ['79,5', 79.5],
    [79, 79],
    [78.5, 78.5],
  ])('%j se acepta como %d', (valor, esperado) => {
    expect(validarPesoCorporal(valor)).toBe(esperado)
  })

  it.each([['19.9'], ['300.1'], ['79.55'], ['abc'], [true], ['NaN']])('%j se rechaza', (valor) => {
    expect(falla(() => validarPesoCorporal(valor))).toEqual(['peso', 'El peso va de 20 a 300 kg, con un decimal.'])
  })

  it.each([[null], [''], ['  ']])('%j pide el peso', (valor) => {
    expect(falla(() => validarPesoCorporal(valor))).toEqual(['peso', 'Escribe tu peso.'])
  })
})

describe('estatura (RN-003-04)', () => {
  it.each([[100], [175], [250]])('%i se acepta', (valor) => {
    expect(validarEstatura(valor)).toBe(valor)
  })

  it.each([[99], [251], [1.75], [175.5], ['175'], [true], [null]])('%j se rechaza', (valor) => {
    expect(falla(() => validarEstatura(valor))).toEqual(['estatura', 'La estatura va en centímetros, de 100 a 250.'])
  })
})

describe('fecha (RN-003-05)', () => {
  it.each([['2026-11-11'], ['2020-02-29']])('%s se acepta', (valor) => {
    expect(validarFechaDePeso(valor, HOY)).toBe(valor)
  })

  it('CA-003-13a: mañana se rechaza', () => {
    expect(falla(() => validarFechaDePeso('2026-11-12', HOY))).toEqual(['fecha', 'La fecha no puede ser futura.'])
  })

  it.each([[null], [''], ['11/11/2026'], ['2026-02-30'], [20261111]])('%j no es una fecha válida', (valor) => {
    expect(falla(() => validarFechaDePeso(valor, HOY))).toEqual(['fecha', 'Escribe una fecha válida.'])
  })
})
