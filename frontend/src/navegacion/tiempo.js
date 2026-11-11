// Tiempo de la sesión en la franja (spec 007 · RN-007-02).

const MINUTO = 60_000

/** "35 min" o, desde la primera hora, "1 h 05 min". Nunca negativo. */
export function tiempoDeSesion(inicio, ahora) {
  const minutos = Math.max(0, Math.floor((ahora.getTime() - new Date(inicio).getTime()) / MINUTO))
  if (minutos < 60) {
    return `${minutos} min`
  }
  const horas = Math.floor(minutos / 60)
  return `${horas} h ${String(minutos % 60).padStart(2, '0')} min`
}
