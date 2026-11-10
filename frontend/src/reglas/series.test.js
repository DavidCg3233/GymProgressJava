// Reglas de una serie: peso y repeticiones.
// Spec 006 · RF-006-24 · RN-006-02, RN-006-03, RN-006-04.
// Las tablas son las del criterio CA-006-24a y deben coincidir, caso por caso
// y mensaje por mensaje, con backend/tests/reglas/test_series.py.

import { describe, expect, it } from 'vitest'

import { ErrorDeValidacion } from './errores.js'
import { validarPeso, validarRepeticiones } from './series.js'

function capturarError(accion) {
  try {
    accion()
  } catch (error) {
    return error
  }
  throw new Error('Se esperaba un error de validación y no ocurrió.')
}

describe('peso de una serie (RN-006-02): de 0 a 500 kg, en múltiplos de 0,5', () => {
  it.each([
    ['CA-006-24a: 0 es peso corporal', '0', 0],
    ['el paso mínimo', '0.5', 0.5],
    ['un valor intermedio', '32.5', 32.5],
    ['CA-006-24a: 500 es el máximo', '500', 500],
    ['acepta números', 30, 30],
    ['acepta coma decimal, como se escribe en Colombia', '32,5', 32.5],
  ])('acepta %s', (_caso, entrada, esperado) => {
    expect(validarPeso(entrada)).toBe(esperado)
  })

  it.each([
    ['CA-006-24a: -0,5 está bajo el mínimo', '-0.5'],
    ['CA-006-24a: 500,5 supera el máximo', '500.5'],
    ['muy por encima del máximo', '1000'],
  ])('rechaza %s indicando el rango', (_caso, entrada) => {
    const error = capturarError(() => validarPeso(entrada))

    expect(error).toBeInstanceOf(ErrorDeValidacion)
    expect(error.campo).toBe('peso')
    expect(error.mensaje).toBe('El peso debe estar entre 0 y 500 kg.')
  })

  it.each([
    ['CA-006-24a: 30,3 no es múltiplo de 0,5', '30.3'],
    ['la mitad del paso', '0.25'],
    ['un número que no cae en el paso', 30.3],
  ])('rechaza %s', (_caso, entrada) => {
    const error = capturarError(() => validarPeso(entrada))

    expect(error.campo).toBe('peso')
    expect(error.mensaje).toBe('El peso va de a 0,5 kg.')
  })

  it.each([
    ['CA-006-24a: vacío', null],
    ['sin definir', undefined],
    ['texto vacío', ''],
    ['solo espacios', '   '],
  ])('rechaza %s pidiendo el dato', (_caso, entrada) => {
    const error = capturarError(() => validarPeso(entrada))

    expect(error.campo).toBe('peso')
    expect(error.mensaje).toBe('Escribe el peso.')
  })

  it.each([
    ['texto', 'treinta'],
    ['no es un número', NaN],
    ['infinito', Infinity],
    ['un booleano no es un peso', true],
    ['número con texto pegado', '30kg'],
  ])('rechaza %s', (_caso, entrada) => {
    const error = capturarError(() => validarPeso(entrada))

    expect(error.campo).toBe('peso')
    expect(error.mensaje).toBe('El peso debe ser un número.')
  })
})

describe('repeticiones de una serie (RN-006-04): entero de 1 a 100', () => {
  it.each([
    ['CA-006-24a: 1 es el mínimo', 1, 1],
    ['un valor intermedio', 8, 8],
    ['CA-006-24a: 100 es el máximo', 100, 100],
    ['acepta texto con un entero', '10', 10],
  ])('acepta %s', (_caso, entrada, esperado) => {
    expect(validarRepeticiones(entrada)).toBe(esperado)
  })

  it.each([
    ['CA-006-24a: 0 está bajo el mínimo', 0],
    ['CA-006-24a: 101 supera el máximo', 101],
    ['negativo', -3],
  ])('rechaza %s indicando el rango', (_caso, entrada) => {
    const error = capturarError(() => validarRepeticiones(entrada))

    expect(error.campo).toBe('reps')
    expect(error.mensaje).toBe('Las repeticiones deben estar entre 1 y 100.')
  })

  it.each([
    ['CA-006-24a: 8,5 no es entero', 8.5],
    ['texto con decimales', '8.5'],
    ['texto', 'ocho'],
    ['un booleano no es una cantidad', true],
  ])('rechaza %s', (_caso, entrada) => {
    const error = capturarError(() => validarRepeticiones(entrada))

    expect(error.campo).toBe('reps')
    expect(error.mensaje).toBe('Las repeticiones deben ser un número entero.')
  })

  it.each([[null], [undefined], [''], ['  ']])('rechaza %j pidiendo el dato', (entrada) => {
    const error = capturarError(() => validarRepeticiones(entrada))

    expect(error.campo).toBe('reps')
    expect(error.mensaje).toBe('Escribe las repeticiones.')
  })
})
