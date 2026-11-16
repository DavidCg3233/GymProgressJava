<script setup>
// Un número con botones de menos y más, para cambiarlo con el pulgar (RNF-006-02).
// También se puede tocar el número y escribirlo.
//
// Es un control unido (T-007-10 · RNF-007-02 · DESIGN.md): "− número +" como el
// control de +/− del iPhone. Sus tres partes miden 44 de alto y se tocan por
// dentro; el aire de 8 px va entre controles.
import { computed } from 'vue'

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

// El número se muestra con coma decimal, como se escribe en Colombia ("38,5").
// Lo escrito se guarda tal cual: las reglas aceptan coma o punto (RF-006-24).
const mostrado = computed(() => (valor.value === null || valor.value === undefined ? '' : String(valor.value).replace('.', ',')))

// CA-007-05a: el número se ve completo. Con 5 caracteres ("472,5") baja a 16 px,
// nunca menos: con menos de 16 px Safari hace zoom al tocar el campo.
const largo = computed(() => mostrado.value.length >= 5)
</script>

<template>
  <div class="paso" data-control-unido>
    <button class="paso__boton" type="button" :aria-label="`Menos ${props.etiqueta}`" @click="mover(-1)">−</button>
    <label class="paso__centro">
      <input
        :value="mostrado"
        class="paso__numero"
        :class="{ 'paso__numero--largo': largo }"
        type="text"
        :inputmode="props.decimales ? 'decimal' : 'numeric'"
        :aria-label="props.etiqueta"
        placeholder="–"
        @input="valor = $event.target.value"
      />
      <span class="paso__unidad" aria-hidden="true">{{ props.etiqueta }}</span>
    </label>
    <button class="paso__boton" type="button" :aria-label="`Más ${props.etiqueta}`" @click="mover(1)">+</button>
  </div>
</template>

<style scoped>
.paso {
  display: grid;
  grid-template-columns: var(--tamano-toque) minmax(var(--tamano-toque), 1fr) var(--tamano-toque);
  align-items: stretch;
  min-height: var(--tamano-toque);
  border-radius: var(--radio);
  background: var(--superficie-2);
  overflow: hidden;
}

.paso__boton {
  min-height: var(--tamano-toque);
  border: 0;
  background: transparent;
  color: var(--tinta);
  font-size: 1.375rem;
  line-height: 1;
  cursor: pointer;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}

.paso__boton:active {
  background: var(--linea);
}

/* El número: toda la celda del centro se toca para escribirlo. */
.paso__centro {
  position: relative;
  display: grid;
  min-width: 0;
  background: var(--superficie);
}

.paso__numero {
  width: 100%;
  height: 100%;
  min-height: var(--tamano-toque);
  border: 0;
  background: transparent;
  text-align: center;
  font-size: 20px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.01em;
  padding: 0 0 10px;
}

.paso__numero--largo {
  font-size: 16px;
}

/* La unidad va debajo del número, sin ocupar ancho. */
.paso__unidad {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 3px;
  text-align: center;
  font-size: 10px;
  line-height: 1;
  color: var(--tinta-suave);
  pointer-events: none;
}
</style>
