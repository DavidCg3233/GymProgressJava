<script setup>
// RNF-004-03: al tocar "?", una frase que explica cómo se calcula el indicador.
import { ref } from 'vue'

defineProps({ texto: { type: String, required: true } })

const abierta = ref(false)
</script>

<template>
  <button class="explicacion__boton" type="button" :aria-expanded="abierta" aria-label="Cómo se calcula" @click="abierta = !abierta">?</button>
  <p v-if="abierta" class="explicacion__texto suave">{{ texto }}</p>
</template>

<style scoped>
.explicacion__boton {
  width: 1.75rem;
  height: 1.75rem;
  border: 1px solid var(--color-borde);
  border-radius: 50%;
  background: var(--color-superficie);
  color: var(--color-texto-suave);
  font-weight: 600;
  cursor: pointer;
  flex: none;
}

.explicacion__texto {
  flex-basis: 100%;
  margin: 0;
  font-size: 0.875rem;
}
</style>
