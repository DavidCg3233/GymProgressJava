// Almacenamiento en el celular (T-006-30 · RNF-006-06).
// Lo guardado aquí sobrevive a cerrar la app y a apagar la pantalla.

import { IDBFactory } from 'fake-indexeddb'
import { beforeEach, describe, expect, it } from 'vitest'

import { crearAlmacen } from './almacen.js'

beforeEach(() => {
  globalThis.indexedDB = new IDBFactory()
})

describe('almacén del celular', () => {
  it('lo que se guarda se puede leer después', async () => {
    const almacen = crearAlmacen()

    await almacen.guardar('estado', { sesion: { id: 'a', series: [1, 2] } })

    expect(await almacen.leer('estado')).toEqual({ sesion: { id: 'a', series: [1, 2] } })
  })

  it('una clave que nunca se guardó se lee como null', async () => {
    expect(await crearAlmacen().leer('no-existe')).toBeNull()
  })

  it('guardar otra vez reemplaza el valor', async () => {
    const almacen = crearAlmacen()
    await almacen.guardar('cola', [1])

    await almacen.guardar('cola', [1, 2])

    expect(await almacen.leer('cola')).toEqual([1, 2])
  })

  it('RNF-006-06: los datos siguen ahí al "volver a abrir la app"', async () => {
    await crearAlmacen().guardar('estado', { pendiente: true })

    // Otra instancia, como al recargar la página.
    expect(await crearAlmacen().leer('estado')).toEqual({ pendiente: true })
  })

  it('borrar todo deja el almacén vacío (al salir de la cuenta)', async () => {
    const almacen = crearAlmacen()
    await almacen.guardar('estado', 1)
    await almacen.guardar('cola', 2)

    await almacen.borrarTodo()

    expect(await almacen.leer('estado')).toBeNull()
    expect(await almacen.leer('cola')).toBeNull()
  })

  it('guarda una copia: cambiar el objeto después no altera lo guardado', async () => {
    const almacen = crearAlmacen()
    const sesion = { nombre: 'antes' }
    await almacen.guardar('estado', sesion)

    sesion.nombre = 'después'

    expect(await almacen.leer('estado')).toEqual({ nombre: 'antes' })
  })
})
