<script setup>
// Íconos propios en SVG (T-007-03 · DESIGN.md, sección 6 · RNF-007-05).
// Van dentro del código: nada se descarga y funcionan sin señal.
// Trazo de 1,75, extremos redondeados, 24 px. Toman el color del texto.

const TRAZOS = {
  inicio: ['M4 10.5 12 4l8 6.5V20h-5.5v-5.5h-5V20H4z'],
  rutinas: ['M9 6h11', 'M9 12h11', 'M9 18h11', 'M4.5 6h.01', 'M4.5 12h.01', 'M4.5 18h.01'],
  progreso: ['M4 4v15h16', 'M7.5 14.5l3.5-4 3 2.5 5-6.5'],
  historial: ['M12 4a8 8 0 1 1 0 16a8 8 0 0 1 0-16z', 'M12 8v4.5l3 2'],
  mas: ['M12 5v14', 'M5 12h14'],
  menos: ['M5 12h14'],
  palomita: ['M5 12.5l4.5 4.5L19 7.5'],
  derecha: ['M9.5 6l6 6-6 6'],
  izquierda: ['M14.5 6l-6 6 6 6'],
  abajo: ['M6 9.5l6 6 6-6'],
  cerrar: ['M6.5 6.5l11 11', 'M17.5 6.5l-11 11'],
  cuenta: ['M12 4.5a4 4 0 1 1 0 8a4 4 0 0 1 0-8z', 'M4.5 20c1.5-3.2 4.3-4.8 7.5-4.8s6 1.6 7.5 4.8'],
}

export const NOMBRES_DE_ICONOS = Object.keys(TRAZOS)

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
