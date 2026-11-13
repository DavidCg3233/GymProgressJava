// Reglas de progreso que usa el celular (T-004-02).
// Espejo de backend/tests/reglas/test_progreso.py en lo que aplica: mismos casos, mismos mensajes.

import { describe, expect, it } from 'vitest'

import { ErrorDeValidacion } from './errores.js'
import { cumple, fechaLocal, inicioDeSemana, mejorSerie, referencia, rutinasHechasHoy, supera, validarMeta } from './progreso.js'

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

// --- Spec 008 (T-008-01): "supera", mejor serie y referencia -----------------
// La tabla de "supera" es la de backend/tests/reglas/test_progreso.py.

describe('supera (RN-008-02)', () => {
  const s = (peso, reps) => ({ peso, reps })

  it.each([
    [s(2, 18), s(1, 20), true],
    [s(10, 20), s(10, 18), true],
    [s(10, 18), s(10, 20), false],
    [s(10, 18), s(10, 18), false],
    [s(80, 2), s(70, 10), true],
    [s(0, 12), s(0, 10), true],
    [s(32.5, 6), s(30, 12), true],
  ])('%j supera a %j: %s', (nueva, anterior, esperado) => {
    expect(supera(nueva, anterior)).toBe(esperado)
  })

  it('cualquier serie supera a no tener récord', () => {
    expect(supera(s(20, 5), null)).toBe(true)
    expect(supera(s(20, 5), undefined)).toBe(true)
  })
})

describe('mejor serie (RN-004-03, RN-008-01)', () => {
  it('CA-004-04a: mayor peso, luego más reps, y en empate la primera', () => {
    const series = [
      { peso: 32.5, reps: 8, id: 'a' },
      { peso: 35, reps: 5, id: 'b' },
      { peso: 35, reps: 6, id: 'c' },
      { peso: 35, reps: 6, id: 'd' },
      { peso: 30, reps: 15, id: 'e' },
    ]

    expect(mejorSerie(series).id).toBe('c')
  })

  it('sin series no hay mejor serie', () => {
    expect(mejorSerie([])).toBeNull()
  })
})

describe('referencia de un ejercicio en una rutina (RN-008-03)', () => {
  it('CA-008-02a: el récord 10 × 20 supera lo previsto 10 × 18', () => {
    expect(referencia({ peso: 10, reps: 18 }, { peso: 10, reps: 20 })).toEqual({ peso: 10, reps: 20, delRecord: true })
  })

  it('CA-008-02b: el peso manda, 2 × 18 sobre 1 × 20 previsto', () => {
    expect(referencia({ peso: 1, reps: 20 }, { peso: 2, reps: 18 })).toEqual({ peso: 2, reps: 18, delRecord: true })
  })

  it('CA-008-02c: un récord que no supera deja lo previsto', () => {
    expect(referencia({ peso: 12, reps: 10 }, { peso: 10, reps: 20 })).toEqual({ peso: 12, reps: 10, delRecord: false })
  })

  it('sin récord, lo previsto', () => {
    expect(referencia({ peso: 30, reps: 10 }, null)).toEqual({ peso: 30, reps: 10, delRecord: false })
  })
})
