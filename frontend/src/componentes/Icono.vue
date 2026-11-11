<script setup>
// Íconos propios en SVG (T-007-03 · DESIGN.md, sección 6 · RNF-007-05).
// Van dentro del código: nada se descarga y funcionan sin señal.
// Trazo de 1,75, extremos redondeados, 24 px. Toman el color del texto.
import { TRAZOS } from './iconos.js'

const props = defineProps({
  nombre: { type: String, required: true, validator: (nombre) => nombre in TRAZOS },
  tamano: { type: Number, default: 24 },
  grosor: { type: Number, default: 1.75 },
})
</script>

<template>
  <!-- Decorativo: el nombre lo pone el botón que lo contiene. -->
  <svg
    class="icono"
    :width="props.tamano"
    :height="props.tamano"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    :stroke-width="props.grosor"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    focusable="false"
  >
    <path v-for="trazo in TRAZOS[props.nombre]" :key="trazo" :d="trazo" />
  </svg>
</template>

<style scoped>
.icono {
  flex: none;
  display: block;
}
</style>
