<script setup>
// RNF-004-03: al tocar "?", una frase que explica cómo se calcula el indicador.
import { ref } from 'vue'

defineProps({ texto: { type: String, required: true } })

const abierta = ref(false)
</script>

<template>
  <button class="explicacion__boton" type="button" :aria-expanded="abierta" aria-label="Cómo se calcula" @click="abierta = !abierta">
    <span class="explicacion__circulo" aria-hidden="true">?</span>
  </button>
  <p v-if="abierta" class="explicacion__texto suave">{{ texto }}</p>
</template>

<style scoped>
/* RNF-007-02: el círculo se ve de 28 px, pero se toca en 44 × 44. */
.explicacion__boton {
  display: grid;
  place-items: center;
  width: var(--tamano-toque);
  height: var(--tamano-toque);
  margin: calc((28px - var(--tamano-toque)) / 2);
  padding: 0;
  border: 0;
  background: transparent;
  cursor: pointer;
  flex: none;
}

.explicacion__circulo {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border: 1px solid var(--linea);
  border-radius: 50%;
  background: var(--superficie);
  color: var(--tinta-suave);
  font-weight: 600;
}

.explicacion__texto {
  flex-basis: 100%;
  margin: 0;
  font-size: 0.875rem;
}
</style>
