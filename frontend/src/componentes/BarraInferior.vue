<script setup>
// Barra inferior (T-007-06 · RF-007-01 · RN-007-01 · RNF-007-06 · DESIGN.md, sección 5).
import { DESTINOS } from '../navegacion/destinos.js'
import Icono from './Icono.vue'

defineProps({
  // El destino marcado: 'inicio', 'rutinas', 'progreso' o 'historial'.
  actual: { type: String, required: true },
})
const emit = defineEmits(['ir'])
</script>

<template>
  <nav class="barra" aria-label="Secciones">
    <button
      v-for="destino in DESTINOS"
      :key="destino.vista"
      class="barra__destino"
      :class="{ 'barra__destino--actual': destino.vista === actual }"
      type="button"
      :aria-current="destino.vista === actual ? 'page' : undefined"
      @click="emit('ir', destino.vista)"
    >
      <Icono :nombre="destino.icono" />
      <span>{{ destino.nombre }}</span>
    </button>
  </nav>
</template>

<style scoped>
.barra {
  position: fixed;
  z-index: 10;
  left: 0;
  right: 0;
  bottom: 0;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  /* La zona inferior del iPhone queda debajo de los botones (RNF-007-06). */
  padding: 0 env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);
  border-top: 1px solid var(--linea);
  background: color-mix(in srgb, var(--superficie) 88%, transparent);
  -webkit-backdrop-filter: saturate(1.6) blur(18px);
  backdrop-filter: saturate(1.6) blur(18px);
}

.barra__destino {
  height: var(--alto-barra);
  display: grid;
  justify-items: center;
  align-content: center;
  gap: 2px;
  border: 0;
  background: none;
  color: var(--tinta-suave);
  font-size: 11px;
  line-height: 13px;
  font-weight: 500;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

.barra__destino--actual {
  color: var(--acento);
}

.barra__destino:focus-visible {
  outline-offset: -4px;
}
</style>
