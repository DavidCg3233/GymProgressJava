// Reglas de un ejercicio dentro de una sesión (specs 006 y 002).
// Espejo de backend/reglas/ejercicios.py.

import { ErrorDeValidacion } from './errores.js'
import { exigirTexto } from './textos.js'

// RN-002-07 y RN-002-08.
export const LARGO_MAXIMO_NOMBRE_DE_EJERCICIO = 50
export const LARGO_MAXIMO_GRUPO = 30

// RN-006-05.
export const SERIES_MINIMAS = 1
export const SERIES_MAXIMAS = 10

const TILDE_DE_LA_ENIE = '̃'
const MARCAS_DE_ACENTO = /\p{M}/gu

export function validarNombreDeEjercicio(valor) {
  const nombre = exigirTexto(valor, 'nombre').trim()
  if (!nombre) {
    throw new ErrorDeValidacion('nombre', 'Escribe el nombre del ejercicio.')
  }
  if (nombre.length > LARGO_MAXIMO_NOMBRE_DE_EJERCICIO) {
    throw new ErrorDeValidacion('nombre', `El nombre del ejercicio admite máximo ${LARGO_MAXIMO_NOMBRE_DE_EJERCICIO} caracteres.`)
  }
  return nombre
}

export function validarGrupoMuscular(valor) {
  const grupo = exigirTexto(valor, 'grupo').trim()
  if (!grupo) {
    throw new ErrorDeValidacion('grupo', 'Elige el grupo muscular.')
  }
  if (grupo.length > LARGO_MAXIMO_GRUPO) {
    throw new ErrorDeValidacion('grupo', `El grupo muscular admite máximo ${LARGO_MAXIMO_GRUPO} caracteres.`)
  }
  return grupo
}

/**
 * Forma canónica del nombre, para reconocer el mismo ejercicio escrito de otra manera.
 * Ignora mayúsculas, tildes y espacios repetidos, pero conserva la ñ: en español es otra letra.
 */
export function claveDeEjercicio(nombre) {
  const sinTildes = nombre
    .toLowerCase()
    .normalize('NFD')
    .replace(MARCAS_DE_ACENTO, (marca) => (marca === TILDE_DE_LA_ENIE ? marca : ''))
    .normalize('NFC')
  return sinTildes.trim().split(/\s+/).join(' ')
}
