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
