<script setup>
// Historial de sesiones terminadas, y el detalle de una (T-006-29 · RF-006-09, 10, 15).
import { onMounted, ref } from 'vue'

import { cargarHistorial, cargarSesion, eliminarSesion } from '../estado/sesion.js'

const emit = defineEmits(['volver'])

const sesiones = ref([])
const pagina = ref(1)
const hayMas = ref(false)
const cargando = ref(true)
const error = ref('')

const abierta = ref(null)
const confirmandoEliminar = ref(false)

const formatoDeFecha = new Intl.DateTimeFormat('es-CO', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })
const formatoDeHora = new Intl.DateTimeFormat('es-CO', { hour: 'numeric', minute: '2-digit' })
const fecha = (iso) => formatoDeFecha.format(new Date(iso))
const hora = (iso) => formatoDeHora.format(new Date(iso))
const peso = (kg) => (kg === 0 ? 'peso corporal' : `${String(kg).replace('.', ',')} kg`)

async function intentar(accion) {
  error.value = ''
  cargando.value = true
  try {
    await accion()
  } catch (fallo) {
    error.value = fallo.sinConexion ? 'El historial necesita conexión.' : fallo.mensaje
  } finally {
    cargando.value = false
  }
}

function cargar(numero) {
  return intentar(async () => {
    const datos = await cargarHistorial(numero)
    sesiones.value = numero === 1 ? datos.sesiones : [...sesiones.value, ...datos.sesiones]
    hayMas.value = datos.hay_mas
    pagina.value = numero
  })
}

function abrir(id) {
  return intentar(async () => {
    abierta.value = await cargarSesion(id)
    confirmandoEliminar.value = false
  })
}

function eliminar() {
  return intentar(async () => {
    await eliminarSesion(abierta.value.id)
    abierta.value = null
    await cargar(1)
  })
}

onMounted(() => cargar(1))
</script>

<template>
  <!-- Detalle de una sesión: solo lectura (RF-006-14). -->
  <main v-if="abierta" class="pantalla">
    <header class="fila fila--separada">
      <div>
        <h1>{{ abierta.nombre }}</h1>
        <p class="suave">{{ fecha(abierta.inicio) }} · {{ hora(abierta.inicio) }} a {{ hora(abierta.fin) }}</p>
      </div>
      <button class="boton boton--texto" type="button" @click="abierta = null">Volver</button>
    </header>

    <p v-if="abierta.nota" class="mensaje mensaje--aviso">“{{ abierta.nota }}”</p>

    <section v-for="ejercicio in abierta.ejercicios" :key="ejercicio.id" class="tarjeta">
      <header>
        <h2>{{ ejercicio.nombre }}</h2>
        <p class="suave">{{ ejercicio.grupo }}</p>
      </header>
      <ol class="series">
        <li v-for="serie in ejercicio.series.filter((s) => s.confirmada)" :key="serie.id">
          {{ peso(serie.peso) }} × {{ serie.reps }}
        </li>
      </ol>
      <p v-if="ejercicio.nota" class="suave">Nota: “{{ ejercicio.nota }}”</p>
    </section>

    <p v-if="error" class="mensaje mensaje--error" role="alert">{{ error }}</p>

    <!-- RNF-USA-04: eliminar no se puede deshacer, así que se confirma. -->
    <section v-if="confirmandoEliminar" class="tarjeta">
      <p>¿Eliminar esta sesión? No se puede deshacer y dejará de contar para tu progreso.</p>
      <div class="fila">
        <button class="boton boton--peligro" type="button" :disabled="cargando" @click="eliminar">Sí, eliminar</button>
        <button class="boton boton--texto" type="button" @click="confirmandoEliminar = false">Cancelar</button>
      </div>
    </section>
    <button v-else class="boton boton--peligro boton--ancho" type="button" @click="confirmandoEliminar = true">
      Eliminar sesión
    </button>
  </main>

  <main v-else class="pantalla">
    <header class="fila fila--separada">
      <h1>Historial</h1>
      <button class="boton boton--texto" type="button" @click="emit('volver')">Inicio</button>
    </header>

    <p v-if="error" class="mensaje mensaje--error" role="alert">{{ error }}</p>
    <p v-else-if="!cargando && sesiones.length === 0" class="suave">
      Aún no tienes sesiones terminadas. La primera aparecerá aquí.
    </p>

    <button v-for="sesion in sesiones" :key="sesion.id" class="tarjeta registro" type="button" @click="abrir(sesion.id)">
      <strong>{{ sesion.nombre }}</strong>
      <span class="suave">
        {{ fecha(sesion.inicio) }} · {{ sesion.ejercicios }} {{ sesion.ejercicios === 1 ? 'ejercicio' : 'ejercicios' }} ·
        {{ sesion.series }} {{ sesion.series === 1 ? 'serie' : 'series' }}
      </span>
    </button>

    <button v-if="hayMas" class="boton boton--ancho" type="button" :disabled="cargando" @click="cargar(pagina + 1)">
      Ver más
    </button>
  </main>
</template>

<style scoped>
.registro {
  width: 100%;
  text-align: left;
  cursor: pointer;
  gap: var(--espacio-1);
}

.series {
  margin: 0;
  padding-left: 1.5rem;
  display: grid;
  gap: var(--espacio-1);
  font-variant-numeric: tabular-nums;
}
</style>
