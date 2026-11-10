// Estado del acceso: quién entró, y las acciones de entrar, salir y cambiar contraseña.

import { reactive } from 'vue'

import { pedir } from '../datos/api.js'

export const acceso = reactive({
  cargando: true,
  cuenta: null,
})

/** Pregunta al servidor si hay acceso vigente. También deja lista la protección CSRF. */
export async function cargarAcceso() {
  try {
    const datos = await pedir('GET', '/api/acceso/')
    acceso.cuenta = datos.cuenta
  } finally {
    acceso.cargando = false
  }
}

export async function entrar(identificador, contrasena) {
  const datos = await pedir('POST', '/api/acceso/entrar/', { identificador, contrasena })
  acceso.cuenta = datos.cuenta
}

export async function salir() {
  await pedir('POST', '/api/acceso/salir/')
  acceso.cuenta = null
}

export async function cambiarContrasena(actual, nueva) {
  await pedir('POST', '/api/acceso/contrasena/', { actual, nueva })
  acceso.cuenta.debe_cambiar_contrasena = false
}
