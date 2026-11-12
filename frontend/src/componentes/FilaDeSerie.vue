<script setup>
// Una serie: peso, repeticiones y el botón para confirmarla.
// Confirmar sin cambios es 1 toque; cambiando un valor, 2 (RNF-006-01, RNF-006-02).
import { computed, ref, watch } from 'vue'

import { confirmarSerie, quitarSerie } from '../estado/sesion.js'
import PasoNumerico from './PasoNumerico.vue'

const props = defineProps({
  ejercicio: { type: Object, required: true },
  serie: { type: Object, required: true },
})

// Lo que se ve en pantalla mientras se edita. Solo pasa a la serie al confirmar.
const peso = ref(props.serie.peso)
const reps = ref(props.serie.reps)
const error = ref('')

watch(
  () => [props.serie.peso, props.serie.reps],
  ([nuevoPeso, nuevasReps]) => {
    peso.value = nuevoPeso
    reps.value = nuevasReps
  },
)

const aNumero = (valor) => Number(String(valor ?? '').replace(',', '.'))

// RF-006-06: una serie confirmada cuyos valores se tocaron vuelve a verse como pendiente.
const cambiada = computed(() => aNumero(peso.value) !== props.serie.peso || aNumero(reps.value) !== props.serie.reps)
const hecha = computed(() => props.serie.confirmada && !cambiada.value)

const ORIGENES = {
  'ultima-vez': 'última vez',
  'serie-anterior': 'igual a la anterior',
  rutina: 'de la rutina',
}
const origen = computed(() => (props.serie.confirmada ? '' : (ORIGENES[props.serie.origen] ?? '')))

function confirmar() {
  error.value = ''
  try {
    confirmarSerie(props.ejercicio, props.serie, { peso: peso.value, reps: reps.value })
  } catch (fallo) {
    // RF-006-24: se conserva lo escrito y se muestra el rango permitido.
    error.value = fallo.mensaje
  }
}
</script>

<template>
  <div class="serie" :class="{ 'serie--hecha': hecha }">
    <div class="serie__fila">
      <span class="serie__numero" aria-hidden="true">{{ props.serie.numero }}</span>

      <PasoNumerico v-model="peso" etiqueta="kg" :paso="0.5" :minimo="0" :maximo="500" decimales />
      <PasoNumerico v-model="reps" etiqueta="reps" :paso="1" :minimo="1" :maximo="100" />

      <button
        class="serie__confirmar"
        type="button"
        :aria-label="hecha ? `Serie ${props.serie.numero} confirmada` : `Confirmar serie ${props.serie.numero}`"
        :aria-pressed="hecha"
        @click="confirmar"
      >
        ✓
      </button>
    </div>

    <div class="serie__pie">
      <span class="suave">{{ hecha ? 'Confirmada' : props.serie.confirmada ? 'Cambiada: confirma de nuevo' : origen }}</span>
      <button class="boton boton--texto serie__quitar" type="button" @click="quitarSerie(props.ejercicio, props.serie)">
        Quitar
      </button>
    </div>

    <p v-if="error" class="mensaje mensaje--error" role="alert">{{ error }}</p>
  </div>
</template>

<style scoped>
.serie {
  display: grid;
  gap: var(--espacio-1);
  padding: var(--espacio-2);
  border-radius: var(--radio);
  border: 1px solid transparent;
}

.serie--hecha {
  background: var(--dorado-tinte);
}

.serie__fila {
  display: grid;
  grid-template-columns: 1.25rem minmax(0, 1fr) minmax(0, 1fr) var(--tamano-toque);
  gap: var(--espacio-2);
  align-items: center;
}

.serie__numero {
  text-align: center;
  font-weight: 600;
  color: var(--tinta-suave);
}

.serie__confirmar {
  width: var(--tamano-toque);
  height: var(--tamano-toque);
  border-radius: 50%;
  border: 2px solid var(--acento);
  background: transparent;
  color: var(--acento);
  font-size: 1.25rem;
  font-weight: 700;
  cursor: pointer;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}

.serie--hecha .serie__confirmar {
  border-color: var(--dorado);
  background: var(--dorado);
  color: var(--sobre-dorado);
}

.serie__pie {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-left: calc(1.25rem + var(--espacio-2));
  min-height: 1.75rem;
}

.serie__quitar {
  min-height: 1.75rem;
  font-size: 0.875rem;
  color: var(--tinta-suave);
}
</style>
