// Cada cambio del usuario, convertido en la petición que lo guarda en el servidor.
//
// Son objetos simples { metodo, url, cuerpo }: se pueden enviar ya, o guardar
// en una cola y enviar cuando vuelva la conexión. Todas son repetibles: enviar
// dos veces la misma deja el mismo resultado.

export function guardarSesion(sesion) {
  return {
    metodo: 'PUT',
    url: `/api/sesiones/${sesion.id}/`,
    cuerpo: { nombre: sesion.nombre, inicio: sesion.inicio, fin: sesion.fin, nota: sesion.nota },
  }
}

export function guardarEjercicio(sesion, ejercicio, momento) {
  return {
    metodo: 'PUT',
    url: `/api/sesiones/${sesion.id}/ejercicios/${ejercicio.id}/`,
    cuerpo: {
      nombre: ejercicio.nombre,
      grupo: ejercicio.grupo,
      orden: ejercicio.orden,
      nota: ejercicio.nota,
      momento: momento.toISOString(),
    },
  }
}

export function guardarSerie(ejercicio, serie, momento) {
  return {
    metodo: 'PUT',
    url: `/api/series/${serie.id}/`,
    cuerpo: {
      ejercicio: ejercicio.id,
      numero: serie.numero,
      peso: serie.peso,
      reps: serie.reps,
      confirmada: serie.confirmada,
      momento: momento.toISOString(),
    },
  }
}

export function quitarSerie(serie, momento) {
  return { metodo: 'DELETE', url: `/api/series/${serie.id}/`, cuerpo: { momento: momento.toISOString() } }
}
