// La sesión de entrenamiento tal como vive en el celular (spec 006).
//
// Funciones puras sobre objetos simples: no tocan la red, la pantalla ni el
// almacenamiento. Quien las llama decide qué hacer con el resultado (mostrarlo,
// guardarlo, enviarlo). Por eso se pueden probar solas y funcionan sin conexión.
//
// Si una validación falla, lanzan ErrorDeValidacion ANTES de cambiar nada.

import {
  SERIES_MAXIMAS,
  claveDeEjercicio,
  validarGrupoMuscular,
  validarNombreDeEjercicio,
} from '../reglas/ejercicios.js'
import { ErrorDeValidacion } from '../reglas/errores.js'
import { valoresParaSerie } from '../reglas/precarga.js'
import { mejorSerie, referencia } from '../reglas/progreso.js'
import { validarPeso, validarRepeticiones } from '../reglas/series.js'
import { debeDescartarse, horaDeCierreAutomatico } from '../reglas/sesiones.js'
import { nombreDeSesionLibre, validarNota } from '../reglas/textos.js'
import { renumerar } from './series.js'

/** RF-006-20: una sesión sin rutina, a la que se le agregan ejercicios sobre la marcha. */
export function nuevaSesionLibre({ id, ahora }) {
  return { id, nombre: '', rutina: null, inicio: ahora.toISOString(), fin: null, nota: '', ejercicios: [] }
}

// --- Spec 008: el récord manda -------------------------------------------------

/**
 * RN-008-01: el récord del ejercicio. El que trae el celular (arranque) manda;
 * si no lo tiene (datos guardados antes de la spec 008), sale de la última vez.
 */
function recordDe(clave, records, ultimaVez) {
  if (records?.[clave]) {
    return records[clave]
  }
  const mejor = mejorSerie(ultimaVez?.[clave]?.series ?? [])
  return mejor ? { peso: mejor.peso, reps: mejor.reps } : null
}

/** RF-008-03: lo que hice en esa serie la última vez, como pista debajo del número. */
function pistaDe(clave, numero, ultimaVez) {
  const serie = ultimaVez?.[clave]?.series.find((anterior) => anterior.numero === numero)
  return serie ? { peso: serie.peso, reps: serie.reps } : null
}

/**
 * RF-006-01 y RF-008-03: una sesión que copia la rutina tal como está ahora (RF-002-13).
 *
 * Cada ejercicio trae tantas series como las previstas, precargadas con su
 * referencia: lo previsto, o el récord si lo supera (RN-008-03). La última vez de
 * cada serie queda como pista. Funciona sin señal: solo usa lo guardado en el celular.
 *
 * @param {Function} nuevoId Genera un identificador nuevo para cada ejercicio y serie.
 */
export function nuevaSesionDesdeRutina({ rutina, ahora, ultimaVez, records, nuevoId }) {
  const sesion = { ...nuevaSesionLibre({ id: nuevoId(), ahora }), nombre: rutina.nombre, rutina: rutina.id }

  sesion.ejercicios = rutina.ejercicios.map((previsto, indice) => {
    const clave = claveDeEjercicio(previsto.nombre)
    const anterior = ultimaVez?.[clave]
    const valores = referencia(previsto, recordDe(clave, records, ultimaVez))
    const series = []
    for (let numero = 1; numero <= previsto.series; numero += 1) {
      series.push({
        id: nuevoId(),
        numero,
        peso: valores.peso,
        reps: valores.reps,
        origen: valores.delRecord ? 'record' : 'rutina',
        pista: pistaDe(clave, numero, ultimaVez),
        confirmada: false,
      })
    }
    return {
      id: nuevoId(),
      nombre: anterior?.nombre ?? previsto.nombre,
      grupo: previsto.grupo,
      orden: indice + 1,
      nota: '',
      notaAnterior: anterior?.nota ?? '',
      series,
    }
  })
  return sesion
}

/** RF-006-13 y RF-008-04: el ejercicio entra con una serie, precargada con su récord si lo tiene. */
export function agregarEjercicio(sesion, { id, idSerie, nombre, grupo, ultimaVez, records }) {
  const nombreValido = validarNombreDeEjercicio(nombre)
  const grupoValido = validarGrupoMuscular(grupo)
  const clave = claveDeEjercicio(nombreValido)
  if (sesion.ejercicios.some((existente) => claveDeEjercicio(existente.nombre) === clave)) {
    throw new ErrorDeValidacion('nombre', 'Ese ejercicio ya está en la sesión.')
  }

  const ejercicio = {
    id,
    // Un ejercicio conocido conserva el nombre con que se registró, aunque hoy se escriba distinto.
    nombre: ultimaVez?.[clave]?.nombre ?? nombreValido,
    grupo: grupoValido,
    orden: sesion.ejercicios.length + 1,
    nota: '',
    // RF-006-23: lo que anoté la última vez, para verlo hoy.
    notaAnterior: ultimaVez?.[clave]?.nota ?? '',
    series: [],
  }
  const primera = agregarSerie(ejercicio, { id: idSerie, ultimaVez })
  const record = recordDe(clave, records, ultimaVez)
  if (record) {
    Object.assign(primera, { peso: record.peso, reps: record.reps, origen: 'record' })
  }
  sesion.ejercicios.push(ejercicio)
  return ejercicio
}

