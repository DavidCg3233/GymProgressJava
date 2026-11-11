// Reglas de la navegación (T-007-05 · RN-007-01, 02 · RF-007-01, 02, 03).

import { describe, expect, it } from 'vitest'

import { DESTINOS, destinoDe, muestraBarra } from './destinos.js'
import { tiempoDeSesion } from './tiempo.js'

describe('destinos de la barra (RN-007-01)', () => {
  it('son cuatro, siempre en este orden y con nombre escrito', () => {
    expect(DESTINOS.map((destino) => destino.nombre)).toEqual(['Inicio', 'Rutinas', 'Progreso', 'Historial'])
    expect(DESTINOS.map((destino) => destino.vista)).toEqual(['inicio', 'rutinas', 'progreso', 'historial'])
  })

  it.each([
    ['inicio', 'inicio'],
    ['contrasena', 'inicio'],
    ['rutinas', 'rutinas'],
    ['editor', 'rutinas'],
    ['catalogo', 'rutinas'],
    ['progreso', 'progreso'],
    ['historial', 'historial'],
  ])('la vista "%s" marca el destino "%s"', (vista, destino) => {
    expect(destinoDe(vista)).toBe(destino)
  })

  it('una vista desconocida marca el Inicio', () => {
    expect(destinoDe('otra')).toBe('inicio')
  })

  it('RF-007-02: la sesión en curso no muestra la barra; las demás sí', () => {
    expect(muestraBarra('sesion')).toBe(false)
    expect(['inicio', 'editor', 'progreso', 'historial', 'contrasena'].every(muestraBarra)).toBe(true)
  })
})

describe('tiempo de la sesión (RN-007-02)', () => {
  const inicio = new Date('2026-11-11T18:00:00-05:00')
  const despues = (minutos, segundos = 0) => new Date(inicio.getTime() + (minutos * 60 + segundos) * 1000)

  it.each([
    [0, 0, '0 min'],
    [0, 59, '0 min'],
    [35, 0, '35 min'],
    [59, 59, '59 min'],
    [60, 0, '1 h 00 min'],
    [65, 0, '1 h 05 min'],
    [119, 0, '1 h 59 min'],
    [125, 0, '2 h 05 min'],
  ])('a los %i min %i s dice "%s"', (minutos, segundos, texto) => {
    expect(tiempoDeSesion(inicio, despues(minutos, segundos))).toBe(texto)
  })

  it('acepta la hora de inicio como texto, como llega guardada', () => {
    expect(tiempoDeSesion(inicio.toISOString(), despues(35))).toBe('35 min')
  })

  it('si el reloj del celular va atrás, no muestra tiempo negativo', () => {
    expect(tiempoDeSesion(inicio, despues(-3))).toBe('0 min')
  })
})
