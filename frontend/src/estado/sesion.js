// Estado de la sesión de entrenamiento y las acciones del usuario sobre ella.
//
// El celular es la primera parada de todo cambio (RNF-006-05, RF-006-16):
//   1. La regla se aplica aquí, al instante (sesion/modelo.js). Si falla, lanza
//      ErrorDeValidacion de inmediato y no se guarda ni se envía nada.
//   2. El estado se guarda en el almacén del celular: sobrevive a cerrar la app.
//   3. El cambio entra a la cola de pendientes, que lo envía cuando haya señal.
// Así la pantalla nunca espera a la red, y sin señal no se pierde nada.

import { reactive } from 'vue'

import { crearAlmacen } from '../datos/almacen.js'
import { pedir } from '../datos/api.js'
import { crearCola } from '../datos/cola.js'
import * as operaciones from '../datos/operaciones.js'
import { claveDeEjercicio } from '../reglas/ejercicios.js'
import { debeCerrarse } from '../reglas/sesiones.js'
import * as modelo from '../sesion/modelo.js'

const CLAVE_DEL_ESTADO = 'estado'

export const estado = reactive({
  cargando: true,
  sesion: null,
  ultimaVez: {},
  // La sesión que se acaba de terminar, para mostrar su resumen en el inicio (RF-006-07).
  resumen: null,
  // RF-006-18: cambios guardados en el celular que el servidor aún no tiene.
  pendientes: 0,
  sinConexion: false,
  aviso: '',
})

const almacen = crearAlmacen()
const cola = crearCola({
  almacen,
  enviar: (operacion) => pedir(operacion.metodo, operacion.url, operacion.cuerpo),
  alCambiar: (cantidad) => {
    estado.pendientes = cantidad
  },
})

const nuevoId = () => crypto.randomUUID()

// --- Guardar y enviar -------------------------------------------------------

function guardarLocal() {
  return almacen.guardar(CLAVE_DEL_ESTADO, { sesion: estado.sesion, ultimaVez: estado.ultimaVez })
}

async function registrar(operacion) {
  await guardarLocal()
  await cola.agregar(operacion)
  await sincronizar()
}

/** Envía lo pendiente. Se llama tras cada cambio, al abrir la app y al volver la señal. */
export async function sincronizar() {
  const resultado = await cola.procesar()
  estado.sinConexion = resultado.detenida === 'sin-conexion'
  if (resultado.detenida === 'acceso') {
    estado.aviso = 'Tu acceso venció. Vuelve a entrar para enviar tus cambios; están guardados en el celular.'
  } else if (resultado.rechazos.length > 0) {
    estado.aviso = `El servidor no aceptó un cambio: ${resultado.rechazos[0].mensaje}`
  } else if (resultado.pendientes === 0) {
    estado.aviso = ''
  }
  return resultado
}

// --- Arrancar ---------------------------------------------------------------

/** RF-006-17: arranca con lo guardado en el celular y, si hay señal, se pone al día. */
export async function cargarArranque() {
  try {
    const guardado = await almacen.leer(CLAVE_DEL_ESTADO)
    estado.sesion = guardado?.sesion ?? null
    estado.ultimaVez = guardado?.ultimaVez ?? {}
    estado.pendientes = await cola.pendientes()

    await cerrarSiVencio()
    await sincronizar()
    await traerDelServidor()
  } finally {
    estado.cargando = false
  }
}

async function traerDelServidor() {
  let datos
  try {
    datos = await pedir('GET', '/api/arranque/')
  } catch (error) {
    if (error.sinConexion || error.estado >= 500) {
      estado.sinConexion = true
      return
    }
    throw error
  }
  estado.sinConexion = false

  // Mientras queden cambios sin enviar, el celular sabe más que el servidor.
  if (estado.pendientes > 0) {
    return
  }
  estado.ultimaVez = datos.ultima_vez
  // La sesión en curso del celular manda; la del servidor solo se adopta si aquí no hay ninguna.
  if (!estado.sesion && datos.sesion_en_curso) {
    estado.sesion = conNotasAnteriores(datos.sesion_en_curso, datos.ultima_vez)
  }
  await guardarLocal()
}

