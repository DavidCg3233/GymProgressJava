// Peso corporal (spec 003, plan 003 sección 4.2).
//
// Todo pide conexión (RNF-003-02): cada acción le pide el cambio al servidor.
// Antes de enviar, se valida aquí para avisar al instante; si no hay señal,
// la pantalla conserva lo escrito.

import { pedir } from '../datos/api.js'
import { validarEstatura, validarFechaDePeso, validarPesoCorporal } from '../reglas/cuerpo.js'
import { fechaLocal } from '../reglas/progreso.js'

export const cargarPeso = () => pedir('GET', '/api/peso/')

/**
 * RF-003-01, 02 y 10. Devuelve `{ registro }` si se guardó, o `{ confirmar: mensaje }`
 * si ya había un peso ese día y falta que el usuario acepte reemplazarlo.
 */
export async function registrarPeso({ fecha, peso, reemplazar = false }) {
  const dia = validarFechaDePeso(fecha, fechaLocal(new Date()))
  const valor = validarPesoCorporal(peso)
  try {
    return await pedir('PUT', `/api/peso/${dia}/`, { peso: valor, reemplazar })
  } catch (fallo) {
    if (fallo.estado === 409) {
      return { confirmar: fallo.mensaje }
    }
    throw fallo
  }
}

/** RF-003-11. La confirmación la pide la pantalla antes. */
export const eliminarPeso = (fecha) => pedir('DELETE', `/api/peso/${fecha}/`)

/** RF-003-12. */
export async function fijarEstatura(estatura) {
  return (await pedir('PUT', '/api/peso/estatura/', { estatura: validarEstatura(estatura) })).estatura
}

/** RF-003-08. `null` quita el objetivo. */
export async function fijarObjetivo(objetivo) {
  const valor = objetivo === null ? null : validarPesoCorporal(objetivo)
  return (await pedir('PUT', '/api/peso/objetivo/', { objetivo: valor })).objetivo
}

/** RNF-003-02: sin señal (o con el servidor caído) se dice, y lo escrito se queda. */
export function mensajeDePeso(fallo) {
  return fallo.sinConexion || fallo.estado >= 500
    ? 'Para guardar tu peso necesitas conexión. Lo que escribiste sigue aquí.'
    : fallo.mensaje
}
