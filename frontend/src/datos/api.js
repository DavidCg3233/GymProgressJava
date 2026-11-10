// Cómo habla la pantalla con el servidor.
//
// Todo pasa por `pedir`: agrega la protección CSRF, habla JSON y convierte
// cualquier fallo en un ErrorDeApi con un mensaje apto para el usuario.

const MENSAJE_GENERICO = 'Algo salió mal. Inténtalo de nuevo.'
const MENSAJE_SIN_CONEXION = 'Sin conexión.'
const COOKIE_CSRF = 'csrftoken'
const METODOS_DE_LECTURA = new Set(['GET', 'HEAD'])

export class ErrorDeApi extends Error {
  /**
   * @param {number} estado  Código HTTP, o 0 si no hubo respuesta (sin conexión).
   * @param {string} mensaje Texto para mostrar al usuario.
   * @param {object} datos   Lo demás que haya enviado el servidor.
   */
  constructor(estado, mensaje, datos = {}) {
    super(mensaje)
    this.name = 'ErrorDeApi'
    this.estado = estado
    this.mensaje = mensaje
    this.campo = datos.campo ?? null
    this.datos = datos
    this.sinConexion = estado === 0
  }
}

export async function pedir(metodo, url, cuerpo) {
  const opciones = {
    method: metodo,
    // La cookie de acceso viaja sola; el código de la página no puede leerla.
    credentials: 'same-origin',
    headers: { Accept: 'application/json' },
  }
  if (!METODOS_DE_LECTURA.has(metodo)) {
    opciones.headers['X-CSRFToken'] = leerCookie(COOKIE_CSRF)
    if (cuerpo !== undefined) {
      opciones.headers['Content-Type'] = 'application/json'
      opciones.body = JSON.stringify(cuerpo)
    }
  }

  let respuesta
  try {
    respuesta = await fetch(url, opciones)
  } catch {
    throw new ErrorDeApi(0, MENSAJE_SIN_CONEXION)
  }

  if (respuesta.status === 204) {
    return null
  }
  const datos = await respuesta.json().catch(() => null)
  if (!respuesta.ok) {
    throw new ErrorDeApi(respuesta.status, datos?.mensaje ?? MENSAJE_GENERICO, datos ?? {})
  }
  return datos
}

function leerCookie(nombre) {
  const cookies = globalThis.document?.cookie ?? ''
  const encontrada = cookies.split('; ').find((cookie) => cookie.startsWith(`${nombre}=`))
  return encontrada ? decodeURIComponent(encontrada.slice(nombre.length + 1)) : ''
}
