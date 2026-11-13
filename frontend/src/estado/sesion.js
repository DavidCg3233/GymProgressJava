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
import { ErrorDeValidacion } from '../reglas/errores.js'
import { fechaLocal, mejorSerie, supera } from '../reglas/progreso.js'
import { debeCerrarse } from '../reglas/sesiones.js'
import * as modelo from '../sesion/modelo.js'

const CLAVE_DEL_ESTADO = 'estado'

export const estado = reactive({
  cargando: true,
  sesion: null,
  ultimaVez: {},
  // Plan 002, 4.5: guardados en el celular para empezar una sesión de rutina sin señal.
  catalogo: { grupos: [], ejercicios: [] },
  rutinas: [],
  // Plan 004, 4.5: el inicio funciona sin señal (RNF-004-01).
  recientes: [], // RF-004-07: las 3 últimas sesiones terminadas
  hechasHoy: null, // RF-004-10: { fecha, rutinas }
  // Spec 008, 4.2: el récord de cada ejercicio, por su clave, para trabajar sin señal.
  records: {},
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
  return almacen.guardar(CLAVE_DEL_ESTADO, {
    sesion: estado.sesion,
    ultimaVez: estado.ultimaVez,
    catalogo: estado.catalogo,
    rutinas: estado.rutinas,
    recientes: estado.recientes,
    hechasHoy: estado.hechasHoy,
    records: estado.records,
  })
}

/** Lo usan las acciones de rutinas y catálogo para dejar sus cambios guardados en el celular. */
export const guardarEstadoLocal = guardarLocal

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
    estado.catalogo = guardado?.catalogo ?? { grupos: [], ejercicios: [] }
    estado.rutinas = guardado?.rutinas ?? []
    estado.recientes = guardado?.recientes ?? []
    estado.hechasHoy = guardado?.hechasHoy ?? null
    estado.records = guardado?.records ?? {}
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
  // El catálogo y las rutinas solo se editan con conexión: el servidor siempre manda.
  estado.catalogo = datos.catalogo ?? estado.catalogo
  estado.rutinas = datos.rutinas ?? estado.rutinas
  await guardarLocal()

  // Mientras queden cambios sin enviar, el celular sabe más que el servidor.
  if (estado.pendientes > 0) {
    return
  }
  estado.ultimaVez = datos.ultima_vez
  estado.recientes = datos.recientes ?? estado.recientes
  estado.hechasHoy = datos.hechas_hoy ?? estado.hechasHoy
  estado.records = datos.records ?? estado.records
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

function exigirSinSesionEnCurso() {
  // RF-006-02: una sola sesión en curso.
  if (estado.sesion) {
    throw new ErrorDeValidacion('sesion', 'Ya tienes una sesión en curso.')
  }
}

export function empezarSesionLibre() {
  exigirSinSesionEnCurso()
  estado.resumen = null
  estado.sesion = modelo.nuevaSesionLibre({ id: nuevoId(), ahora: new Date() })
  return registrar(operaciones.guardarSesion(estado.sesion))
}

/** RF-006-01 y plan 002, 4.5: empieza una sesión con la rutina guardada en el celular, con o sin señal. */
export function empezarSesionDesdeRutina(rutina) {
  // Como las demás acciones: la regla se aplica en el momento y lanza el error de inmediato.
  exigirSinSesionEnCurso()
  estado.resumen = null
  const sesion = modelo.nuevaSesionDesdeRutina({
    rutina,
    ahora: new Date(),
    ultimaVez: estado.ultimaVez,
    records: estado.records,
    nuevoId,
  })
  estado.sesion = sesion
  return registrarInicioDeRutina(sesion)
}

async function registrarInicioDeRutina(sesion) {
  // La sesión primero, luego sus ejercicios en orden. Las series viajan al confirmarse.
  const momento = new Date()
  await guardarLocal()
  await cola.agregar(operaciones.guardarSesion(sesion))
  for (const ejercicio of sesion.ejercicios) {
    await cola.agregar(operaciones.guardarEjercicio(sesion, ejercicio, momento))
  }
  await sincronizar()
}

export function agregarEjercicio(nombre, grupo) {
  const sesion = estado.sesion
  const ejercicio = modelo.agregarEjercicio(sesion, {
    id: nuevoId(),
    idSerie: nuevoId(),
    nombre,
    grupo,
    ultimaVez: estado.ultimaVez,
    records: estado.records,
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
  subirRecordSiSupera(ejercicio, serie)
  return registrar(operaciones.guardarSerie(ejercicio, serie, new Date()))
}

/**
 * RF-008-05: una serie que supera el récord lo reemplaza al instante, también sin
 * señal. Al volver la señal, el arranque trae el del servidor, que ya la incluye.
 */
function subirRecordSiSupera(ejercicio, serie) {
  const clave = claveDeEjercicio(ejercicio.nombre)
  const mejorDeAntes = mejorSerie(estado.ultimaVez[clave]?.series ?? [])
  const actual = estado.records[clave] ?? mejorDeAntes
  if (supera(serie, actual)) {
    estado.records = { ...estado.records, [clave]: { peso: serie.peso, reps: serie.reps } }
  }
}

/**
 * RF-008-08: quita la serie y numera las demás seguidas. Devuelve lo necesario
 * para deshacer (RF-008-09).
 *
 * El servidor no admite dos series con el mismo número, así que el orden importa:
 * primero se borra la quitada y luego bajan las de atrás, de la primera a la última.
 * Solo viajan las confirmadas: las pendientes viven solo en el celular.
 */
export async function quitarSerie(ejercicio, serie) {
  const quitada = modelo.quitarSerie(ejercicio, serie.id)
  if (!quitada) {
    return null
  }
  const momento = new Date()
  const envios = []
  if (quitada.serie.confirmada) {
    envios.push(operaciones.quitarSerie(quitada.serie, momento))
  }
  for (const renumerada of quitada.renumeradas.filter((otra) => otra.confirmada)) {
    envios.push(operaciones.guardarSerie(ejercicio, renumerada, momento))
  }
  await registrarEnOrden(envios)
  return quitada
}

/**
 * RF-008-09: devuelve la serie quitada a su lugar. Al revés que al quitar: primero
 * suben las de atrás, de la última a la primera, y al final vuelve la quitada.
 */
export async function deshacerQuitarSerie(ejercicio, quitada) {
  const renumeradas = modelo.restaurarSerie(ejercicio, quitada)
  const momento = new Date()
  const envios = renumeradas
    .filter((otra) => otra.confirmada)
    .sort((a, b) => b.numero - a.numero)
    .map((otra) => operaciones.guardarSerie(ejercicio, otra, momento))
  if (quitada.serie.confirmada) {
    envios.push(operaciones.guardarSerie(ejercicio, quitada.serie, momento))
  }
  await registrarEnOrden(envios)
}

async function registrarEnOrden(envios) {
  await guardarLocal()
  for (const envio of envios) {
    await cola.agregar(envio)
  }
  if (envios.length > 0) {
    await sincronizar()
  }
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
    incorporarAlInicio(sesion)
  }
  estado.sesion = null
  await registrar(operaciones.guardarSesion(sesion))
}

const SESIONES_RECIENTES = 3

/** Plan 004, 4.5: la sesión recién terminada se ve en el inicio sin esperar al servidor. */
function incorporarAlInicio(sesion) {
  const reciente = { id: sesion.id, nombre: sesion.nombre, inicio: sesion.inicio, rutina: sesion.rutina ?? null }
  estado.recientes = [reciente, ...estado.recientes.filter((otra) => otra.id !== sesion.id)].slice(0, SESIONES_RECIENTES)

  // Cuenta para el día en que empezó (RN-004-02), igual que en el servidor.
  const dia = fechaLocal(new Date(sesion.inicio))
  if (sesion.rutina && dia === fechaLocal(new Date())) {
    const deHoy = estado.hechasHoy?.fecha === dia ? estado.hechasHoy.rutinas : []
    estado.hechasHoy = { fecha: dia, rutinas: [...new Set([...deHoy, sesion.rutina])] }
  }
}

/** Al salir de la cuenta: nada de esta persona queda en el celular (RNF-ACC-04). */
export async function olvidarDatosLocales() {
  await cola.vaciar()
  await almacen.borrarTodo()
  Object.assign(estado, {
    sesion: null,
    ultimaVez: {},
    catalogo: { grupos: [], ejercicios: [] },
    rutinas: [],
    recientes: [],
    hechasHoy: null,
    records: {},
    resumen: null,
    pendientes: 0,
    sinConexion: false,
    aviso: '',
  })
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
