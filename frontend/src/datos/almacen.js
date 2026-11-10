// Almacenamiento en el celular, con IndexedDB (T-006-30 · RNF-006-06).
//
// Un almacén de clave y valor: suficiente para guardar la sesión en curso,
// "la última vez" y la cola de pendientes. Lo guardado sobrevive a cerrar la
// app, a apagar la pantalla y a quedarse sin señal.
//
// El plan proponía la librería Dexie. Para tres claves no hace falta: estas
// 40 líneas evitan una dependencia más que auditar (RNF-SEG-07).

const NOMBRE_DE_LA_BASE = 'gymprogress'
const VERSION = 1
const TABLA = 'datos'

export function crearAlmacen() {
  let conexion = null

  function abrir() {
    conexion ??= new Promise((resolver, rechazar) => {
      const peticion = globalThis.indexedDB.open(NOMBRE_DE_LA_BASE, VERSION)
      peticion.onupgradeneeded = () => peticion.result.createObjectStore(TABLA)
      peticion.onsuccess = () => resolver(peticion.result)
      peticion.onerror = () => rechazar(peticion.error)
    })
    return conexion
  }

  /** Corre una operación en una transacción y espera a que quede escrita de verdad. */
  async function operar(modo, accion) {
    const base = await abrir()
    return new Promise((resolver, rechazar) => {
      const transaccion = base.transaction(TABLA, modo)
      const peticion = accion(transaccion.objectStore(TABLA))
      transaccion.oncomplete = () => resolver(peticion.result)
      transaccion.onerror = () => rechazar(transaccion.error)
      transaccion.onabort = () => rechazar(transaccion.error)
    })
  }

  return {
    async leer(clave) {
      return (await operar('readonly', (tabla) => tabla.get(clave))) ?? null
    },

    async guardar(clave, valor) {
      // Copia en datos simples: los objetos reactivos de Vue no se pueden guardar tal cual,
      // y así un cambio posterior al objeto no altera lo guardado.
      const copia = JSON.parse(JSON.stringify(valor))
      await operar('readwrite', (tabla) => tabla.put(copia, clave))
    },

    async borrarTodo() {
      await operar('readwrite', (tabla) => tabla.clear())
    },
  }
}
