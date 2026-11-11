<script setup>
// Gráfica de línea propia en SVG (T-004-14 · plan 004, sección 6): un punto por sesión.
import { computed, ref, watch } from 'vue'

import { puntosDeLaGrafica } from '../progreso/grafica.js'

const props = defineProps({
  valores: { type: Array, required: true },
  // Texto de cada punto al tocarlo, por ejemplo "16 nov · 35 kg × 6".
  detalles: { type: Array, required: true },
  formato: { type: Function, required: true },
})

const AREA = { ancho: 300, alto: 160, margen: 16 }

const grafica = computed(() => puntosDeLaGrafica(props.valores, AREA))
const linea = computed(() => grafica.value.puntos.map(({ x, y }) => `${x},${y}`).join(' '))

// Arranca mostrando el último punto: lo más reciente es lo que más interesa.
const elegido = ref(props.valores.length - 1)
watch(
  () => props.valores,
  (valores) => {
    elegido.value = valores.length - 1
  },
)
</script>

<template>
  <figure class="grafica">
    <svg :viewBox="`0 0 ${AREA.ancho} ${AREA.alto}`" role="img" :aria-label="`Gráfica con ${valores.length} sesiones`">
      <polyline v-if="grafica.puntos.length > 1" class="grafica__linea" :points="linea" />
      <circle
        v-for="(punto, indice) in grafica.puntos"
        :key="indice"
        class="grafica__punto"
        :class="{ 'grafica__punto--elegido': indice === elegido }"
        :cx="punto.x"
        :cy="punto.y"
        :r="indice === elegido ? 7 : 5"
        role="button"
        tabindex="0"
        :aria-label="detalles[indice]"
        @click="elegido = indice"
        @keydown.enter="elegido = indice"
      />
    </svg>
    <figcaption class="fila fila--separada suave">
      <span>Mín. {{ formato(grafica.minimo) }}</span>
      <span>Máx. {{ formato(grafica.maximo) }}</span>
    </figcaption>
    <p v-if="elegido >= 0" class="grafica__detalle" role="status">{{ detalles[elegido] }}</p>
  </figure>
</template>

<style scoped>
.grafica {
  margin: 0;
  display: grid;
  gap: var(--espacio-2);
}

.grafica svg {
  width: 100%;
  height: auto;
  background: var(--color-fondo);
  border-radius: var(--radio);
  overflow: visible;
}

.grafica__linea {
  fill: none;
  stroke: var(--color-acento);
  stroke-width: 2.5;
  stroke-linejoin: round;
}

.grafica__punto {
  fill: var(--color-superficie);
  stroke: var(--color-acento);
  stroke-width: 2.5;
  cursor: pointer;
}

.grafica__punto--elegido {
  fill: var(--color-acento);
}

.grafica__detalle {
  margin: 0;
  font-weight: 600;
}
</style>
