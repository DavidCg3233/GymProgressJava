<script setup>
// Un ejercicio de la sesión en curso, con sus series y su nota.
import { ref } from 'vue'

import { agregarSerie, anotarEjercicio } from '../estado/sesion.js'
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
      />
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
.ejercicio__series {
  display: grid;
  gap: var(--espacio-1);
  /* Las filas llegan casi al borde de la tarjeta para dar más ancho a los controles. */
  margin: 0 calc(-1 * var(--espacio-2));
}
</style>
