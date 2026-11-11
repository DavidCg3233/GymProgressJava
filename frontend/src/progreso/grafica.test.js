// Escalas de la gráfica de evolución (T-004-14 · RF-004-09 · plan 004, sección 6).

import { describe, expect, it } from 'vitest'

import { puntosDeLaGrafica } from './grafica.js'

const AREA = { ancho: 300, alto: 160, margen: 20 }

describe('puntos de la gráfica', () => {
  it('sin valores no hay puntos', () => {
    expect(puntosDeLaGrafica([], AREA).puntos).toEqual([])
  })

  it('un solo punto queda en el centro', () => {
    const { puntos } = puntosDeLaGrafica([35], AREA)

    expect(puntos).toEqual([{ x: 150, y: 80 }])
  })

  it('valores iguales forman una línea plana en el medio', () => {
    const { puntos } = puntosDeLaGrafica([35, 35, 35], AREA)

    expect(puntos.map((p) => p.y)).toEqual([80, 80, 80])
    expect(puntos.map((p) => p.x)).toEqual([20, 150, 280])
  })

  it('el mayor queda arriba y el menor abajo, dentro del margen', () => {
    const { puntos, minimo, maximo } = puntosDeLaGrafica([30, 35, 32.5], AREA)

    expect([minimo, maximo]).toEqual([30, 35])
    expect(puntos[1].y).toBe(20) // 35 arriba
    expect(puntos[0].y).toBe(140) // 30 abajo
    expect(puntos[2].y).toBe(80)
  })

  it('valores grandes no se salen del área', () => {
    const { puntos } = puntosDeLaGrafica([755, 12000, 3000], AREA)

    for (const { x, y } of puntos) {
      expect(x).toBeGreaterThanOrEqual(20)
      expect(x).toBeLessThanOrEqual(280)
      expect(y).toBeGreaterThanOrEqual(20)
      expect(y).toBeLessThanOrEqual(140)
    }
  })
})
