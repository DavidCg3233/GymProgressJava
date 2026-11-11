<script setup>
// Franja de la sesión en curso (T-007-07 · RF-007-03 · RN-007-02 · DESIGN.md, sección 5).
// Va sobre la barra inferior y abre la sesión en un toque.
import { computed, onUnmounted, ref } from 'vue'

import { tiempoDeSesion } from '../navegacion/tiempo.js'
import Icono from './Icono.vue'

const props = defineProps({
  sesion: { type: Object, required: true },
})
const emit = defineEmits(['abrir'])

// RN-007-02: el tiempo se recalcula al menos cada minuto.
const ahora = ref(new Date())
const reloj = setInterval(() => {
  ahora.value = new Date()
}, 30_000)
onUnmounted(() => clearInterval(reloj))

const nombre = computed(() => props.sesion.nombre || 'Sesión libre')
const tiempo = computed(() => tiempoDeSesion(props.sesion.inicio, ahora.value))
</script>

<template>
  <button class="franja" type="button" :aria-label="`Continuar sesión: ${nombre}, ${tiempo}`" @click="emit('abrir')">
    <span class="franja__punto" aria-hidden="true" />
    <span class="franja__texto">{{ nombre }} · <span class="numeros">{{ tiempo }}</span></span>
    <Icono nombre="derecha" :tamano="20" />
  </button>
</template>

<style scoped>
.franja {
  position: fixed;
  z-index: 10;
  left: calc(var(--espacio-2) + env(safe-area-inset-left));
  right: calc(var(--espacio-2) + env(safe-area-inset-right));
  bottom: calc(var(--alto-barra) + env(safe-area-inset-bottom) + var(--espacio-2));
  height: var(--alto-franja);
  max-width: 34rem;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: var(--espacio-3);
  padding: 0 var(--espacio-3) 0 var(--espacio-4);
  border: 0;
  border-radius: calc(var(--alto-franja) / 2);
  background: var(--acento-tinte);
  color: var(--tinta);
  font-size: 15px;
  font-weight: 600;
  text-align: left;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.franja__punto {
  width: 8px;
  height: 8px;
  flex: none;
  border-radius: 50%;
  background: var(--acento);
}

.franja__texto {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.franja .icono {
  color: var(--acento);
}
</style>
