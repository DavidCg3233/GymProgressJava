<script setup>
// La sesión de entrenamiento en curso (T-006-23 a T-006-28).
import { computed, ref } from 'vue'

import TarjetaDeEjercicio from '../componentes/TarjetaDeEjercicio.vue'
import { agregarEjercicio, estado, terminarSesion } from '../estado/sesion.js'
import { claveDeEjercicio } from '../reglas/ejercicios.js'
import { LARGO_MAXIMO_NOMBRE, LARGO_MAXIMO_NOTA } from '../reglas/textos.js'
import { seriesConfirmadas } from '../sesion/modelo.js'

const emit = defineEmits(['volver'])

// Grupos de la lista predefinida de la spec 002. Con el catálogo propio (hito B) saldrán de ahí.
const GRUPOS = ['Pecho', 'Espalda', 'Hombro', 'Bíceps', 'Tríceps', 'Pierna', 'Pantorrilla', 'Abdomen']

const sesion = computed(() => estado.sesion)
const confirmadas = computed(() => (sesion.value ? seriesConfirmadas(sesion.value) : 0))

// --- Agregar ejercicio ---
const agregando = ref(false)
const nombre = ref('')
const grupo = ref('')
const errorDeEjercicio = ref('')

// Ejercicios que ya he hecho: se sugieren al escribir y traen su grupo.
const conocidos = computed(() => Object.values(estado.ultimaVez))

function alEscribirNombre() {
  const conocido = estado.ultimaVez[claveDeEjercicio(nombre.value)]
  if (conocido) {
    grupo.value = conocido.grupo
  }
}

function guardarEjercicio() {
  errorDeEjercicio.value = ''
  try {
    agregarEjercicio(nombre.value, grupo.value)
    nombre.value = ''
    grupo.value = ''
    agregando.value = false
  } catch (fallo) {
    errorDeEjercicio.value = fallo.mensaje
  }
}

// --- Terminar ---
const terminando = ref(false)
const nombreDeSesion = ref('')
const nota = ref('')
const errorAlTerminar = ref('')
const enviando = ref(false)

async function terminar() {
  errorAlTerminar.value = ''
  enviando.value = true
  try {
    await terminarSesion(nombreDeSesion.value, nota.value)
  } catch (fallo) {
    errorAlTerminar.value = fallo.mensaje
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <main v-if="sesion" class="pantalla">
    <header class="fila fila--separada">
      <div>
        <h1>Sesión en curso</h1>
        <p class="suave">{{ confirmadas }} {{ confirmadas === 1 ? 'serie confirmada' : 'series confirmadas' }}</p>
      </div>
      <button class="boton boton--texto" type="button" @click="emit('volver')">Inicio</button>
    </header>

    <!-- RF-006-18: cambios que el servidor aún no confirma. -->
    <p v-if="estado.aviso" class="mensaje mensaje--aviso" role="status">{{ estado.aviso }}</p>

    <TarjetaDeEjercicio v-for="ejercicio in sesion.ejercicios" :key="ejercicio.id" :ejercicio="ejercicio" />

    <p v-if="sesion.ejercicios.length === 0 && !agregando" class="suave">
      Aún no hay ejercicios. Agrega el primero para empezar a registrar.
    </p>

    <form v-if="agregando" class="tarjeta" @submit.prevent="guardarEjercicio">
      <h2>Nuevo ejercicio</h2>
      <label class="campo">
        <span>Nombre</span>
        <input
          v-model="nombre"
          type="text"
          list="ejercicios-conocidos"
          maxlength="50"
          autocomplete="off"
          placeholder="Ej.: Press inclinado"
          @input="alEscribirNombre"
        />
        <datalist id="ejercicios-conocidos">
          <option v-for="conocido in conocidos" :key="conocido.nombre" :value="conocido.nombre">{{ conocido.grupo }}</option>
        </datalist>
      </label>
      <label class="campo">
        <span>Grupo muscular</span>
        <select v-model="grupo">
          <option value="" disabled>Elige uno</option>
          <option v-for="opcion in GRUPOS" :key="opcion" :value="opcion">{{ opcion }}</option>
          <option v-if="grupo && !GRUPOS.includes(grupo)" :value="grupo">{{ grupo }}</option>
        </select>
      </label>
      <p v-if="errorDeEjercicio" class="mensaje mensaje--error" role="alert">{{ errorDeEjercicio }}</p>
      <div class="fila">
        <button class="boton boton--principal" type="submit">Agregar</button>
        <button class="boton boton--texto" type="button" @click="agregando = false">Cancelar</button>
      </div>
    </form>
    <button v-else class="boton boton--ancho" type="button" @click="agregando = true">+ Ejercicio</button>

    <form v-if="terminando" class="tarjeta" @submit.prevent="terminar">
      <h2>Terminar sesión</h2>
      <p v-if="confirmadas === 0" class="mensaje mensaje--aviso">
        No confirmaste ninguna serie: esta sesión se descartará y no quedará en tu historial.
      </p>
      <template v-else>
        <label class="campo">
          <span>Nombre (opcional)</span>
          <input v-model="nombreDeSesion" type="text" :maxlength="LARGO_MAXIMO_NOMBRE" placeholder="Sesión libre" />
        </label>
        <label class="campo">
          <span>Nota (opcional)</span>
          <textarea v-model="nota" rows="2" :maxlength="LARGO_MAXIMO_NOTA" placeholder="¿Cómo te fue?"></textarea>
        </label>
      </template>
      <p v-if="errorAlTerminar" class="mensaje mensaje--error" role="alert">{{ errorAlTerminar }}</p>
      <div class="fila">
        <button class="boton boton--principal" type="submit" :disabled="enviando">
          {{ confirmadas === 0 ? 'Descartar sesión' : 'Terminar' }}
        </button>
        <button class="boton boton--texto" type="button" @click="terminando = false">Seguir entrenando</button>
      </div>
    </form>
    <button v-else class="boton boton--principal boton--ancho" type="button" @click="terminando = true">
      Terminar sesión
    </button>
  </main>
</template>
