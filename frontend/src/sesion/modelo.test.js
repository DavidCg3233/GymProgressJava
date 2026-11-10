// La sesión de entrenamiento tal como vive en el celular.
// Spec 006. Funciones puras: reciben datos, devuelven datos. Sin red ni pantalla.

import { describe, expect, it } from 'vitest'

import { ErrorDeValidacion } from '../reglas/errores.js'
import {
  agregarEjercicio,
  agregarSerie,
  confirmarSerie,
  incorporarAUltimaVez,
  nuevaSesionLibre,
  quitarSerie,
  seriesConfirmadas,
  terminarSesion,
} from './modelo.js'

const AHORA = new Date('2026-11-09T18:00:00-05:00')
const despues = (minutos) => new Date(AHORA.getTime() + minutos * 60_000)

// Lo que el servidor entrega en /api/arranque/ para un ejercicio ya hecho (CA-006-04a).
const ULTIMA_VEZ = {
  'press inclinado': {
    nombre: 'Press inclinado',
    grupo: 'Pecho',
    nota: 'subir a 35',
    series: [
      { numero: 1, peso: 30, reps: 10 },
      { numero: 2, peso: 32.5, reps: 8 },
      { numero: 3, peso: 32.5, reps: 6 },
    ],
  },
}

let contador = 0
const id = () => `id-${++contador}`

function sesionConPress() {
  const sesion = nuevaSesionLibre({ id: id(), ahora: AHORA })
  const ejercicio = agregarEjercicio(sesion, { id: id(), idSerie: id(), nombre: 'Press inclinado', grupo: 'Pecho', ultimaVez: ULTIMA_VEZ })
  return { sesion, ejercicio }
}

describe('RF-006-20: empezar una sesión libre', () => {
  it('nace en curso, sin nombre y sin ejercicios', () => {
    const sesion = nuevaSesionLibre({ id: 'abc', ahora: AHORA })

    expect(sesion).toEqual({ id: 'abc', nombre: '', inicio: AHORA.toISOString(), fin: null, nota: '', ejercicios: [] })
  })
})

describe('RF-006-13: agregar un ejercicio', () => {
  it('RN-006-11: empieza con una serie pendiente', () => {
    const { ejercicio } = sesionConPress()

    expect(ejercicio.series).toHaveLength(1)
    expect(ejercicio.series[0].confirmada).toBe(false)
  })

  it('RN-006-11: si ya lo hice antes, la serie trae lo de la última vez', () => {
    const { ejercicio } = sesionConPress()

    expect(ejercicio.series[0]).toMatchObject({ numero: 1, peso: 30, reps: 10, origen: 'ultima-vez' })
  })

  it('RF-006-23: trae la nota que dejé la última vez', () => {
    const { ejercicio } = sesionConPress()

    expect(ejercicio.notaAnterior).toBe('subir a 35')
    expect(ejercicio.nota).toBe('')
  })

  it('reconoce el ejercicio aunque lo escriba con otras mayúsculas o tildes', () => {
    const sesion = nuevaSesionLibre({ id: id(), ahora: AHORA })

    const ejercicio = agregarEjercicio(sesion, { id: id(), idSerie: id(), nombre: ' PRESS inclinádo', grupo: 'Pecho', ultimaVez: ULTIMA_VEZ })

    expect(ejercicio.series[0].peso).toBe(30)
  })

  it('si ya lo conoce, usa el nombre con que lo registré antes, pero respeta el grupo que elijo', () => {
    const sesion = nuevaSesionLibre({ id: id(), ahora: AHORA })

    const ejercicio = agregarEjercicio(sesion, { id: id(), idSerie: id(), nombre: 'press INCLINADO', grupo: 'Hombro', ultimaVez: ULTIMA_VEZ })

    expect(ejercicio.nombre).toBe('Press inclinado')
    expect(ejercicio.grupo).toBe('Hombro')
  })

  it('si nunca lo he hecho, la serie viene vacía para que yo la llene', () => {
    const sesion = nuevaSesionLibre({ id: id(), ahora: AHORA })

    const ejercicio = agregarEjercicio(sesion, { id: id(), idSerie: id(), nombre: 'Dominadas', grupo: 'Espalda', ultimaVez: ULTIMA_VEZ })

    expect(ejercicio.series[0]).toMatchObject({ numero: 1, peso: null, reps: null, origen: null })
    expect(ejercicio.notaAnterior).toBe('')
  })

  it('los ejercicios quedan en el orden en que se agregan', () => {
    const { sesion } = sesionConPress()

    agregarEjercicio(sesion, { id: id(), idSerie: id(), nombre: 'Fondos', grupo: 'Pecho', ultimaVez: {} })

    expect(sesion.ejercicios.map((e) => [e.nombre, e.orden])).toEqual([['Press inclinado', 1], ['Fondos', 2]])
  })

  it('no acepta un ejercicio sin nombre o sin grupo', () => {
    const sesion = nuevaSesionLibre({ id: id(), ahora: AHORA })

    expect(() => agregarEjercicio(sesion, { id: id(), idSerie: id(), nombre: ' ', grupo: 'Pecho', ultimaVez: {} })).toThrow(ErrorDeValidacion)
    expect(() => agregarEjercicio(sesion, { id: id(), idSerie: id(), nombre: 'Fondos', grupo: '', ultimaVez: {} })).toThrow(ErrorDeValidacion)
    expect(sesion.ejercicios).toHaveLength(0)
  })

  it('no acepta dos veces el mismo ejercicio en la sesión', () => {
    const { sesion } = sesionConPress()

    expect(() => agregarEjercicio(sesion, { id: id(), idSerie: id(), nombre: 'press INCLINADO', grupo: 'Pecho', ultimaVez: {} })).toThrow(
      'Ese ejercicio ya está en la sesión.',
    )
  })
})

