// Destinos de la barra inferior (spec 007 · RN-007-01, RF-007-01, 02).

/** Los cuatro, siempre en este orden, con ícono y nombre escrito. */
export const DESTINOS = [
  { vista: 'inicio', nombre: 'Inicio', icono: 'inicio' },
  { vista: 'rutinas', nombre: 'Rutinas', icono: 'rutinas' },
  { vista: 'progreso', nombre: 'Progreso', icono: 'progreso' },
  { vista: 'historial', nombre: 'Historial', icono: 'historial' },
]

// Las vistas que viven dentro de una sección marcan esa sección.
const SECCION_DE = {
  contrasena: 'inicio',
  editor: 'rutinas',
  catalogo: 'rutinas',
}

/** Qué destino de la barra se marca mientras se ve `vista`. */
export function destinoDe(vista) {
  if (DESTINOS.some((destino) => destino.vista === vista)) {
    return vista
  }
  return SECCION_DE[vista] ?? 'inicio'
}

/** RF-007-02: la sesión en curso ocupa toda la pantalla, sin barra. */
export function muestraBarra(vista) {
  return vista !== 'sesion'
}

/**
 * RF-007-03: la franja de la sesión en curso se ve fuera de la sesión.
 * En el Inicio no: ahí "Continuar sesión" ya es lo primero (RF-004-02, CA-004-02a)
 * y repetirlo sería el mismo botón dos veces.
 */
export function muestraFranja(vista, haySesion) {
  return haySesion && vista !== 'sesion' && vista !== 'inicio'
}
