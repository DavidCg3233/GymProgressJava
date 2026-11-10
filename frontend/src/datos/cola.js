// Cola de pendientes (T-006-31 · RF-006-16, RF-006-18).
//
// Cada cambio hecho en el celular entra aquí y sale cuando el servidor lo
// acepta. La cola vive en el almacén del celular, así que sobrevive a cerrar
// la app. Se envía en orden: el servidor debe conocer la sesión antes que sus
// ejercicios, y los ejercicios antes que sus series.

const CLAVE = 'cola'

/**
 * @param {object}   dependencias
 * @param {object}   dependencias.almacen    Dónde se guarda la cola (leer, guardar).
 * @param {Function} dependencias.enviar     Envía una operación; lanza un error con `estado` si falla.
 * @param {Function} [dependencias.alCambiar] Recibe la cantidad de pendientes cada vez que cambia.
 */
export function crearCola({ almacen, enviar, alCambiar = () => {} }) {
  let operaciones = null
  let carga = null
  let vueltaEnCurso = null

  function cargar() {
    carga ??= almacen.leer(CLAVE).then((guardadas) => {
      operaciones = guardadas ?? []
      return operaciones
    })
    return carga
  }

  async function guardar() {
    await almacen.guardar(CLAVE, operaciones)
    alCambiar(operaciones.length)
  }

  async function enviarEnOrden() {
    await cargar()
    const rechazos = []

    while (operaciones.length > 0) {
      const operacion = operaciones[0]
      const resultado = await intentar(operacion)

      if (resultado.detenida) {
        return { pendientes: operaciones.length, detenida: resultado.detenida, rechazos }
      }
      if (resultado.rechazo) {
        rechazos.push({ operacion, mensaje: resultado.rechazo })
      }
      // Si mientras se enviaba llegó una versión nueva del mismo dato, ocupó este
      // lugar: no se quita, para que la versión nueva también se envíe.
      if (operaciones[0] === operacion) {
        operaciones.shift()
        await guardar()
      }
    }
    return { pendientes: 0, detenida: null, rechazos }
  }

  async function intentar(operacion) {
    try {
      await enviar(operacion)
      return {}
    } catch (error) {
      return clasificar(operacion, error)
    }
  }

  return {
    async pendientes() {
      return (await cargar()).length
    },

    /**
     * Agrega un cambio al final.
     *
     * Si el último pendiente es sobre el mismo dato, lo reemplaza: dos cambios
     * seguidos equivalen al último. Pero si hay otros en medio, se conservan los
     * dos, porque el orden importa: el cierre de una sesión no puede adelantarse
     * a sus series, ni una serie a su ejercicio.
     */
    async agregar(operacion) {
      await cargar()
      const ultima = operaciones.at(-1)
      if (ultima && ultima.metodo === operacion.metodo && ultima.url === operacion.url) {
        operaciones[operaciones.length - 1] = operacion
      } else {
        operaciones.push(operacion)
      }
      await guardar()
    },

    /** Envía lo pendiente. Si ya se está enviando, devuelve esa misma vuelta. */
    procesar() {
      vueltaEnCurso ??= enviarEnOrden().finally(() => {
        vueltaEnCurso = null
      })
      return vueltaEnCurso
    },

    async vaciar() {
      await cargar()
      operaciones.length = 0
      await guardar()
    },
  }
}

/**
 * Qué hacer con una operación que falló:
 * - Sin conexión o falla pasajera del servidor: esperar y reintentar después.
 * - Acceso vencido: esperar a que el usuario vuelva a entrar, sin perder nada.
 * - Quitar algo que ya no existe: ya estaba hecho.
 * - Cualquier otro rechazo: el dato no es válido; se descarta y se informa.
 */
function clasificar(operacion, error) {
  const estado = typeof error?.estado === 'number' ? error.estado : 0

  if (estado === 0 || estado >= 500 || estado === 429) {
    return { detenida: 'sin-conexion' }
  }
  if (estado === 401 || estado === 403) {
    return { detenida: 'acceso' }
  }
  if (estado === 404 && operacion.metodo === 'DELETE') {
    return {}
  }
  return { rechazo: error.mensaje ?? 'El servidor no aceptó un cambio.' }
}
