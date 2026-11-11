// Reglas de progreso que usa el celular (T-004-02).
// Espejo de backend/tests/reglas/test_progreso.py en lo que aplica: mismos casos, mismos mensajes.

import { describe, expect, it } from 'vitest'

import { ErrorDeValidacion } from './errores.js'
import { cumple, fechaLocal, inicioDeSemana, rutinasHechasHoy, validarMeta } from './progreso.js'

describe('semana (RN-004-02)', () => {
  it.each([
    ['2026-11-09', '2026-11-09'],
    ['2026-11-12', '2026-11-09'],
    ['2026-11-15', '2026-11-09'],
    ['2026-11-16', '2026-11-16'],
    ['2027-01-01', '2026-12-28'],
  ])('%s es de la semana que empieza el %s', (dia, lunes) => {
    expect(inicioDeSemana(dia)).toBe(lunes)
  })

  it('la fecha local es la del reloj del celular, no la de Londres', () => {
    // 11:30 p. m. del domingo en el celular: sigue siendo domingo (CA-004-05b).
    expect(fechaLocal(new Date(2026, 10, 15, 23, 30))).toBe('2026-11-15')
  })
})

describe('meta (RN-004-08)', () => {
  it.each([
    [3, 4, false],
    [4, 4, true],
    [5, 4, true],
    [9, null, null],
  ])('%i sesiones con meta %j: %j', (sesiones, meta, esperado) => {
    expect(cumple(sesiones, meta)).toBe(esperado)
  })

  it.each([[1], [4], [14], [null]])('%j es válida', (valor) => {
    expect(validarMeta(valor)).toBe(valor)
  })

  it.each([[0], [15], [-1], [2.5], ['4'], [''], [true]])('%j se rechaza', (valor) => {
    let error
    try {
      validarMeta(valor)
    } catch (fallo) {
      error = fallo
    }

    expect(error).toBeInstanceOf(ErrorDeValidacion)
    expect([error.campo, error.mensaje]).toEqual(['meta', 'La meta va de 1 a 14 sesiones por semana.'])
  })
})

describe('rutinas hechas hoy (RF-004-10, plan 004 sección 4.5)', () => {
  it('son las de la lista si la lista es de hoy', () => {
    expect(rutinasHechasHoy({ fecha: '2026-11-10', rutinas: ['a', 'b'] }, '2026-11-10')).toEqual(['a', 'b'])
  })

  it('una lista de otro día no cuenta', () => {
    expect(rutinasHechasHoy({ fecha: '2026-11-09', rutinas: ['a'] }, '2026-11-10')).toEqual([])
  })

  it('sin lista no hay ninguna', () => {
    expect(rutinasHechasHoy(null, '2026-11-10')).toEqual([])
  })
})
