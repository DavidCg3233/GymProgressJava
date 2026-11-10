// Reglas de un ejercicio dentro de una sesión.
// Deben coincidir con backend/tests/reglas/test_ejercicios.py.

import { describe, expect, it } from 'vitest'

import { claveDeEjercicio, validarGrupoMuscular, validarNombreDeEjercicio, SERIES_MAXIMAS } from './ejercicios.js'
import { ErrorDeValidacion } from './errores.js'

function capturarError(accion) {
  try {
    accion()
  } catch (error) {
    return error
  }
  throw new Error('Se esperaba un error de validación y no ocurrió.')
}

describe('nombre de ejercicio (RN-002-07)', () => {
  it('se guarda sin espacios sobrantes', () => {
    expect(validarNombreDeEjercicio('  Press inclinado ')).toBe('Press inclinado')
  })

  it('acepta 50 caracteres', () => {
    expect(validarNombreDeEjercicio('e'.repeat(50))).toBe('e'.repeat(50))
  })

  it.each([[null], [undefined], [''], ['   ']])('vacío (%j) se rechaza', (entrada) => {
    const error = capturarError(() => validarNombreDeEjercicio(entrada))

    expect(error).toBeInstanceOf(ErrorDeValidacion)
    expect(error.campo).toBe('nombre')
    expect(error.mensaje).toBe('Escribe el nombre del ejercicio.')
  })

  it('rechaza 51 caracteres', () => {
    const error = capturarError(() => validarNombreDeEjercicio('e'.repeat(51)))

    expect(error.mensaje).toBe('El nombre del ejercicio admite máximo 50 caracteres.')
  })
})

describe('grupo muscular (RN-002-08)', () => {
  it('se guarda sin espacios sobrantes', () => {
    expect(validarGrupoMuscular(' Pecho ')).toBe('Pecho')
  })

  it.each([[null], [''], ['  ']])('vacío (%j) se rechaza', (entrada) => {
    const error = capturarError(() => validarGrupoMuscular(entrada))

    expect(error.campo).toBe('grupo')
    expect(error.mensaje).toBe('Elige el grupo muscular.')
  })

  it('rechaza 31 caracteres', () => {
    const error = capturarError(() => validarGrupoMuscular('g'.repeat(31)))

    expect(error.mensaje).toBe('El grupo muscular admite máximo 30 caracteres.')
  })
})

describe('clave para reconocer el mismo ejercicio (RN-006-08)', () => {
  it.each([['Press inclinado'], ['press inclinado'], ['  PRESS   INCLINADO '], ['Préss Inclinádo']])(
    '%j es "press inclinado"',
    (variante) => {
      expect(claveDeEjercicio(variante)).toBe('press inclinado')
    },
  )

  it('ejercicios distintos tienen claves distintas', () => {
    expect(claveDeEjercicio('Press inclinado')).not.toBe(claveDeEjercicio('Press declinado'))
  })

  it('la ñ no se confunde con la n', () => {
    expect(claveDeEjercicio('Peña')).not.toBe(claveDeEjercicio('Pena'))
  })
})

describe('series por ejercicio (RN-006-05)', () => {
  it('el máximo es 10', () => {
    expect(SERIES_MAXIMAS).toBe(10)
  })
})
