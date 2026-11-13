<script setup>
// Un ejercicio de la sesión en curso, con sus series y su nota.
import { onUnmounted, ref } from 'vue'

import { agregarSerie, anotarEjercicio, deshacerQuitarSerie, quitarSerie } from '../estado/sesion.js'
import { LARGO_MAXIMO_NOTA } from '../reglas/textos.js'
import FilaDeSerie from './FilaDeSerie.vue'

const props = defineProps({ ejercicio: { type: Object, required: true } })

const nota = ref(props.ejercicio.nota)
const editandoNota = ref(false)
const error = ref('')

function agregar() {
  error.value = ''
  try {
    agregarSerie(props.ejercicio)
  } catch (fallo) {
    error.value = fallo.mensaje
  }
}

// --- Quitar y deshacer (RF-008-08, 09) -----------------------------------------

const DURACION_DE_DESHACER = 5_000 // RN-008-09
const quitada = ref(null) // { quitada, numero }
let temporizador = null

function olvidarQuitada() {
  clearTimeout(temporizador)
  quitada.value = null
}

async function quitar(serie) {
  error.value = ''
  olvidarQuitada()
  const numero = serie.numero
  const resultado = await quitarSerie(props.ejercicio, serie)
  if (resultado) {
    quitada.value = { quitada: resultado, numero }
    temporizador = setTimeout(olvidarQuitada, DURACION_DE_DESHACER)
  }
}

async function deshacer() {
  const { quitada: resultado } = quitada.value
  olvidarQuitada()
  await deshacerQuitarSerie(props.ejercicio, resultado)
}

onUnmounted(olvidarQuitada)

function guardarNota() {
  error.value = ''
  try {
    anotarEjercicio(props.ejercicio, nota.value)
    editandoNota.value = false
  } catch (fallo) {
    error.value = fallo.mensaje
  }
}
</script>

<template>
  <section class="tarjeta ejercicio">
    <header>
      <h2>{{ props.ejercicio.nombre }}</h2>
      <p class="suave">{{ props.ejercicio.grupo }}</p>
    </header>

    <!-- RF-006-23: lo que anoté la última vez. -->
    <p v-if="props.ejercicio.notaAnterior" class="mensaje mensaje--aviso">
      La última vez: “{{ props.ejercicio.notaAnterior }}”
    </p>

    <div class="ejercicio__series">
      <FilaDeSerie
        v-for="serie in props.ejercicio.series"
        :key="serie.id"
        :ejercicio="props.ejercicio"
        :serie="serie"
        @quitar="quitar"
      />
    </div>

    <!-- RF-008-09: un toque de más no borra nada para siempre. -->
    <div v-if="quitada" class="deshacer" role="status">
      <span>Serie {{ quitada.numero }} quitada</span>
      <button class="boton boton--texto" type="button" @click="deshacer">Deshacer</button>
    </div>

    <p v-if="error" class="mensaje mensaje--error" role="alert">{{ error }}</p>

    <form v-if="editandoNota" class="campo" @submit.prevent="guardarNota">
      <span>Nota del ejercicio</span>
      <textarea v-model="nota" rows="2" :maxlength="LARGO_MAXIMO_NOTA" placeholder="Ej.: subir a 35 la próxima"></textarea>
      <div class="fila">
        <button class="boton boton--principal" type="submit">Guardar nota</button>
        <button class="boton boton--texto" type="button" @click="editandoNota = false">Cancelar</button>
      </div>
    </form>
    <p v-else-if="props.ejercicio.nota" class="suave">Nota de hoy: “{{ props.ejercicio.nota }}”</p>

    <div class="fila fila--separada">
      <button class="boton" type="button" @click="agregar">+ Serie</button>
      <button v-if="!editandoNota" class="boton boton--texto" type="button" @click="editandoNota = true">
        {{ props.ejercicio.nota ? 'Editar nota' : 'Agregar nota' }}
      </button>
    </div>
  </section>
</template>

<style scoped>
.deshacer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-left: var(--espacio-3);
  border-radius: var(--radio);
  background: var(--superficie-2);
  font-size: 15px;
}

.ejercicio__series {
  display: grid;
  gap: var(--espacio-1);
  /* Las filas llegan casi al borde de la tarjeta para dar más ancho a los controles. */
  margin: 0 calc(-1 * var(--espacio-2));
}
</style>
