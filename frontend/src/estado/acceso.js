// Estado del acceso: quién entró, y las acciones de entrar, salir y cambiar contraseña.
//
// El celular recuerda la cuenta con que se entró la última vez, para poder abrir
// la app sin señal (RF-006-17). Con señal, siempre manda lo que diga el servidor.

import { reactive } from 'vue'

import { crearAlmacen } from '../datos/almacen.js'
import { pedir } from '../datos/api.js'

const CLAVE = 'cuenta'
const almacen = crearAlmacen()

export const acceso = reactive({
  cargando: true,
  cuenta: null,
})

async function recordar(cuenta) {
  acceso.cuenta = cuenta
  await almacen.guardar(CLAVE, cuenta)
}

/** Pregunta al servidor si hay acceso vigente. También deja lista la protección CSRF. */
export async function cargarAcceso() {
  try {
    const datos = await pedir('GET', '/api/acceso/')
    await recordar(datos.cuenta)
  } catch (error) {
    if (!(error.sinConexion || error.estado >= 500)) {
      throw error
    }
    // Sin señal: se sigue con la cuenta de la última vez, si la hay.
    // Al volver la señal, el servidor confirmará o pedirá entrar de nuevo.
    acceso.cuenta = await almacen.leer(CLAVE)
  } finally {
    acceso.cargando = false
  }
}

export async function entrar(identificador, contrasena) {
  const datos = await pedir('POST', '/api/acceso/entrar/', { identificador, contrasena })
  await recordar(datos.cuenta)
}

export async function salir() {
  await pedir('POST', '/api/acceso/salir/')
  await recordar(null)
}

export async function cambiarContrasena(actual, nueva) {
  await pedir('POST', '/api/acceso/contrasena/', { actual, nueva })
  await recordar({ ...acceso.cuenta, debe_cambiar_contrasena: false })
}
