// Reglas del ciclo de vida de una sesión de entrenamiento (spec 006).

// RN-006-06: una sesión en curso dura como máximo 2 horas desde su inicio.
export const DURACION_MAXIMA_MS = 2 * 60 * 60 * 1000

/** Momento en que una sesión olvidada se da por terminada (RN-006-12). */
export function horaDeCierreAutomatico(inicio) {
  exigirFechaValida(inicio)
  return new Date(inicio.getTime() + DURACION_MAXIMA_MS)
}

/** Indica si una sesión en curso ya cumplió su duración máxima (RF-006-08). */
export function debeCerrarse(inicio, ahora) {
  exigirFechaValida(ahora)
  return ahora.getTime() >= horaDeCierreAutomatico(inicio).getTime()
}

/** Una sesión que termina sin series confirmadas no se guarda (RF-006-19). */
export function debeDescartarse(seriesConfirmadas) {
  if (!Number.isInteger(seriesConfirmadas) || seriesConfirmadas < 0) {
    throw new RangeError('La cantidad de series confirmadas debe ser un entero no negativo.')
  }
  return seriesConfirmadas === 0
}

function exigirFechaValida(momento) {
  if (!(momento instanceof Date) || Number.isNaN(momento.getTime())) {
    throw new TypeError('Se esperaba una fecha válida.')
  }
}
