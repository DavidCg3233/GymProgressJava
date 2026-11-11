// Validaciones del cuerpo (spec 003, plan 003 sección 5). Espejo parcial de
// backend/reglas/cuerpo.py: el IMC y el objetivo los calcula el servidor.

import { ErrorDeValidacion } from './errores.js'

// RN-003-03.
export const PESO_MINIMO = 20
export const PESO_MAXIMO = 300

// RN-003-04: en centímetros.
export const ESTATURA_MINIMA = 100
export const ESTATURA_MAXIMA = 250

const MENSAJE_PESO = 'El peso va de 20 a 300 kg, con un decimal.'
const MENSAJE_ESTATURA = `La estatura va en centímetros, de ${ESTATURA_MINIMA} a ${ESTATURA_MAXIMA}.`
const MENSAJE_FECHA = 'Escribe una fecha válida.'

/** RN-003-03: de 20,0 a 300,0 kg, con un decimal como máximo. */
export function validarPesoCorporal(valor) {
  if (valor === null || valor === undefined || (typeof valor === 'string' && !valor.trim())) {
    throw new ErrorDeValidacion('peso', 'Escribe tu peso.')
  }
  if (typeof valor !== 'number' && typeof valor !== 'string') {
    throw new ErrorDeValidacion('peso', MENSAJE_PESO)
  }
  // Se mira el texto para contar decimales sin errores de coma flotante.
  const texto = String(valor).trim().replace(',', '.')
  if (!/^\d+(\.\d)?0*$/.test(texto)) {
    throw new ErrorDeValidacion('peso', MENSAJE_PESO)
  }
  const peso = Number(texto)
  if (peso < PESO_MINIMO || peso > PESO_MAXIMO) {
    throw new ErrorDeValidacion('peso', MENSAJE_PESO)
  }
  return peso
}

/** RN-003-04: entero de 100 a 250 cm. 1,75 se rechaza: va en centímetros. */
export function validarEstatura(valor) {
  if (!Number.isInteger(valor) || valor < ESTATURA_MINIMA || valor > ESTATURA_MAXIMA) {
    throw new ErrorDeValidacion('estatura', MENSAJE_ESTATURA)
  }
  return valor
}

/** RN-003-05: "AAAA-MM-DD", que exista en el calendario y no sea futura. */
export function validarFechaDePeso(valor, hoy) {
  if (typeof valor !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(valor)) {
    throw new ErrorDeValidacion('fecha', MENSAJE_FECHA)
  }
  const [anio, mes, dia] = valor.split('-').map(Number)
  const fecha = new Date(anio, mes - 1, dia)
  if (fecha.getFullYear() !== anio || fecha.getMonth() !== mes - 1 || fecha.getDate() !== dia) {
    throw new ErrorDeValidacion('fecha', MENSAJE_FECHA)
  }
  // Las fechas "AAAA-MM-DD" se comparan bien como texto.
  if (valor > hoy) {
    throw new ErrorDeValidacion('fecha', 'La fecha no puede ser futura.')
  }
  return valor
}
