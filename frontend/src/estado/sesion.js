// Estado de la sesión de entrenamiento en curso y las acciones del usuario sobre ella.
//
// Cada acción hace dos cosas, en este orden:
//   1. Cambia el estado en el celular (con las funciones puras de sesion/modelo.js),
//      así la pantalla responde al instante (RNF-REN-02).
//   2. Envía el cambio al servidor.
// Si el paso 1 falla por una regla, lanza ErrorDeValidacion y no se envía nada.

import { reactive } from 'vue'

import { pedir } from '../datos/api.js'
import * as operaciones from '../datos/operaciones.js'
import { claveDeEjercicio } from '../reglas/ejercicios.js'
import * as modelo from '../sesion/modelo.js'

export const estado = reactive({
  cargando: true,
  sesion: null,
  ultimaVez: {},
  // La sesión que se acaba de terminar, para mostrar su resumen en el inicio (RF-006-07).
  resumen: null,
  // Cambios hechos en el celular que el servidor aún no confirma (RF-006-18).
  pendientes: 0,
  aviso: '',
})

const nuevoId = () => crypto.randomUUID()

// Las peticiones salen de a una y en orden: el servidor debe conocer la sesión
// antes que sus ejercicios, y los ejercicios antes que sus series.
let enOrden = Promise.resolve()

function enviar(operacion) {
  estado.pendientes += 1
  enOrden = enOrden
    .then(() => pedir(operacion.metodo, operacion.url, operacion.cuerpo))
    .then(() => {
      estado.aviso = ''
    })
    .catch((error) => {
      estado.aviso = error.sinConexion
        ? 'Sin conexión: este cambio no se guardó en el servidor.'
        : error.mensaje
    })
    .finally(() => {
      estado.pendientes -= 1
    })
  return enOrden
}

export async function cargarArranque() {
  try {
    const datos = await pedir('GET', '/api/arranque/')
    estado.ultimaVez = datos.ultima_vez
    estado.sesion = datos.sesion_en_curso ? conNotasAnteriores(datos.sesion_en_curso, datos.ultima_vez) : null
  } finally {
    estado.cargando = false
  }
}

function conNotasAnteriores(sesion, ultimaVez) {
  for (const ejercicio of sesion.ejercicios) {
    ejercicio.notaAnterior = ultimaVez[claveDeEjercicio(ejercicio.nombre)]?.nota ?? ''
  }
  return sesion
}

export function empezarSesionLibre() {
  estado.resumen = null
  estado.sesion = modelo.nuevaSesionLibre({ id: nuevoId(), ahora: new Date() })
  return enviar(operaciones.guardarSesion(estado.sesion))
}

export function agregarEjercicio(nombre, grupo) {
  const sesion = estado.sesion
  const ejercicio = modelo.agregarEjercicio(sesion, {
    id: nuevoId(),
    idSerie: nuevoId(),
    nombre,
    grupo,
    ultimaVez: estado.ultimaVez,
  })
  return enviar(operaciones.guardarEjercicio(sesion, ejercicio, new Date()))
}

export function agregarSerie(ejercicio) {
  // No se envía todavía: una serie solo viaja al servidor cuando se confirma.
  modelo.agregarSerie(ejercicio, { id: nuevoId(), ultimaVez: estado.ultimaVez })
}

export function confirmarSerie(ejercicio, serie, valores) {
  modelo.confirmarSerie(serie, valores)
  return enviar(operaciones.guardarSerie(ejercicio, serie, new Date()))
}

export function quitarSerie(ejercicio, serie) {
  modelo.quitarSerie(ejercicio, serie.id)
  // Una serie que nunca se confirmó no existe en el servidor: no hay nada que quitar allá.
  return serie.confirmada ? enviar(operaciones.quitarSerie(serie, new Date())) : Promise.resolve()
}

export function anotarEjercicio(ejercicio, nota) {
  modelo.anotar(ejercicio, nota)
  return enviar(operaciones.guardarEjercicio(estado.sesion, ejercicio, new Date()))
}

/** Termina la sesión. Devuelve la sesión terminada, o null si se descartó por estar vacía. */
export async function terminarSesion(nombre, nota) {
  const sesion = estado.sesion
  const { descartada } = modelo.terminarSesion(sesion, { ahora: new Date(), nombre, nota })
  await enviar(operaciones.guardarSesion(sesion))
  // El resumen se guarda aquí y no se pasa como evento: al quitar la sesión,
  // la pantalla que la mostraba desaparece y un evento suyo ya no llegaría.
  estado.resumen = descartada ? null : sesion
  estado.sesion = null
  if (!descartada) {
    // Lo de hoy pasa a ser "la última vez" de la próxima sesión.
    await cargarArranque()
  }
  return descartada ? null : sesion
}

// --- Historial (solo lectura; requiere conexión) ----------------------------

export function cargarHistorial(pagina = 1) {
  return pedir('GET', `/api/sesiones/?pagina=${pagina}`)
}

export async function cargarSesion(id) {
  return (await pedir('GET', `/api/sesiones/${id}/`)).sesion
}

export async function eliminarSesion(id) {
  await pedir('DELETE', `/api/sesiones/${id}/`)
  await cargarArranque()
}