function conNotasAnteriores(sesion, ultimaVez) {
  for (const ejercicio of sesion.ejercicios) {
    ejercicio.notaAnterior = ultimaVez[claveDeEjercicio(ejercicio.nombre)]?.nota ?? ''
  }
  return sesion
}

/** RF-006-08: una sesión olvidada se termina sola, también sin conexión. */
async function cerrarSiVencio() {
  const sesion = estado.sesion
  if (!sesion || !debeCerrarse(new Date(sesion.inicio), new Date())) {
    return
  }
  const { descartada } = modelo.terminarSesion(sesion, { ahora: new Date(), nombre: sesion.nombre, nota: sesion.nota })
  await cerrar(sesion, descartada)
}

// --- Acciones del usuario ---------------------------------------------------
//
// Cada una valida y cambia el estado de forma inmediata (sincrónica): si algo no
// es válido, lanza el error en el momento. Luego devuelve una promesa que se
// resuelve cuando el cambio quedó guardado en el celular.

export function empezarSesionLibre() {
  estado.resumen = null
  estado.sesion = modelo.nuevaSesionLibre({ id: nuevoId(), ahora: new Date() })
  return registrar(operaciones.guardarSesion(estado.sesion))
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
  return registrar(operaciones.guardarEjercicio(sesion, ejercicio, new Date()))
}

export function agregarSerie(ejercicio) {
  // Una serie solo viaja al servidor cuando se confirma; aquí basta con recordarla.
  modelo.agregarSerie(ejercicio, { id: nuevoId(), ultimaVez: estado.ultimaVez })
  return guardarLocal()
}

export function confirmarSerie(ejercicio, serie, valores) {
  modelo.confirmarSerie(serie, valores)
  return registrar(operaciones.guardarSerie(ejercicio, serie, new Date()))
}

export function quitarSerie(ejercicio, serie) {
  modelo.quitarSerie(ejercicio, serie.id)
  // Una serie que nunca se confirmó no existe en el servidor: no hay nada que quitar allá.
  return serie.confirmada ? registrar(operaciones.quitarSerie(serie, new Date())) : guardarLocal()
}

export function anotarEjercicio(ejercicio, nota) {
  modelo.anotar(ejercicio, nota)
  return registrar(operaciones.guardarEjercicio(estado.sesion, ejercicio, new Date()))
}

/** Termina la sesión. Devuelve la sesión terminada, o null si se descartó por estar vacía. */
export async function terminarSesion(nombre, nota) {
  const sesion = estado.sesion
  const { descartada } = modelo.terminarSesion(sesion, { ahora: new Date(), nombre, nota })
  await cerrar(sesion, descartada)
  // El resumen se guarda en el estado y no se pasa como evento: al quitar la sesión,
  // la pantalla que la mostraba desaparece y un evento suyo ya no llegaría.
  estado.resumen = descartada ? null : sesion
  return estado.resumen
}

async function cerrar(sesion, descartada) {
  if (!descartada) {
    // Lo de hoy pasa a ser "la última vez" ya mismo, aunque no haya señal.
    estado.ultimaVez = modelo.incorporarAUltimaVez(estado.ultimaVez, sesion)
  }
  estado.sesion = null
  await registrar(operaciones.guardarSesion(sesion))
}

/** Al salir de la cuenta: nada de esta persona queda en el celular (RNF-ACC-04). */
export async function olvidarDatosLocales() {
  await cola.vaciar()
  await almacen.borrarTodo()
  Object.assign(estado, { sesion: null, ultimaVez: {}, resumen: null, pendientes: 0, sinConexion: false, aviso: '' })
}

/** Reintenta enviar al volver la señal, al volver a la app y cada 10 segundos si queda algo (RNF-006-07). */
export function iniciarSincronizacion() {
  const reintentar = () => {
    if (estado.pendientes > 0) {
      sincronizar()
    }
  }
  window.addEventListener('online', reintentar)
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') reintentar()
  })
  setInterval(reintentar, 10_000)
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
  await traerDelServidor()
}
