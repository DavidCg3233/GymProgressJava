<script setup>
// Evolución de un ejercicio (T-004-15 · RF-004-09 · RN-004-05, 06).
import { computed, onMounted, ref } from 'vue'

import Explicacion from '../componentes/Explicacion.vue'
import GraficaDeLinea from '../componentes/GraficaDeLinea.vue'
import { cargarEvolucion, mensajeDeProgreso } from '../estado/progreso.js'
import { EXPLICACIONES } from '../progreso/explicaciones.js'

const props = defineProps({ clave: { type: String, required: true }, nombre: { type: String, required: true } })
const emit = defineEmits(['volver'])

const datos = ref(null)
const error = ref('')
const modo = ref('pesada') // 'pesada' o 'volumen'

const kg = (valor) => `${String(Math.round(valor * 10) / 10).replace('.', ',')} kg`
const formatoDeFecha = new Intl.DateTimeFormat('es-CO', { day: 'numeric', month: 'short', year: 'numeric' })
const fecha = (dia) => formatoDeFecha.format(new Date(`${dia}T12:00:00`))

// Plan 004, regla nueva 2: en peso corporal se grafican repeticiones.
const formato = computed(() => (datos.value?.peso_corporal ? (valor) => `${valor} reps` : kg))

const valores = computed(() =>
  (datos.value?.puntos ?? []).map((punto) => {
    if (modo.value === 'volumen') return punto.volumen
    return datos.value.peso_corporal ? punto.reps_de_la_pesada : punto.pesada
  }),
)

const detalles = computed(() =>
  (datos.value?.puntos ?? []).map((punto) => {
    if (modo.value === 'volumen') return `${fecha(punto.fecha)} · volumen ${formato.value(punto.volumen)}`
    const serie = datos.value.peso_corporal ? 'peso corporal' : kg(punto.pesada)
    return `${fecha(punto.fecha)} · ${serie} × ${punto.reps_de_la_pesada}`
  }),
)

async function cargar() {
  error.value = ''
  try {
    datos.value = await cargarEvolucion(props.clave)
  } catch (fallo) {
    error.value = mensajeDeProgreso(fallo)
  }
}

onMounted(cargar)
</script>

<template>
  <main class="pantalla">
    <header class="fila fila--separada">
      <h1>{{ datos?.nombre ?? nombre }}</h1>
      <button class="boton boton--texto" type="button" @click="emit('volver')">Progreso</button>
    </header>

    <template v-if="error">
      <p class="mensaje mensaje--error" role="alert">{{ error }}</p>
      <button class="boton boton--ancho" type="button" @click="cargar">Reintentar</button>
    </template>

    <p v-else-if="!datos" class="suave">Cargando…</p>

    <section v-else class="tarjeta">
      <div class="selector" role="group" aria-label="Qué graficar">
        <button
          v-for="opcion in [
            { valor: 'pesada', texto: 'Serie más pesada' },
            { valor: 'volumen', texto: 'Volumen' },
          ]"
          :key="opcion.valor"
          class="selector__opcion"
          :class="{ 'selector__opcion--activa': modo === opcion.valor }"
          type="button"
          :aria-pressed="modo === opcion.valor"
          @click="modo = opcion.valor"
        >
          {{ opcion.texto }}
        </button>
      </div>
      <div class="fila">
        <Explicacion :texto="EXPLICACIONES[modo]" />
      </div>
      <GraficaDeLinea :valores="valores" :detalles="detalles" :formato="formato" />
      <p class="suave">{{ datos.puntos.length }} {{ datos.puntos.length === 1 ? 'sesión' : 'sesiones' }}</p>
    </section>
  </main>
</template>

<style scoped>
.fila {
  flex-wrap: wrap;
}

.selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border: 1px solid var(--linea);
  border-radius: var(--radio);
  overflow: hidden;
}

.selector__opcion {
  min-height: var(--tamano-toque);
  border: 0;
  background: var(--superficie);
  color: var(--tinta);
  cursor: pointer;
}

.selector__opcion--activa {
  background: var(--acento);
  color: var(--sobre-acento);
  font-weight: 600;
}
</style>
