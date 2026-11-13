// Numeración de series y sugerencias de ejercicios (T-008-03 · RN-008-08, 10).

import { describe, expect, it } from 'vitest'

import { renumerar, sugerencias } from './series.js'

describe('renumerar (RN-008-08)', () => {
  it('CA-008-08a: al quitar la 2 de 1, 2, 3, la vieja 3 pasa a ser la 2', () => {
    const series = [
      { id: 'a', numero: 1 },
      { id: 'c', numero: 3 },
    ]

    const cambiadas = renumerar(series)

    expect(series.map((s) => [s.id, s.numero])).toEqual([
      ['a', 1],
      ['c', 2],
    ])
    expect(cambiadas.map((s) => s.id)).toEqual(['c'])
  })

  it('sin huecos no cambia nada', () => {
    const series = [
      { id: 'a', numero: 1 },
      { id: 'b', numero: 2 },
    ]

    expect(renumerar(series)).toEqual([])
  })

  it('conserva el orden y los demás datos', () => {
    const series = [
      { id: 'b', numero: 2, peso: 30, confirmada: true },
      { id: 'd', numero: 4, peso: 35, confirmada: false },
    ]

    renumerar(series)

    expect(series).toEqual([
      { id: 'b', numero: 1, peso: 30, confirmada: true },
      { id: 'd', numero: 2, peso: 35, confirmada: false },
    ])
  })
})

describe('sugerencias de ejercicios (RN-008-10)', () => {
  const catalogo = [
    'Aperturas con mancuernas',
    'Curl con barra',
    'Peso muerto',
    'Peso muerto rumano',
    'Press Arnold',
    'Press con mancuernas',
    'Press de banca',
    'Press declinado',
    'Press francés',
    'Press inclinado',
    'Press militar',
    'Pájaros',
    'Remo con barra',
  ].map((nombre) => ({ nombre, grupo: 'Grupo' }))

  const nombres = (lista) => lista.map((e) => e.nombre)

  it('CA-008-10a: "pr" sugiere primero los que empiezan por "pr", máximo 6', () => {
    const lista = sugerencias(catalogo, 'pr')

    expect(lista).toHaveLength(6)
    expect(lista.every((e) => e.nombre.startsWith('Press'))).toBe(true)
  })

  it('primero los que empiezan, luego los que contienen', () => {
    expect(nombres(sugerencias(catalogo, 'barra'))).toEqual(['Curl con barra', 'Remo con barra'])
    expect(nombres(sugerencias(catalogo, 'muerto'))).toEqual(['Peso muerto', 'Peso muerto rumano'])
    expect(nombres(sugerencias(catalogo, 'peso'))).toEqual(['Peso muerto', 'Peso muerto rumano'])
  })

  it('no distingue tildes ni mayúsculas', () => {
    expect(nombres(sugerencias(catalogo, 'pajaro'))).toEqual(['Pájaros'])
    expect(nombres(sugerencias(catalogo, 'PRESS FRANC'))).toEqual(['Press francés'])
  })

  it('sin texto o sin coincidencias, nada', () => {
    expect(sugerencias(catalogo, '')).toEqual([])
    expect(sugerencias(catalogo, '   ')).toEqual([])
    expect(sugerencias(catalogo, 'zancadas')).toEqual([])
  })

  it('el nombre ya escrito completo no se sugiere a sí mismo', () => {
    expect(nombres(sugerencias(catalogo, 'Peso muerto'))).toEqual(['Peso muerto rumano'])
  })
})
