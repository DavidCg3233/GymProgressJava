// Reglas de progreso que el celular necesita sin señal (spec 004, plan 004 sección 5).
// Espejo parcial de backend/reglas/progreso.py: el resto lo calcula el servidor.

import { ErrorDeValidacion } from './errores.js'

// RN-004-08.
export const META_MINIMA = 1
export const META_MAXIMA = 14

const dosCifras = (numero) => String(numero).padStart(2, '0')

/** Día del calendario en el reloj del celular, como "2026-11-15". */
export function fechaLocal(momento) {
  return `${momento.getFullYear()}-${dosCifras(momento.getMonth() + 1)}-${dosCifras(momento.getDate())}`
}

/** RN-004-02: el lunes de la semana de `dia` ("AAAA-MM-DD"). */
export function inicioDeSemana(dia) {
  const [anio, mes, numero] = dia.split('-').map(Number)
  const fecha = new Date(anio, mes - 1, numero)
  const diasDesdeElLunes = (fecha.getDay() + 6) % 7
  fecha.setDate(fecha.getDate() - diasDesdeElLunes)
  return fechaLocal(fecha)
}

/** RN-004-08: una semana cumple si llegó a la meta. Sin meta no se juzga. */
export function cumple(sesiones, meta) {
  return meta === null ? null : sesiones >= meta
}

/** RN-004-08: entero de 1 a 14, o null para no tener meta. */
export function validarMeta(valor) {
  if (valor === null) {
    return null
  }
  if (!Number.isInteger(valor) || valor < META_MINIMA || valor > META_MAXIMA) {
    throw new ErrorDeValidacion('meta', `La meta va de ${META_MINIMA} a ${META_MAXIMA} sesiones por semana.`)
  }
  return valor
}

/** RF-004-10: ids de las rutinas hechas hoy. Una lista de otro día ya no vale (plan 004, 4.5). */
export function rutinasHechasHoy(hechas, hoy) {
  return hechas?.fecha === hoy ? hechas.rutinas : []
}
