// Progreso: lo calcula el servidor y necesita conexión (RNF-004-02, plan 004 sección 4.4).

import { pedir } from '../datos/api.js'
import { validarMeta } from '../reglas/progreso.js'

export const cargarProgreso = () => pedir('GET', '/api/progreso/')

export const cargarEvolucion = (clave) => pedir('GET', `/api/progreso/evolucion/?clave=${encodeURIComponent(clave)}`)

/** RF-004-11: fija, cambia o quita (null) la meta. Valida antes de esperar a la red. */
export async function fijarMeta(meta) {
  const respuesta = await pedir('PUT', '/api/progreso/meta/', { meta: validarMeta(meta) })
  return respuesta.meta
}

/**
 * RNF-004-02: Progreso necesita conexión y lo dice. Un servidor que no responde
 * (5xx, también el del proxy) se trata igual que no tener red, como en el arranque.
 */
export function mensajeDeProgreso(fallo) {
  return fallo.sinConexion || fallo.estado >= 500
    ? 'Progreso necesita conexión. Revisa tu señal y vuelve a intentar.'
    : fallo.mensaje
}
