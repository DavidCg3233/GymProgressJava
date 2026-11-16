<script setup>
// Historial de sesiones terminadas, y el detalle de una (T-006-29 · RF-006-09, 10, 15).
import { onMounted, ref } from 'vue'

import Encabezado from '../componentes/Encabezado.vue'
import GuardarComoRutina from '../componentes/GuardarComoRutina.vue'
import { cargarHistorial, cargarSesion, eliminarSesion } from '../estado/sesion.js'
import { NOMBRE_SESION_LIBRE } from '../reglas/textos.js'

// "volver" ya no se usa aquí (la barra inferior navega), pero App lo sigue escuchando.
defineEmits(['volver'])

const sesiones = ref([])
const pagina = ref(1)
const hayMas = ref(false)
const cargando = ref(true)
const error = ref('')

const abierta = ref(null)
// RF-008-06, 07: guardar la sesión abierta como rutina.
const guardandoComoRutina = ref(false)
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
    <Encabezado
      :titulo="abierta.nombre || NOMBRE_SESION_LIBRE"
      :subtitulo="`${fecha(abierta.inicio)} · ${hora(abierta.inicio)} a ${hora(abierta.fin)}`"
      atras="Historial"
      @atras="abierta = null; guardandoComoRutina = false"
    />

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

    <GuardarComoRutina
      v-if="guardandoComoRutina"
      :id-sesion="abierta.id"
      :nombre-sugerido="abierta.nombre || NOMBRE_SESION_LIBRE"
      @cerrar="guardandoComoRutina = false"
    />
    <button v-else class="boton boton--secundario boton--ancho" type="button" @click="guardandoComoRutina = true">
      Guardar como rutina
    </button>

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
    <!-- T-007-14: sin botón "Inicio": la barra de abajo lleva a todas partes. -->
    <Encabezado titulo="Historial" />

    <p v-if="error" class="mensaje mensaje--error" role="alert">{{ error }}</p>
    <p v-else-if="!cargando && sesiones.length === 0" class="suave">
      Aún no tienes sesiones terminadas. La primera aparecerá aquí.
    </p>

    <!-- T-007-14: la lista es un grupo de filas, como en Ajustes del iPhone. -->
    <ul v-if="sesiones.length" class="grupo">
      <li v-for="sesion in sesiones" :key="sesion.id">
        <button class="grupo__fila registro" type="button" @click="abrir(sesion.id)">
          <span class="grupo__texto">
            <strong>{{ sesion.nombre || NOMBRE_SESION_LIBRE }}</strong>
            <span class="suave">
              {{ fecha(sesion.inicio) }} · {{ sesion.ejercicios }} {{ sesion.ejercicios === 1 ? 'ejercicio' : 'ejercicios' }} ·
              {{ sesion.series }} {{ sesion.series === 1 ? 'serie' : 'series' }}
            </span>
          </span>
          <span class="registro__ir" aria-hidden="true">›</span>
        </button>
      </li>
    </ul>

    <button v-if="hayMas" class="boton boton--ancho" type="button" :disabled="cargando" @click="cargar(pagina + 1)">
      Ver más
    </button>
  </main>
</template>

<style scoped>
.registro__ir {
  font-size: 22px;
  color: var(--tinta-suave);
}

.series {
  margin: 0;
  padding-left: 1.5rem;
  display: grid;
  gap: var(--espacio-1);
  font-variant-numeric: tabular-nums;
}
</style>
