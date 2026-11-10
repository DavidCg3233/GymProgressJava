// Reglas de los textos de una sesión: notas y nombre (spec 006).

import { ErrorDeValidacion } from './errores.js'

// RN-006-14: notas de sesión y de ejercicio, opcionales.
export const LARGO_MAXIMO_NOTA = 280

// RN-006-15 y RF-006-21: nombre de una sesión libre.
export const LARGO_MAXIMO_NOMBRE = 50
export const NOMBRE_SESION_LIBRE = 'Sesión libre'

/** Devuelve la nota sin espacios sobrantes. Vacía es válida: la nota es opcional. */
export function validarNota(valor) {
  const nota = limpiar(valor, 'nota')
  if (nota.length > LARGO_MAXIMO_NOTA) {
    throw new ErrorDeValidacion('nota', `La nota admite máximo ${LARGO_MAXIMO_NOTA} caracteres.`)
  }
  return nota
}

/** Devuelve el nombre que escribió el usuario, o el nombre por defecto si lo dejó vacío. */
export function nombreDeSesionLibre(valor) {
  const nombre = limpiar(valor, 'nombre')
  if (nombre.length > LARGO_MAXIMO_NOMBRE) {
    throw new ErrorDeValidacion('nombre', `El nombre admite máximo ${LARGO_MAXIMO_NOMBRE} caracteres.`)
  }
  return nombre || NOMBRE_SESION_LIBRE
}

function limpiar(valor, campo) {
  return exigirTexto(valor, campo).trim()
}

/** Acepta un texto o nada. Cualquier otro tipo es un dato mal formado. */
export function exigirTexto(valor, campo) {
  if (valor === null || valor === undefined) {
    return ''
  }
  if (typeof valor !== 'string') {
    throw new ErrorDeValidacion(campo, 'Escribe un texto válido.')
  }
  return valor
}
