// Reglas de una serie: peso y repeticiones (spec 006, RF-006-24).
//
// Estas reglas también existen en el servidor (backend/reglas/series.py), que
// es el único en el que se confía. Esta copia responde al instante y sin señal.

import { ErrorDeValidacion } from './errores.js'

// RN-006-02 y RN-006-03: de 0 a 500 kg en múltiplos de 0,5; 0 es peso corporal.
export const PESO_MINIMO = 0
export const PESO_MAXIMO = 500
export const PASO_DE_PESO = 0.5

// RN-006-04: entero de 1 a 100.
export const REPETICIONES_MINIMAS = 1
export const REPETICIONES_MAXIMAS = 100

const CAMPO_PESO = 'peso'
const CAMPO_REPS = 'reps'

/** Devuelve el peso como número, o explica por qué no es válido. */
export function validarPeso(valor) {
  if (estaVacio(valor)) {
    throw new ErrorDeValidacion(CAMPO_PESO, 'Escribe el peso.')
  }

  const peso = aNumero(valor)
  if (peso === null) {
    throw new ErrorDeValidacion(CAMPO_PESO, 'El peso debe ser un número.')
  }
  if (peso < PESO_MINIMO || peso > PESO_MAXIMO) {
    throw new ErrorDeValidacion(CAMPO_PESO, 'El peso debe estar entre 0 y 500 kg.')
  }
  if (!esMultiploDelPaso(peso)) {
    throw new ErrorDeValidacion(CAMPO_PESO, 'El peso va de a 0,5 kg.')
  }
  return peso
}

/** Devuelve las repeticiones como entero, o explica por qué no son válidas. */
export function validarRepeticiones(valor) {
  if (estaVacio(valor)) {
    throw new ErrorDeValidacion(CAMPO_REPS, 'Escribe las repeticiones.')
  }

  const cantidad = aNumero(valor)
  if (cantidad === null || !Number.isInteger(cantidad)) {
    throw new ErrorDeValidacion(CAMPO_REPS, 'Las repeticiones deben ser un número entero.')
  }
  if (cantidad < REPETICIONES_MINIMAS || cantidad > REPETICIONES_MAXIMAS) {
    throw new ErrorDeValidacion(CAMPO_REPS, 'Las repeticiones deben estar entre 1 y 100.')
  }
  return cantidad
}

function estaVacio(valor) {
  return valor === null || valor === undefined || (typeof valor === 'string' && valor.trim() === '')
}

/** Convierte a número. Devuelve null si no es un número finito. */
function aNumero(valor) {
  if (typeof valor === 'number') {
    return Number.isFinite(valor) ? valor : null
  }
  if (typeof valor !== 'string') {
    return null
  }
  // Number('30kg') da NaN, a diferencia de parseFloat, que devolvería 30.
  const numero = Number(valor.trim().replace(',', '.'))
  return Number.isFinite(numero) ? numero : null
}

/**
 * Un múltiplo de 0,5 multiplicado por 2 da un entero exacto. Así se evita el
 * operador de resto con decimales, que falla por la imprecisión de la coma flotante.
 */
function esMultiploDelPaso(peso) {
  return Number.isInteger(peso / PASO_DE_PESO)
}
