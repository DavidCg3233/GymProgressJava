<script setup>
// Mi catálogo de ejercicios (T-002-16 · RF-002-15 a 19 · RNF-USA-04).
import { computed, ref } from 'vue'

import { eliminarEjercicio, eliminarGrupo, guardarEjercicio, guardarGrupo, usoDeEjercicio } from '../estado/rutinas.js'
import { estado } from '../estado/sesion.js'

const emit = defineEmits(['volver'])

const error = ref('')
const aviso = ref('')
const ocupado = ref(false)

const porGrupo = computed(() =>
  estado.catalogo.grupos.map((grupo) => ({
    ...grupo,
    ejercicios: estado.catalogo.ejercicios.filter((ejercicio) => ejercicio.grupo === grupo.id),
  })),
)

async function intentar(accion) {
  error.value = ''
  aviso.value = ''
  ocupado.value = true
  try {
    await accion()
  } catch (fallo) {
    error.value = fallo.sinConexion ? 'Para cambiar tu catálogo necesitas conexión.' : fallo.mensaje
  } finally {
    ocupado.value = false
  }
}

// --- Editar un ejercicio ----------------------------------------------------

const editando = ref(null) // { id, nombre, grupo }

function editar(ejercicio) {
  editando.value = { ...ejercicio }
  confirmando.value = null
}

function guardarEdicion() {
  return intentar(async () => {
    await guardarEjercicio(editando.value)
    editando.value = null
  })
}

// --- Eliminar un ejercicio (RF-002-17, 18) ----------------------------------

const confirmando = ref(null) // { ejercicio, rutinas }

function pedirEliminar(ejercicio) {
  editando.value = null
  return intentar(async () => {
    confirmando.value = { ejercicio, rutinas: await usoDeEjercicio(ejercicio.id) }
  })
}

function eliminar() {
  return intentar(async () => {
    const eliminadas = await eliminarEjercicio(confirmando.value.ejercicio.id)
    if (eliminadas.length > 0) {
      aviso.value = `También se eliminó: ${eliminadas.map((rutina) => rutina.nombre).join(', ')}.`
    }
    confirmando.value = null
  })
}

// --- Grupos (RF-002-19) -----------------------------------------------------

const grupoNuevo = ref('')

function crearGrupo() {
  return intentar(async () => {
    await guardarGrupo({ nombre: grupoNuevo.value })
    grupoNuevo.value = ''
  })
}

function renombrarGrupo(grupo) {
  const nombre = window.prompt('Nuevo nombre del grupo', grupo.nombre)
  if (nombre !== null && nombre.trim() && nombre !== grupo.nombre) {
    return intentar(() => guardarGrupo({ id: grupo.id, nombre }))
  }
}
</script>

<template>
  <main class="pantalla">
    <header class="fila fila--separada">
      <h1>Mi catálogo</h1>
      <button class="boton boton--texto" type="button" @click="emit('volver')">Volver</button>
    </header>

    <p v-if="error" class="mensaje mensaje--error" role="alert">{{ error }}</p>
    <p v-if="aviso" class="mensaje mensaje--aviso" role="status">{{ aviso }}</p>

    <!-- RF-002-17 y 18: antes de eliminar se ve en qué rutinas está. -->
    <section v-if="confirmando" class="tarjeta">
      <p>¿Eliminar "{{ confirmando.ejercicio.nombre }}" de tu catálogo?</p>
      <p v-if="confirmando.rutinas.length === 0" class="suave">No está en ninguna rutina.</p>
      <template v-else>
        <p class="suave">Se quitará de estas rutinas:</p>
        <ul>
          <li v-for="rutina in confirmando.rutinas" :key="rutina.id">
            {{ rutina.nombre }}<strong v-if="rutina.quedaria_vacia"> (quedaría vacía y se eliminará)</strong>
          </li>
        </ul>
      </template>
      <p class="suave">Tus sesiones pasadas lo conservan.</p>
      <div class="fila">
        <button class="boton boton--peligro" type="button" :disabled="ocupado" @click="eliminar">Sí, eliminar</button>
        <button class="boton boton--texto" type="button" @click="confirmando = null">Cancelar</button>
      </div>
    </section>

    <section v-for="grupo in porGrupo" :key="grupo.id" class="tarjeta">
      <header class="fila fila--separada">
        <h2>{{ grupo.nombre }}</h2>
        <div class="fila">
          <button class="boton boton--texto" type="button" @click="renombrarGrupo(grupo)">Renombrar</button>
          <button class="boton boton--texto" type="button" :disabled="ocupado" @click="intentar(() => eliminarGrupo(grupo.id))">
            Eliminar
          </button>
        </div>
      </header>

      <p v-if="grupo.ejercicios.length === 0" class="suave">Sin ejercicios.</p>

      <div v-for="ejercicio in grupo.ejercicios" :key="ejercicio.id" class="ejercicio">
        <form v-if="editando?.id === ejercicio.id" class="ejercicio__edicion" @submit.prevent="guardarEdicion">
          <input v-model="editando.nombre" type="text" maxlength="50" aria-label="Nombre del ejercicio" />
          <select v-model="editando.grupo" aria-label="Grupo muscular">
            <option v-for="opcion in estado.catalogo.grupos" :key="opcion.id" :value="opcion.id">{{ opcion.nombre }}</option>
          </select>
          <div class="fila">
            <button class="boton boton--principal" type="submit" :disabled="ocupado">Guardar</button>
            <button class="boton boton--texto" type="button" @click="editando = null">Cancelar</button>
          </div>
        </form>
        <div v-else class="fila fila--separada">
          <span>{{ ejercicio.nombre }}</span>
          <div class="fila">
            <button class="boton boton--texto" type="button" @click="editar(ejercicio)">Editar</button>
            <button class="boton boton--texto" type="button" :aria-label="`Eliminar ${ejercicio.nombre}`" @click="pedirEliminar(ejercicio)">✕</button>
          </div>
        </div>
      </div>
    </section>

    <form class="tarjeta" @submit.prevent="crearGrupo">
      <label class="campo">
        <span>Nuevo grupo muscular</span>
        <input v-model="grupoNuevo" type="text" maxlength="30" placeholder="Ej.: Cardio" />
      </label>
      <button class="boton" type="submit" :disabled="ocupado || !grupoNuevo.trim()">Crear grupo</button>
    </form>
  </main>
</template>

<style scoped>
.ejercicio {
  border-top: 1px solid var(--linea);
  padding-top: var(--espacio-2);
}

.ejercicio__edicion {
  display: grid;
  gap: var(--espacio-2);
}

.ejercicio__edicion input,
.ejercicio__edicion select {
  min-height: var(--tamano-toque);
  padding: var(--espacio-2) var(--espacio-3);
  border: 1px solid var(--linea);
  border-radius: var(--radio);
  background: var(--superficie);
}
</style>
