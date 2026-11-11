// Reglas de una rutina (T-002-02).
// Espejo de backend/tests/reglas/test_rutinas.py: mismos casos, mismos mensajes.

import { describe, expect, it } from 'vitest'

import { ErrorDeValidacion } from './errores.js'
import {
  MAXIMO_DE_EJERCICIOS,
  bitsADias,
  diasABits,
  nombreDeCopia,
  tieneDia,
  validarDias,
  validarEjerciciosDeRutina,
  validarNombreDeRutina,
  validarSeriesPrevistas,
} from './rutinas.js'

function falla(accion) {
  try {
    accion()
  } catch (error) {
    expect(error).toBeInstanceOf(ErrorDeValidacion)
    return error
  }
  throw new Error('Se esperaba un error de validación y no ocurrió.')
}

describe('nombre (RN-002-01)', () => {
  it('se guarda sin espacios sobrantes', () => {
    expect(validarNombreDeRutina('  Pecho ')).toBe('Pecho')
  })

  it('CA-002-RN: 50 caracteres se aceptan', () => {
    expect(validarNombreDeRutina('r'.repeat(50))).toBe('r'.repeat(50))
  })

  it('CA-002-RN: 51 caracteres se rechazan', () => {
    const error = falla(() => validarNombreDeRutina('r'.repeat(51)))

    expect([error.campo, error.mensaje]).toEqual(['nombre', 'El nombre de la rutina admite máximo 50 caracteres.'])
  })

  it.each([[null], [''], ['   ']])('CA-002-03a: sin nombre (%j) se rechaza', (valor) => {
    const error = falla(() => validarNombreDeRutina(valor))

    expect([error.campo, error.mensaje]).toEqual(['nombre', 'Escribe el nombre de la rutina.'])
  })
})

describe('días (RN-002-02)', () => {
  it.each([
    [[], []],
    [[1], [1]],
    [[4, 1], [1, 4]],
    [[1, 2, 3, 4, 5, 6, 7], [1, 2, 3, 4, 5, 6, 7]],
  ])('%j son válidos y quedan en orden', (entrada, esperado) => {
    expect(validarDias(entrada)).toEqual(esperado)
  })

  it.each([[[0]], [[8]], [[1, 1]], [['lunes']], [[true]], [null], ['1,4']])('%j se rechaza', (entrada) => {
    const error = falla(() => validarDias(entrada))

    expect([error.campo, error.mensaje]).toEqual(['dias', 'Los días van de lunes (1) a domingo (7), sin repetir.'])
  })

  it.each([
    [[], 0],
    [[1], 1],
    [[7], 64],
    [[1, 4], 9],
    [[1, 2, 3, 4, 5, 6, 7], 127],
  ])('%j se guarda como %i y vuelve igual', (dias, bits) => {
    expect(diasABits(dias)).toBe(bits)
    expect(bitsADias(bits)).toEqual(dias)
  })

  it('dice si la rutina toca un día', () => {
    const lunesYJueves = diasABits([1, 4])

    expect([1, 2, 3, 4, 5, 6, 7].map((dia) => tieneDia(lunesYJueves, dia))).toEqual([true, false, false, true, false, false, false])
  })
})

describe('ejercicios de la rutina (RN-002-03)', () => {
  const claves = (cantidad) => Array.from({ length: cantidad }, (_, n) => `ejercicio ${n}`)

  it('CA-002-RN: 20 se aceptan', () => {
    expect(() => validarEjerciciosDeRutina(claves(20))).not.toThrow()
    expect(MAXIMO_DE_EJERCICIOS).toBe(20)
  })

  it('CA-002-RN: 21 se rechazan', () => {
    const error = falla(() => validarEjerciciosDeRutina(claves(21)))

    expect([error.campo, error.mensaje]).toEqual(['ejercicios', 'Una rutina admite máximo 20 ejercicios.'])
  })

  it('CA-002-03a: sin ejercicios se rechaza', () => {
    const error = falla(() => validarEjerciciosDeRutina([]))

    expect([error.campo, error.mensaje]).toEqual(['ejercicios', 'Agrega al menos un ejercicio.'])
  })

  it('CA-002-RN: el mismo ejercicio dos veces se rechaza', () => {
    const error = falla(() => validarEjerciciosDeRutina(['press inclinado', 'fondos', 'press inclinado']))

    expect([error.campo, error.mensaje]).toEqual(['ejercicios', 'Un ejercicio aparece una sola vez por rutina.'])
  })
})

describe('series previstas (RN-002-04)', () => {
  it.each([[1], [3], [10]])('%i se acepta', (valor) => {
    expect(validarSeriesPrevistas(valor)).toBe(valor)
  })

  it.each([[0], [11], [2.5], ['3'], [null], [true]])('%j se rechaza', (valor) => {
    const error = falla(() => validarSeriesPrevistas(valor))

    expect([error.campo, error.mensaje]).toEqual(['series', 'Las series previstas van de 1 a 10.'])
  })
})

describe('nombre de una copia (RF-002-21, plan 002 sección 6)', () => {
  it('CA-002-21a: la primera se llama "(copia)"', () => {
    expect(nombreDeCopia('Pecho', ['Pecho'])).toBe('Pecho (copia)')
  })

  it('la segunda se numera', () => {
    expect(nombreDeCopia('Pecho', ['Pecho', 'Pecho (copia)'])).toBe('Pecho (copia 2)')
  })

  it('sigue hasta encontrar un nombre libre, sin distinguir mayúsculas', () => {
    expect(nombreDeCopia('Pecho', ['Pecho', 'Pecho (copia)', 'Pecho (copia 2)', 'pecho (COPIA 3)'])).toBe('Pecho (copia 4)')
  })

  it('nunca pasa de 50 caracteres', () => {
    const copia = nombreDeCopia('r'.repeat(50), ['r'.repeat(50)])

    expect(copia).toHaveLength(50)
    expect(copia.endsWith(' (copia)')).toBe(true)
  })
})
