// Acciones sobre rutinas y catálogo (spec 002).
//
// A diferencia de las sesiones, estas se hacen solo con conexión (RNF-002-01):
// cada acción le pide el cambio al servidor y, solo si lo acepta, lo refleja en
// el celular. Sin señal, el error llega a la pantalla y no se cambia nada.

import { ErrorDeApi, pedir } from '../datos/api.js'
import { estado, guardarEstadoLocal, sincronizar } from './sesion.js'

const nuevoId = () => crypto.randomUUID()
const porNombre = (a, b) => a.nombre.localeCompare(b.nombre, 'es')

function reemplazar(lista, objeto) {
  return [...lista.filter((existente) => existente.id !== objeto.id), objeto].sort(porNombre)
}

// --- Rutinas ----------------------------------------------------------------

/** Crea o reemplaza una rutina completa (RF-002-01, 05). */
export async function guardarRutina({ id = nuevoId(), nombre, dias, ejercicios }) {
  const { rutina } = await pedir('PUT', `/api/rutinas/${id}/`, { nombre, dias, ejercicios })
  estado.rutinas = reemplazar(estado.rutinas, rutina)
  await guardarEstadoLocal()
  return rutina
}

export async function eliminarRutina(id) {
  await pedir('DELETE', `/api/rutinas/${id}/`)
  estado.rutinas = estado.rutinas.filter((rutina) => rutina.id !== id)
  await guardarEstadoLocal()
}

export async function duplicarRutina(id) {
  const { rutina } = await pedir('POST', `/api/rutinas/${id}/duplicar/`, { id_copia: nuevoId() })
  estado.rutinas = reemplazar(estado.rutinas, rutina)
  await guardarEstadoLocal()
  return rutina
}

// --- Catálogo ---------------------------------------------------------------

export async function guardarGrupo({ id = nuevoId(), nombre }) {
  const { grupo } = await pedir('PUT', `/api/catalogo/grupos/${id}/`, { nombre })
  estado.catalogo = { ...estado.catalogo, grupos: reemplazar(estado.catalogo.grupos, grupo) }
  await guardarEstadoLocal()
  return grupo
}

export async function eliminarGrupo(id) {
  await pedir('DELETE', `/api/catalogo/grupos/${id}/`)
  estado.catalogo = { ...estado.catalogo, grupos: estado.catalogo.grupos.filter((grupo) => grupo.id !== id) }
  await guardarEstadoLocal()
}

/** Crea, renombra o cambia de grupo un ejercicio (RF-002-09, 15). */
export async function guardarEjercicio({ id, nombre, grupo }) {
  const existia = Boolean(id)
  const { ejercicio } = await pedir('PUT', `/api/catalogo/ejercicios/${id ?? nuevoId()}/`, { nombre, grupo })
  estado.catalogo = { ...estado.catalogo, ejercicios: reemplazar(estado.catalogo.ejercicios, ejercicio) }
  if (existia) {
    // Las rutinas muestran el nombre y el grupo del ejercicio: se traen de nuevo.
    await refrescarRutinas()
  }
  await guardarEstadoLocal()
  return ejercicio
}

/** RF-002-17 y 18: en qué rutinas está, y cuáles quedarían vacías. */
export async function usoDeEjercicio(id) {
  return (await pedir('GET', `/api/catalogo/ejercicios/${id}/uso/`)).rutinas
}

/** RF-002-16 y 18: lo quita del catálogo y de las rutinas; las que quedan vacías se van con él. */
export async function eliminarEjercicio(id) {
  const { rutinas_eliminadas: eliminadas } = await pedir('DELETE', `/api/catalogo/ejercicios/${id}/`)
  const idsEliminadas = new Set(eliminadas.map((rutina) => rutina.id))
  estado.rutinas = estado.rutinas
    .filter((rutina) => !idsEliminadas.has(rutina.id))
    .map((rutina) => ({ ...rutina, ejercicios: rutina.ejercicios.filter((previsto) => previsto.ejercicio !== id) }))
  estado.catalogo = { ...estado.catalogo, ejercicios: estado.catalogo.ejercicios.filter((e) => e.id !== id) }
  await guardarEstadoLocal()
  return eliminadas
}

async function refrescarRutinas() {
  const datos = await pedir('GET', '/api/rutinas/')
  if (datos?.rutinas) {
    estado.rutinas = datos.rutinas
  }
}

// --- Sesión → rutina (spec 008 · RF-008-06, 07) ---------------------------------

/**
 * Guarda una sesión terminada como rutina nueva o actualizando otra.
 * Con `confirmar: false` solo trae la vista previa de los cambios.
 *
 * La sesión tiene que estar en el servidor: primero se envía lo pendiente. Sin
 * señal se lanza el error de siempre (RNF-008-03) y no cambia nada.
 */
export async function sesionARutina(idSesion, datos) {
  await sincronizar()
  if (estado.pendientes > 0) {
    throw new ErrorDeApi(0, 'Sin conexión.')
  }
  const respuesta = await pedir('POST', `/api/sesiones/${idSesion}/a-rutina/`, datos)
  if (respuesta.rutina) {
    estado.rutinas = reemplazar(estado.rutinas, respuesta.rutina)
    // Un ejercicio que ya no estaba en el catálogo vuelve a él (plan 008, 4.5).
    estado.catalogo = await pedir('GET', '/api/catalogo/')
    await guardarEstadoLocal()
  }
  return respuesta
}
