// Reglas de una rutina (spec 002, plan 002). Espejo de backend/reglas/rutinas.py.

import { claveDeEjercicio } from './ejercicios.js'
import { ErrorDeValidacion } from './errores.js'
import { exigirTexto } from './textos.js'

// RN-002-01.
export const LARGO_MAXIMO_NOMBRE_DE_RUTINA = 50

// RN-002-03.
export const MAXIMO_DE_EJERCICIOS = 20

// RN-002-04.
export const SERIES_PREVISTAS_MINIMAS = 1
export const SERIES_PREVISTAS_MAXIMAS = 10

// RN-002-02: 1 = lunes ... 7 = domingo.
export const DIAS_DE_LA_SEMANA = [1, 2, 3, 4, 5, 6, 7]
export const NOMBRES_DE_LOS_DIAS = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

const MENSAJE_DIAS = 'Los días van de lunes (1) a domingo (7), sin repetir.'

export function validarNombreDeRutina(valor) {
  const nombre = exigirTexto(valor, 'nombre').trim()
  if (!nombre) {
    throw new ErrorDeValidacion('nombre', 'Escribe el nombre de la rutina.')
  }
  if (nombre.length > LARGO_MAXIMO_NOMBRE_DE_RUTINA) {
    throw new ErrorDeValidacion('nombre', `El nombre de la rutina admite máximo ${LARGO_MAXIMO_NOMBRE_DE_RUTINA} caracteres.`)
  }
  return nombre
}

/** Devuelve los días ordenados. Una lista vacía es válida: la rutina no tiene día. */
export function validarDias(valor) {
  if (!Array.isArray(valor)) {
    throw new ErrorDeValidacion('dias', MENSAJE_DIAS)
  }
  const validos = valor.every((dia) => Number.isInteger(dia) && DIAS_DE_LA_SEMANA.includes(dia))
  if (!validos || new Set(valor).size !== valor.length) {
    throw new ErrorDeValidacion('dias', MENSAJE_DIAS)
  }
  return [...valor].sort((a, b) => a - b)
}

/** Cada día es un bit: lunes = 1, martes = 2, miércoles = 4 ... domingo = 64. */
export function diasABits(dias) {
  return dias.reduce((bits, dia) => bits | (1 << (dia - 1)), 0)
}

export function bitsADias(bits) {
  return DIAS_DE_LA_SEMANA.filter((dia) => tieneDia(bits, dia))
}

export function tieneDia(bits, dia) {
  return (bits & (1 << (dia - 1))) !== 0
}

/** Recibe las claves de los ejercicios de la rutina, en orden. */
export function validarEjerciciosDeRutina(claves) {
  if (claves.length === 0) {
    throw new ErrorDeValidacion('ejercicios', 'Agrega al menos un ejercicio.')
  }
  if (claves.length > MAXIMO_DE_EJERCICIOS) {
    throw new ErrorDeValidacion('ejercicios', `Una rutina admite máximo ${MAXIMO_DE_EJERCICIOS} ejercicios.`)
  }
  if (new Set(claves).size !== claves.length) {
    throw new ErrorDeValidacion('ejercicios', 'Un ejercicio aparece una sola vez por rutina.')
  }
}

export function validarSeriesPrevistas(valor) {
  if (!Number.isInteger(valor) || valor < SERIES_PREVISTAS_MINIMAS || valor > SERIES_PREVISTAS_MAXIMAS) {
    throw new ErrorDeValidacion('series', `Las series previstas van de ${SERIES_PREVISTAS_MINIMAS} a ${SERIES_PREVISTAS_MAXIMAS}.`)
  }
  return valor
}

/**
 * RF-002-21 y plan 002, sección 6: "Pecho (copia)", luego "(copia 2)", "(copia 3)"...
 * Se compara sin mayúsculas ni tildes. El original se recorta para no pasar de 50 caracteres.
 */
export function nombreDeCopia(original, existentes) {
  const ocupados = new Set(existentes.map(claveDeEjercicio))
  for (let numero = 1; ; numero += 1) {
    const sufijo = numero === 1 ? ' (copia)' : ` (copia ${numero})`
    const candidato = original.slice(0, LARGO_MAXIMO_NOMBRE_DE_RUTINA - sufijo.length).trimEnd() + sufijo
    if (!ocupados.has(claveDeEjercicio(candidato))) {
      return candidato
    }
  }
}
