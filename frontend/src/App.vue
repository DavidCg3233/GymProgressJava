<script setup>
// Decide qué pantalla se ve, según el acceso y lo que el usuario eligió.
import { onMounted, ref, watch } from 'vue'

import { acceso, cargarAcceso } from './estado/acceso.js'
import { cargarArranque, estado } from './estado/sesion.js'
import Acceso from './pantallas/Acceso.vue'
import CambiarContrasena from './pantallas/CambiarContrasena.vue'
import Catalogo from './pantallas/Catalogo.vue'
import EditorDeRutina from './pantallas/EditorDeRutina.vue'
import Historial from './pantallas/Historial.vue'
import Inicio from './pantallas/Inicio.vue'
import MisRutinas from './pantallas/MisRutinas.vue'
import SesionEnCurso from './pantallas/SesionEnCurso.vue'

const vista = ref('inicio')
// La rutina que se edita: su id, o null si es nueva.
const rutinaEnEdicion = ref(null)
const errorDeArranque = ref('')

const puedeUsarLaApp = () => acceso.cuenta && !acceso.cuenta.debe_cambiar_contrasena

async function arrancar() {
  errorDeArranque.value = ''
  try {
    await cargarArranque()
    // RF-006-02: con una sesión en curso, se vuelve directo a ella.
    vista.value = estado.sesion ? 'sesion' : 'inicio'
  } catch (fallo) {
    errorDeArranque.value = fallo.sinConexion ? 'Sin conexión. Revisa tu señal e inténtalo de nuevo.' : fallo.mensaje
  }
}

onMounted(async () => {
  try {
    await cargarAcceso()
  } catch (fallo) {
    errorDeArranque.value = fallo.sinConexion ? 'Sin conexión. Revisa tu señal e inténtalo de nuevo.' : fallo.mensaje
  }
})

// Al entrar (o al cambiar la contraseña temporal) se cargan los datos; al salir se limpian.
watch(
  () => puedeUsarLaApp(),
  (puede) => {
    estado.resumen = null
    if (puede) {
      arrancar()
    } else {
      estado.sesion = null
      estado.ultimaVez = {}
      estado.cargando = true
      vista.value = 'inicio'
    }
  },
)

function editarRutina(id) {
  rutinaEnEdicion.value = id
  vista.value = 'editor'
}

function ir(destino) {
  estado.resumen = null
  vista.value = destino
}
</script>

<template>
  <main v-if="acceso.cargando" class="pantalla"><p class="suave">Cargando…</p></main>

  <main v-else-if="errorDeArranque" class="pantalla">
    <p class="mensaje mensaje--error" role="alert">{{ errorDeArranque }}</p>
    <button class="boton boton--ancho" type="button" @click="acceso.cuenta ? arrancar() : cargarAcceso()">Reintentar</button>
  </main>

  <Acceso v-else-if="!acceso.cuenta" />

  <CambiarContrasena v-else-if="acceso.cuenta.debe_cambiar_contrasena" obligatorio />

  <main v-else-if="estado.cargando" class="pantalla"><p class="suave">Cargando…</p></main>

  <SesionEnCurso v-else-if="vista === 'sesion' && estado.sesion" @volver="ir('inicio')" />

  <Historial v-else-if="vista === 'historial'" @volver="ir('inicio')" />

  <MisRutinas
    v-else-if="vista === 'rutinas'"
    @volver="ir('inicio')"
    @editar="editarRutina"
    @sesion="ir('sesion')"
    @catalogo="ir('catalogo')"
  />

  <EditorDeRutina
    v-else-if="vista === 'editor'"
    :key="rutinaEnEdicion ?? 'nueva'"
    :rutina-id="rutinaEnEdicion"
    @listo="ir('rutinas')"
    @cancelar="ir('rutinas')"
  />

  <Catalogo v-else-if="vista === 'catalogo'" @volver="ir('rutinas')" />

  <CambiarContrasena v-else-if="vista === 'contrasena'" @listo="ir('inicio')" @cancelar="ir('inicio')" />

  <Inicio
    v-else
    @sesion="ir('sesion')"
    @historial="ir('historial')"
    @contrasena="ir('contrasena')"
    @rutinas="ir('rutinas')"
  />
</template>
