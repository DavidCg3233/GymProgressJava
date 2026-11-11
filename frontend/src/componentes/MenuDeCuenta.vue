<script setup>
// Menú de cuenta (T-007-08 · RF-007-07 · RNF-USA-04 · RNF-ACC-04).
// "Cambiar contraseña" y "Salir", desde el encabezado del Inicio.
import { onMounted, onUnmounted, ref } from 'vue'

import { salir } from '../estado/acceso.js'
import { estado, olvidarDatosLocales } from '../estado/sesion.js'
import Icono from './Icono.vue'

const emit = defineEmits(['contrasena'])

const abierto = ref(false)
const confirmandoSalida = ref(false)
const error = ref('')

// Se cierra al tocar fuera o con Escape, como un menú del iPhone.
const raiz = ref(null)
function cerrarSiEsAfuera(evento) {
  if (abierto.value && raiz.value && !raiz.value.contains(evento.target)) {
    abierto.value = false
  }
}
function cerrarConEscape(evento) {
  if (evento.key === 'Escape') {
    abierto.value = false
  }
}
onMounted(() => {
  document.addEventListener('pointerdown', cerrarSiEsAfuera)
  document.addEventListener('keydown', cerrarConEscape)
})
onUnmounted(() => {
  document.removeEventListener('pointerdown', cerrarSiEsAfuera)
  document.removeEventListener('keydown', cerrarConEscape)
})

function alternar() {
  abierto.value = !abierto.value
  confirmandoSalida.value = false
  error.value = ''
}

// RNF-ACC-04: al salir no queda nada de esta persona en el celular.
// Si hay cambios sin enviar, se perderían: primero se avisa (RNF-USA-04).
async function salirDeLaCuenta() {
  if (estado.pendientes > 0 && !confirmandoSalida.value) {
    confirmandoSalida.value = true
    return
  }
  error.value = ''
  try {
    await salir()
    await olvidarDatosLocales()
  } catch (fallo) {
    error.value = fallo.sinConexion ? 'Para salir de la cuenta necesitas conexión.' : fallo.mensaje
  }
}
</script>

<template>
  <div ref="raiz" class="cuenta">
    <button class="boton boton--texto cuenta__boton" type="button" aria-label="Cuenta" :aria-expanded="abierto" @click="alternar">
      <Icono nombre="cuenta" :tamano="28" />
    </button>

    <div v-if="abierto" class="cuenta__menu" role="group" aria-label="Cuenta">
      <template v-if="!confirmandoSalida">
        <button class="cuenta__opcion" type="button" @click="emit('contrasena')">Cambiar contraseña</button>
        <button class="cuenta__opcion cuenta__opcion--peligro" type="button" @click="salirDeLaCuenta">Salir</button>
      </template>

      <div v-else class="cuenta__aviso">
        <p>
          Tienes {{ estado.pendientes }} {{ estado.pendientes === 1 ? 'cambio' : 'cambios' }} sin enviar al servidor. Si sales
          ahora, se pierden.
        </p>
        <button class="boton boton--peligro boton--ancho" type="button" @click="salirDeLaCuenta">Salir y perderlos</button>
        <button class="boton boton--texto boton--ancho" type="button" @click="confirmandoSalida = false">Cancelar</button>
      </div>

      <p v-if="error" class="mensaje mensaje--error cuenta__error" role="alert">{{ error }}</p>
    </div>
  </div>
</template>

<style scoped>
.cuenta {
  position: relative;
}

.cuenta__boton {
  padding: 0;
  color: var(--acento);
}

.cuenta__menu {
  position: absolute;
  z-index: 20;
  top: calc(100% + var(--espacio-1));
  right: 0;
  width: min(17rem, calc(100vw - 2 * var(--espacio-4)));
  display: grid;
  border-radius: var(--radio-grupo);
  background: var(--superficie);
  border: 1px solid var(--linea);
  overflow: hidden;
}

.cuenta__opcion {
  min-height: 48px;
  padding: 0 var(--espacio-4);
  border: 0;
  border-top: 1px solid var(--linea);
  background: none;
  color: var(--tinta);
  text-align: left;
  cursor: pointer;
}

.cuenta__opcion:first-child {
  border-top: 0;
}

.cuenta__opcion--peligro {
  color: var(--error);
}

.cuenta__aviso {
  display: grid;
  gap: var(--espacio-2);
  padding: var(--espacio-4);
  font-size: 15px;
}

.cuenta__error {
  padding: 0 var(--espacio-4) var(--espacio-3);
}
</style>