describe('RF-006-12: agregar y quitar series', () => {
  it('la serie siguiente trae lo de la última vez en ese número', () => {
    const { ejercicio } = sesionConPress()

    const segunda = agregarSerie(ejercicio, { id: id(), ultimaVez: ULTIMA_VEZ })

    expect(segunda).toMatchObject({ numero: 2, peso: 32.5, reps: 8, origen: 'ultima-vez', confirmada: false })
  })

  it('CA-006-12a: una serie sin antecedente copia la anterior de hoy', () => {
    const { ejercicio } = sesionConPress()
    agregarSerie(ejercicio, { id: id(), ultimaVez: ULTIMA_VEZ })
    const tercera = agregarSerie(ejercicio, { id: id(), ultimaVez: ULTIMA_VEZ })
    confirmarSerie(tercera, { peso: 32.5, reps: 6 })

    const cuarta = agregarSerie(ejercicio, { id: id(), ultimaVez: ULTIMA_VEZ })

    expect(cuarta).toMatchObject({ numero: 4, peso: 32.5, reps: 6, origen: 'serie-anterior' })
  })

  it('RN-006-05: no pasa de 10 series', () => {
    const { ejercicio } = sesionConPress()
    for (let i = 0; i < 9; i += 1) agregarSerie(ejercicio, { id: id(), ultimaVez: {} })

    expect(() => agregarSerie(ejercicio, { id: id(), ultimaVez: {} })).toThrow('Un ejercicio admite entre 1 y 10 series.')
    expect(ejercicio.series).toHaveLength(10)
  })

  it('quitar una serie la saca del ejercicio', () => {
    const { ejercicio } = sesionConPress()
    const segunda = agregarSerie(ejercicio, { id: id(), ultimaVez: ULTIMA_VEZ })

    quitarSerie(ejercicio, segunda.id)

    expect(ejercicio.series.map((s) => s.numero)).toEqual([1])
  })

  it('tras quitar la del medio, la siguiente que se agrega no repite número', () => {
    const { ejercicio } = sesionConPress()
    const segunda = agregarSerie(ejercicio, { id: id(), ultimaVez: {} })
    agregarSerie(ejercicio, { id: id(), ultimaVez: {} })
    quitarSerie(ejercicio, segunda.id)

    const nueva = agregarSerie(ejercicio, { id: id(), ultimaVez: {} })

    expect(ejercicio.series.map((s) => s.numero)).toEqual([1, 3, 4])
    expect(nueva.numero).toBe(4)
  })
})

describe('RF-006-03 y RF-006-24: confirmar una serie', () => {
  it('CA-006-03a: con los valores precargados queda confirmada', () => {
    const { ejercicio } = sesionConPress()
    const serie = ejercicio.series[0]

    confirmarSerie(serie, { peso: serie.peso, reps: serie.reps })

    expect(serie).toMatchObject({ peso: 30, reps: 10, confirmada: true })
  })

  it('CA-006-14a: se puede corregir una serie ya confirmada', () => {
    const { ejercicio } = sesionConPress()
    const serie = ejercicio.series[0]
    confirmarSerie(serie, { peso: 30, reps: 10 })

    confirmarSerie(serie, { peso: '32,5', reps: '10' })

    expect(serie).toMatchObject({ peso: 32.5, reps: 10, confirmada: true })
  })

  it.each([
    [{ peso: 500.5, reps: 1 }, 'El peso debe estar entre 0 y 500 kg.'],
    [{ peso: 30.3, reps: 10 }, 'El peso va de a 0,5 kg.'],
    [{ peso: '', reps: 10 }, 'Escribe el peso.'],
    [{ peso: 30, reps: 0 }, 'Las repeticiones deben estar entre 1 y 100.'],
    [{ peso: 30, reps: 8.5 }, 'Las repeticiones deben ser un número entero.'],
  ])('CA-006-24a: %j se rechaza y la serie queda como estaba', (valores, mensaje) => {
    const { ejercicio } = sesionConPress()
    const serie = ejercicio.series[0]

    expect(() => confirmarSerie(serie, valores)).toThrow(mensaje)
    expect(serie).toMatchObject({ peso: 30, reps: 10, confirmada: false })
  })
})

