// Con qué valores aparece una serie antes de que el usuario la toque (spec 006).

/**
 * Decide el peso y las repeticiones con que se presenta una serie.
 *
 * Orden de preferencia:
 *  1. Lo registrado en esa misma serie la última vez (RF-006-04, RN-006-08).
 *  2. Lo previsto en la rutina, si la rutina tiene esa serie (RF-006-05).
 *  3. La serie anterior de la sesión de hoy, para una serie agregada (RN-006-10).
 *  4. Nada: el usuario la llena (ejercicio nuevo, sin rutina).
 *
 * @param {object} datos
 * @param {number} datos.numero                Número de la serie dentro del ejercicio (desde 1).
 * @param {Array}  [datos.historial]           Sesiones en las que se hizo el ejercicio: { fin, series }.
 * @param {object} [datos.previsto]            Lo previsto en la rutina: { series, peso, reps }.
 * @param {object} [datos.serieAnterior]       La serie anterior de la sesión de hoy: { peso, reps }.
 * @returns {{peso: number, reps: number, origen: string} | null}
 */
export function valoresParaSerie({ numero, historial = [], previsto = null, serieAnterior = null }) {
  const ultimaVez = buscarUltimaVez(numero, historial)
  if (ultimaVez) {
    return { peso: ultimaVez.peso, reps: ultimaVez.reps, origen: 'ultima-vez' }
  }
  if (previsto && numero <= previsto.series) {
    return { peso: previsto.peso, reps: previsto.reps, origen: 'rutina' }
  }
  if (serieAnterior) {
    return { peso: serieAnterior.peso, reps: serieAnterior.reps, origen: 'serie-anterior' }
  }
  return null
}

/** La serie confirmada con ese número en la sesión terminada más reciente que la tenga. */
function buscarUltimaVez(numero, historial) {
  const terminadasDeRecienteAAntigua = historial
    .filter((sesion) => sesion.fin)
    .sort((a, b) => new Date(b.fin).getTime() - new Date(a.fin).getTime())

  for (const sesion of terminadasDeRecienteAAntigua) {
    const serie = sesion.series.find((candidata) => candidata.numero === numero && candidata.confirmada)
    if (serie) {
      return serie
    }
  }
  return null
}
