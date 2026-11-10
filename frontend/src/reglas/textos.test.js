// Reglas de los textos de una sesión: notas y nombre.
// Spec 006 · RF-006-21, RF-006-22, RF-006-23 · RN-006-14, RN-006-15.

import { describe, expect, it } from 'vitest'

import { ErrorDeValidacion } from './errores.js'
import { NOMBRE_SESION_LIBRE, nombreDeSesionLibre, validarNota } from './textos.js'

describe('notas (RN-006-14): opcionales, hasta 280 caracteres', () => {
  it('acepta una nota válida', () => {
    expect(validarNota('dormí mal')).toBe('dormí mal')
  })

  it('la guarda sin espacios sobrantes', () => {
    expect(validarNota('  subir a 35  ')).toBe('subir a 35')
  })

  it.each([[null], [undefined], [''], ['   ']])('es opcional: %j queda vacía', (entrada) => {
    expect(validarNota(entrada)).toBe('')
  })

  it('acepta 280 caracteres', () => {
    const nota = 'a'.repeat(280)

    expect(validarNota(nota)).toBe(nota)
  })

  it('CA-006-24b: rechaza 281 caracteres indicando el máximo', () => {
    expect(() => validarNota('a'.repeat(281))).toThrow(ErrorDeValidacion)

    try {
      validarNota('a'.repeat(281))
    } catch (error) {
      expect(error.campo).toBe('nota')
      expect(error.mensaje).toBe('La nota admite máximo 280 caracteres.')
    }
  })

  it('mide el límite después de quitar los espacios sobrantes', () => {
    expect(validarNota(` ${'a'.repeat(280)} `)).toBe('a'.repeat(280))
  })
})

describe('nombre de una sesión libre (RF-006-21, RN-006-15)', () => {
  it('CA-006-21a: conserva el nombre que escribe el usuario', () => {
    expect(nombreDeSesionLibre('Hotel Bogotá')).toBe('Hotel Bogotá')
  })

  it.each([[null], [undefined], [''], ['   ']])('CA-006-20a: sin nombre (%j) se llama "Sesión libre"', (entrada) => {
    expect(nombreDeSesionLibre(entrada)).toBe('Sesión libre')
    expect(NOMBRE_SESION_LIBRE).toBe('Sesión libre')
  })

  it('acepta 50 caracteres', () => {
    const nombre = 'n'.repeat(50)

    expect(nombreDeSesionLibre(nombre)).toBe(nombre)
  })

  it('rechaza 51 caracteres indicando el máximo', () => {
    try {
      nombreDeSesionLibre('n'.repeat(51))
      throw new Error('Se esperaba un error de validación.')
    } catch (error) {
      expect(error).toBeInstanceOf(ErrorDeValidacion)
      expect(error.campo).toBe('nombre')
      expect(error.mensaje).toBe('El nombre admite máximo 50 caracteres.')
    }
  })
})
