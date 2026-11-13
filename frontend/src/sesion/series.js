// Numeración de series y sugerencias de ejercicios (spec 008 · plan 008, sección 4.1).

import { claveDeEjercicio } from '../reglas/ejercicios.js'

/**
 * RN-008-08: numera las series 1, 2, 3… en el orden en que están, sin huecos.
 * Cambia las series que recibe y devuelve las que cambiaron de número.
 */
export function renumerar(series) {
  const cambiadas = []
  series.forEach((serie, indice) => {
    if (serie.numero !== indice + 1) {
      serie.numero = indice + 1
      cambiadas.push(serie)
    }
  })
  return cambiadas
}

export const MAXIMO_DE_SUGERENCIAS = 6

/**
 * RN-008-10: ejercicios del catálogo que coinciden con lo escrito, sin importar
 * mayúsculas ni tildes. Primero los que empiezan por el texto, luego los que lo
 * contienen; máximo 6. El nombre ya escrito completo no se sugiere a sí mismo.
 */
export function sugerencias(catalogo, texto) {
  const buscado = claveDeEjercicio(texto ?? '')
  if (!buscado) {
    return []
  }
  const conClave = catalogo
    .map((ejercicio) => ({ ejercicio, clave: claveDeEjercicio(ejercicio.nombre) }))
    .filter(({ clave }) => clave !== buscado && clave.includes(buscado))
  const empiezan = conClave.filter(({ clave }) => clave.startsWith(buscado))
  const contienen = conClave.filter(({ clave }) => !clave.startsWith(buscado))
  return [...empiezan, ...contienen].slice(0, MAXIMO_DE_SUGERENCIAS).map(({ ejercicio }) => ejercicio)
}
