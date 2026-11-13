<script setup>
// Buscador de ejercicios (T-008-11 · RF-008-10 · RNF-008-01).
//
// Reemplaza el <datalist> del navegador, que en Safari del iPhone da tirones al
// escribir. La lista la arma una función pura (sugerencias) y se dibuja aquí.
import { computed, ref } from 'vue'

import { sugerencias } from '../sesion/series.js'

const props = defineProps({
  modelValue: { type: String, required: true },
  // [{ nombre, detalle, ... }]: `detalle` se muestra a la derecha (el grupo).
  opciones: { type: Array, required: true },
  etiqueta: { type: String, default: 'Nombre' },
  placeholder: { type: String, default: 'Ej.: Press inclinado' },
})
const emit = defineEmits(['update:modelValue', 'elegir'])

const enfocado = ref(false)
const lista = computed(() => (enfocado.value ? sugerencias(props.opciones, props.modelValue) : []))

function elegir(opcion) {
  emit('update:modelValue', opcion.nombre)
  emit('elegir', opcion)
  enfocado.value = false
}

// Al salir del campo la lista se cierra, pero después del toque en una sugerencia.
function alSalir() {
  setTimeout(() => {
    enfocado.value = false
  }, 150)
}
</script>

<template>
  <div class="buscador">
    <label class="campo">
      <span>{{ etiqueta }}</span>
      <input
        :value="modelValue"
        type="text"
        maxlength="50"
        :placeholder="placeholder"
        autocomplete="off"
        autocorrect="off"
        autocapitalize="sentences"
        spellcheck="false"
        enterkeyhint="done"
        role="combobox"
        :aria-expanded="lista.length > 0"
        aria-autocomplete="list"
        @input="emit('update:modelValue', $event.target.value)"
        @focus="enfocado = true"
        @blur="alSalir"
      />
    </label>
    <ul v-if="lista.length > 0" class="buscador__lista" role="listbox" :aria-label="`Sugerencias para ${etiqueta.toLowerCase()}`">
      <li v-for="opcion in lista" :key="opcion.nombre" role="none">
        <button class="buscador__opcion" type="button" role="option" @pointerdown.prevent @click="elegir(opcion)">
          <span>{{ opcion.nombre }}</span>
          <span class="suave">{{ opcion.detalle }}</span>
        </button>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.buscador {
  display: grid;
  gap: var(--espacio-1);
}

.buscador__lista {
  list-style: none;
  margin: 0;
  padding: 0;
  border-radius: var(--radio);
  background: var(--superficie-2);
  overflow: hidden;
}

.buscador__opcion {
  width: 100%;
  min-height: var(--tamano-toque);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--espacio-2);
  padding: 0 var(--espacio-3);
  border: 0;
  border-top: 1px solid var(--linea);
  background: none;
  color: var(--tinta);
  text-align: left;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

li:first-child .buscador__opcion {
  border-top: 0;
}
</style>
