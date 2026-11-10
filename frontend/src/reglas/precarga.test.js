// Con qué valores aparece una serie antes de que el usuario la toque.
// Spec 006 · RF-006-04, RF-006-05 · RN-006-08, RN-006-10, RN-006-11.

import { describe, expect, it } from 'vitest'

import { valoresParaSerie } from './precarga.js'

const serie = (numero, peso, reps, confirmada = true) => ({ numero, peso, reps, confirmada })

// El lunes pasado, como en CA-006-04a.
const LUNES_PASADO = {
  fin: '2026-11-02T19:30:00-05:00',
  series: [serie(1, 30, 10), serie(2, 32.5, 8), serie(3, 32.5, 6)],
}

// Lo previsto en la rutina "Pecho" para "Press inclinado".
const PREVISTO = { series: 3, peso: 30, reps: 10 }

describe('RF-006-04: la serie viene con lo de la última vez', () => {
  it('CA-006-04a: cada serie trae lo que se registró en esa misma serie', () => {
    const historial = [LUNES_PASADO]

    expect(valoresParaSerie({ numero: 1, historial, previsto: PREVISTO })).toEqual({ peso: 30, reps: 10, origen: 'ultima-vez' })
    expect(valoresParaSerie({ numero: 2, historial, previsto: PREVISTO })).toEqual({ peso: 32.5, reps: 8, origen: 'ultima-vez' })
    expect(valoresParaSerie({ numero: 3, historial, previsto: PREVISTO })).toEqual({ peso: 32.5, reps: 6, origen: 'ultima-vez' })
  })

  it('RN-006-08: gana la sesión más reciente, sin importar el orden en que llegue el historial', () => {
    const haceDosSemanas = { fin: '2026-10-26T19:30:00-05:00', series: [serie(1, 27.5, 10)] }

    expect(valoresParaSerie({ numero: 1, historial: [haceDosSemanas, LUNES_PASADO] }).peso).toBe(30)
    expect(valoresParaSerie({ numero: 1, historial: [LUNES_PASADO, haceDosSemanas] }).peso).toBe(30)
  })

  it('RN-006-08: si la sesión más reciente no tiene esa serie, se busca en la anterior que sí la tenga', () => {
    const ayerSoloDosSeries = { fin: '2026-11-08T19:30:00-05:00', series: [serie(1, 35, 5), serie(2, 35, 4)] }
    const historial = [LUNES_PASADO, ayerSoloDosSeries]

    expect(valoresParaSerie({ numero: 2, historial })).toEqual({ peso: 35, reps: 4, origen: 'ultima-vez' })
    expect(valoresParaSerie({ numero: 3, historial })).toEqual({ peso: 32.5, reps: 6, origen: 'ultima-vez' })
  })

  it('RN-006-09: una serie que no se confirmó no cuenta como última vez', () => {
    const sinConfirmar = { fin: '2026-11-08T19:30:00-05:00', series: [serie(1, 40, 3, false)] }

    expect(valoresParaSerie({ numero: 1, historial: [LUNES_PASADO, sinConfirmar] }).peso).toBe(30)
  })

  it('una sesión que no ha terminado no cuenta como última vez', () => {
    const enCurso = { fin: null, series: [serie(1, 40, 3)] }

    expect(valoresParaSerie({ numero: 1, historial: [LUNES_PASADO, enCurso] }).peso).toBe(30)
  })
})

describe('RF-006-05: sin historial, la serie viene con lo previsto en la rutina', () => {
  it('CA-006-05a: nunca he registrado el ejercicio', () => {
    for (const numero of [1, 2, 3]) {
      expect(valoresParaSerie({ numero, historial: [], previsto: PREVISTO })).toEqual({ peso: 30, reps: 10, origen: 'rutina' })
    }
  })

  it('lo previsto solo cubre las series que la rutina tiene', () => {
    expect(valoresParaSerie({ numero: 4, historial: [], previsto: PREVISTO })).toBeNull()
  })
})

describe('RN-006-10: una serie agregada sin antecedente copia la serie anterior de hoy', () => {
  it('CA-006-12a: la cuarta serie viene con los valores de la tercera', () => {
    const serieAnterior = serie(3, 32.5, 6)

    expect(valoresParaSerie({ numero: 4, historial: [LUNES_PASADO], previsto: PREVISTO, serieAnterior })).toEqual({
      peso: 32.5,
      reps: 6,
      origen: 'serie-anterior',
    })
  })

  it('si la última vez sí hubo cuarta serie, manda la última vez', () => {
    const conCuatro = { fin: '2026-11-08T19:30:00-05:00', series: [serie(4, 25, 12)] }

    expect(valoresParaSerie({ numero: 4, historial: [conCuatro], serieAnterior: serie(3, 32.5, 6) })).toEqual({
      peso: 25,
      reps: 12,
      origen: 'ultima-vez',
    })
  })
})

describe('RN-006-11: ejercicio agregado en vivo', () => {
  it('si ya lo he hecho antes, su primera serie viene con la última vez', () => {
    expect(valoresParaSerie({ numero: 1, historial: [LUNES_PASADO] })).toEqual({ peso: 30, reps: 10, origen: 'ultima-vez' })
  })

  it('si nunca lo he hecho y no hay rutina, la serie viene vacía', () => {
    expect(valoresParaSerie({ numero: 1 })).toBeNull()
    expect(valoresParaSerie({ numero: 1, historial: [] })).toBeNull()
  })
})
