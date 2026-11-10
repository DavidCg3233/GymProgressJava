<script setup>
// Un número con botones de menos y más, para cambiarlo con el pulgar (RNF-006-02).
// También se puede tocar el número y escribirlo.

const valor = defineModel({ type: [Number, String, null], default: null })

const props = defineProps({
  etiqueta: { type: String, required: true },
  paso: { type: Number, required: true },
  minimo: { type: Number, required: true },
  maximo: { type: Number, required: true },
  decimales: { type: Boolean, default: false },
})

function mover(direccion) {
  const actual = Number(String(valor.value ?? '').replace(',', '.'))
  const base = Number.isFinite(actual) && valor.value !== null && valor.value !== '' ? actual : props.minimo - props.paso
  const siguiente = Math.min(props.maximo, Math.max(props.minimo, base + direccion * props.paso))
  // Evita restos de coma flotante como 32.50000001.
  valor.value = Math.round(siguiente * 10) / 10
}
</script>

<template>
  <div class="paso">
    <button class="paso__boton" type="button" :aria-label="`Menos ${props.etiqueta}`" @click="mover(-1)">−</button>
    <label class="paso__centro">
      <input
        v-model="valor"
        class="paso__numero"
        type="text"
        :inputmode="props.decimales ? 'decimal' : 'numeric'"
        :aria-label="props.etiqueta"
        placeholder="–"
      />
      <span class="paso__unidad">{{ props.etiqueta }}</span>
    </label>
    <button class="paso__boton" type="button" :aria-label="`Más ${props.etiqueta}`" @click="mover(1)">+</button>
  </div>
</template>

<style scoped>
.paso {
  display: grid;
  grid-template-columns: var(--tamano-toque) minmax(0, 1fr) var(--tamano-toque);
  align-items: stretch;
  border: 1px solid var(--color-borde);
  border-radius: var(--radio);
  background: var(--color-superficie);
  overflow: hidden;
}

.paso__boton {
  min-height: var(--tamano-toque);
  border: 0;
  background: transparent;
  font-size: 1.375rem;
  line-height: 1;
  cursor: pointer;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}

.paso__boton:active {
  background: var(--color-borde);
}

.paso__centro {
  display: grid;
  justify-items: center;
  align-content: center;
  min-width: 0;
}

.paso__numero {
  width: 100%;
  border: 0;
  background: transparent;
  text-align: center;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  padding: 0;
}

.paso__unidad {
  font-size: 0.6875rem;
  color: var(--color-texto-suave);
  line-height: 1;
  padding-bottom: 0.2rem;
}
</style>