/** RF-006-12: agrega la serie siguiente, con los valores que le correspondan. */
export function agregarSerie(ejercicio, { id, ultimaVez }) {
  if (ejercicio.series.length >= SERIES_MAXIMAS) {
    throw new ErrorDeValidacion('numero', 'Un ejercicio admite entre 1 y 10 series.')
  }

  const anterior = ejercicio.series.at(-1) ?? null
  const numero = anterior ? anterior.numero + 1 : 1
  const precarga = valoresParaSerie({
    numero,
    historial: historialDesde(ultimaVez?.[claveDeEjercicio(ejercicio.nombre)]),
    serieAnterior: anterior && anterior.peso !== null ? anterior : null,
  })

  const serie = {
    id,
    numero,
    peso: precarga?.peso ?? null,
    reps: precarga?.reps ?? null,
    origen: precarga?.origen ?? null,
    pista: pistaDe(claveDeEjercicio(ejercicio.nombre), numero, ultimaVez),
    confirmada: false,
  }
  ejercicio.series.push(serie)
  return serie
}

/**
 * RF-008-08: quita una serie y numera las demás seguidas (RN-008-08).
 * Devuelve lo necesario para deshacer: la serie, su lugar y las que cambiaron
 * de número; o null si no estaba.
 */
export function quitarSerie(ejercicio, idSerie) {
  const indice = ejercicio.series.findIndex((serie) => serie.id === idSerie)
  if (indice === -1) {
    return null
  }
  const [serie] = ejercicio.series.splice(indice, 1)
  return { serie, indice, renumeradas: renumerar(ejercicio.series) }
}

/**
 * RF-008-09 y RN-008-09: devuelve una serie quitada a su lugar, con su número y
 * sus valores. Devuelve las demás series que cambiaron de número.
 */
export function restaurarSerie(ejercicio, { serie, indice }) {
  ejercicio.series.splice(Math.min(indice, ejercicio.series.length), 0, serie)
  return renumerar(ejercicio.series).filter((otra) => otra !== serie)
}

/** RF-006-03, 14 y 24: confirma (o corrige) una serie con valores válidos. */
export function confirmarSerie(serie, { peso, reps }) {
  const pesoValido = validarPeso(peso)
  const repsValidas = validarRepeticiones(reps)

  serie.peso = pesoValido
  serie.reps = repsValidas
  serie.confirmada = true
  return serie
}

/** RF-006-22 y 23: nota de la sesión o de un ejercicio. */
export function anotar(destino, nota) {
  destino.nota = validarNota(nota)
  return destino
}

/** RF-006-07, 19 y 21: termina la sesión. Devuelve si debe descartarse por no tener nada. */
export function terminarSesion(sesion, { ahora, nombre, nota }) {
  // Sin nombre escrito, una sesión de rutina conserva el de la rutina; una libre se llama "Sesión libre".
  const nombreValido = nombreDeSesionLibre(nombre?.trim() ? nombre : sesion.nombre)
  const notaValida = validarNota(nota)

  // RN-006-12: aunque se termine tarde, ninguna sesión dura más de 2 horas.
  const cierreMaximo = horaDeCierreAutomatico(new Date(sesion.inicio))
  const fin = ahora.getTime() > cierreMaximo.getTime() ? cierreMaximo : ahora

  sesion.nombre = nombreValido
  sesion.nota = notaValida
  sesion.fin = fin.toISOString()
  return { sesion, descartada: debeDescartarse(seriesConfirmadas(sesion)) }
}

export function seriesConfirmadas(sesion) {
  return sesion.ejercicios.reduce(
    (total, ejercicio) => total + ejercicio.series.filter((serie) => serie.confirmada).length,
    0,
  )
}

/**
 * El servidor ya entrega "la última vez" resuelta serie por serie. Se le da
 * la forma de historial que espera `valoresParaSerie`.
 */
function historialDesde(resumen) {
  if (!resumen) {
    return []
  }
  return [{ fin: 'ultima-vez', series: resumen.series.map((serie) => ({ ...serie, confirmada: true })) }]
}

/**
 * RN-006-08 y RN-006-16: incorpora una sesión terminada a "la última vez".
 *
 * Hace en el celular lo mismo que el servidor, para que la siguiente sesión
 * precargue lo de hoy aunque no haya habido señal para preguntarle.
 * Devuelve un objeto nuevo: no modifica el que recibe.
 */
export function incorporarAUltimaVez(ultimaVez, sesion) {
  // Copia en datos simples: structuredClone no sabe copiar los objetos reactivos de Vue.
  const nueva = JSON.parse(JSON.stringify(ultimaVez))

  for (const ejercicio of sesion.ejercicios) {
    const confirmadas = ejercicio.series.filter((serie) => serie.confirmada)
    if (confirmadas.length === 0) {
      continue
    }
    const clave = claveDeEjercicio(ejercicio.nombre)
    const porNumero = new Map((nueva[clave]?.series ?? []).map((serie) => [serie.numero, serie]))
    for (const serie of confirmadas) {
      porNumero.set(serie.numero, { numero: serie.numero, peso: serie.peso, reps: serie.reps })
    }
    nueva[clave] = {
      nombre: ejercicio.nombre,
      grupo: ejercicio.grupo,
      nota: ejercicio.nota,
      series: [...porNumero.values()].sort((a, b) => a.numero - b.numero),
    }
  }
  return nueva
}