describe('RF-006-07, 19, 21, 22: terminar', () => {
  it('con series confirmadas queda terminada con su hora, nombre y nota', () => {
    const { sesion, ejercicio } = sesionConPress()
    confirmarSerie(ejercicio.series[0], { peso: 30, reps: 10 })

    const resultado = terminarSesion(sesion, { ahora: despues(50), nombre: ' Hotel Bogotá ', nota: 'dormí mal' })

    expect(resultado.descartada).toBe(false)
    expect(sesion).toMatchObject({ fin: despues(50).toISOString(), nombre: 'Hotel Bogotá', nota: 'dormí mal' })
  })

  it('CA-006-20a: sin nombre se llama "Sesión libre"', () => {
    const { sesion, ejercicio } = sesionConPress()
    confirmarSerie(ejercicio.series[0], { peso: 30, reps: 10 })

    terminarSesion(sesion, { ahora: despues(50), nombre: '', nota: '' })

    expect(sesion.nombre).toBe('Sesión libre')
  })

  it('CA-006-19a: sin series confirmadas se descarta', () => {
    const { sesion } = sesionConPress()

    expect(terminarSesion(sesion, { ahora: despues(50), nombre: '', nota: '' }).descartada).toBe(true)
  })

  it('RN-006-12: terminada tarde, el fin no pasa de inicio más 2 horas', () => {
    const { sesion, ejercicio } = sesionConPress()
    confirmarSerie(ejercicio.series[0], { peso: 30, reps: 10 })

    terminarSesion(sesion, { ahora: despues(300), nombre: '', nota: '' })

    expect(sesion.fin).toBe(despues(120).toISOString())
  })

  it('una nota demasiado larga impide terminar y la sesión sigue en curso', () => {
    const { sesion, ejercicio } = sesionConPress()
    confirmarSerie(ejercicio.series[0], { peso: 30, reps: 10 })

    expect(() => terminarSesion(sesion, { ahora: despues(50), nombre: '', nota: 'a'.repeat(281) })).toThrow(ErrorDeValidacion)
    expect(sesion.fin).toBeNull()
  })

  it('cuenta las series confirmadas de toda la sesión', () => {
    const { sesion, ejercicio } = sesionConPress()
    confirmarSerie(ejercicio.series[0], { peso: 30, reps: 10 })
    agregarSerie(ejercicio, { id: id(), ultimaVez: ULTIMA_VEZ })

    expect(seriesConfirmadas(sesion)).toBe(1)
  })
})

describe('RN-006-08: al terminar, lo de hoy pasa a ser "la última vez" (también sin conexión)', () => {
  function terminadaHoy() {
    const { sesion, ejercicio } = sesionConPress()
    confirmarSerie(ejercicio.series[0], { peso: 35, reps: 5 })
    agregarSerie(ejercicio, { id: id(), ultimaVez: ULTIMA_VEZ }) // serie 2 sin confirmar
    ejercicio.nota = 'bajar a 32,5'
    const fondos = agregarEjercicio(sesion, { id: id(), idSerie: id(), nombre: 'Fondos', grupo: 'Pecho', ultimaVez: {} })
    confirmarSerie(fondos.series[0], { peso: 0, reps: 12 })
    agregarEjercicio(sesion, { id: id(), idSerie: id(), nombre: 'Aperturas', grupo: 'Pecho', ultimaVez: {} }) // nada confirmado
    terminarSesion(sesion, { ahora: despues(50), nombre: '', nota: '' })
    return sesion
  }

  it('cada serie confirmada hoy reemplaza la de ese número; las demás se conservan', () => {
    const nueva = incorporarAUltimaVez(ULTIMA_VEZ, terminadaHoy())

    expect(nueva['press inclinado'].series).toEqual([
      { numero: 1, peso: 35, reps: 5 },
      { numero: 2, peso: 32.5, reps: 8 },
      { numero: 3, peso: 32.5, reps: 6 },
    ])
  })

  it('RN-006-16: la nota es la de hoy, aunque esté vacía', () => {
    const nueva = incorporarAUltimaVez(ULTIMA_VEZ, terminadaHoy())

    expect(nueva['press inclinado'].nota).toBe('bajar a 32,5')
  })

  it('un ejercicio nuevo entra; uno sin series confirmadas no', () => {
    const nueva = incorporarAUltimaVez(ULTIMA_VEZ, terminadaHoy())

    expect(nueva.fondos).toEqual({ nombre: 'Fondos', grupo: 'Pecho', nota: '', series: [{ numero: 1, peso: 0, reps: 12 }] })
    expect(nueva.aperturas).toBeUndefined()
  })

  it('no modifica la última vez original', () => {
    const copia = structuredClone(ULTIMA_VEZ)

    incorporarAUltimaVez(ULTIMA_VEZ, terminadaHoy())

    expect(ULTIMA_VEZ).toEqual(copia)
  })
})
