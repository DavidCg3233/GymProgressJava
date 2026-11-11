// Progreso necesita conexión y lo dice (T-004-13 · RNF-004-02).

import { describe, expect, it } from 'vitest'

import { ErrorDeApi } from '../datos/api.js'
import { mensajeDeProgreso } from './progreso.js'

const SIN_CONEXION = 'Progreso necesita conexión. Revisa tu señal y vuelve a intentar.'

describe('mensaje cuando Progreso no carga', () => {
  it('sin red, pide conexión', () => {
    expect(mensajeDeProgreso(new ErrorDeApi(0, 'Sin conexión.'))).toBe(SIN_CONEXION)
  })

  it.each([[500], [502], [503]])('con el servidor caído (%i), también pide conexión', (estado) => {
    expect(mensajeDeProgreso(new ErrorDeApi(estado, 'Algo salió mal.'))).toBe(SIN_CONEXION)
  })

  it('un error del usuario conserva su mensaje', () => {
    expect(mensajeDeProgreso(new ErrorDeApi(400, 'La meta va de 1 a 14 sesiones por semana.'))).toBe(
      'La meta va de 1 a 14 sesiones por semana.',
    )
  })
})
