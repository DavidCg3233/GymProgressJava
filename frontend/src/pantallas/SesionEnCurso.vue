<script setup>
// La sesión de entrenamiento en curso (T-006-23 a T-006-28).
import { computed, ref, watch } from 'vue'

import BuscadorDeEjercicio from '../componentes/BuscadorDeEjercicio.vue'
import EstadoDeSincronizacion from '../componentes/EstadoDeSincronizacion.vue'
import TarjetaDeEjercicio from '../componentes/TarjetaDeEjercicio.vue'
import { agregarEjercicio, estado, terminarSesion } from '../estado/sesion.js'
import { claveDeEjercicio } from '../reglas/ejercicios.js'
import { LARGO_MAXIMO_NOMBRE, LARGO_MAXIMO_NOTA } from '../reglas/textos.js'
import { seriesConfirmadas } from '../sesion/modelo.js'

const emit = defineEmits(['volver'])

// Grupos de la lista predefinida de la spec 002. Con el catálogo propio (hito B) saldrán de ahí.
// RF-002-08: los grupos y las sugerencias salen del catálogo propio, guardado en el celular.
const grupos = computed(() => estado.catalogo.grupos.map((g) => g.nombre))
const nombreDeGrupo = (id) => estado.catalogo.grupos.find((g) => g.id === id)?.nombre ?? ''

const sesion = computed(() => estado.sesion)
const confirmadas = computed(() => (sesion.value ? seriesConfirmadas(sesion.value) : 0))

// --- Agregar ejercicio ---
const agregando = ref(false)
const nombre = ref('')
const grupo = ref('')
const errorDeEjercicio = ref('')

// Ejercicios del catálogo: se sugieren al escribir y traen su grupo (RF-008-10).
const conocidos = computed(() =>
  estado.catalogo.ejercicios.map((ejercicio) => {
    const nombreDelGrupo = nombreDeGrupo(ejercicio.grupo)
    return { nombre: ejercicio.nombre, grupo: nombreDelGrupo, detalle: nombreDelGrupo }
  }),
)

// Si lo escrito ya es un ejercicio conocido, se pone su grupo.
watch(nombre, alEscribirNombre)

function alEscribirNombre() {
  const clave = claveDeEjercicio(nombre.value)
  const conocido = conocidos.value.find((c) => claveDeEjercicio(c.nombre) === clave) ?? estado.ultimaVez[clave]
  if (conocido) {
    grupo.value = conocido.grupo
  }
}

function guardarEjercicio() {
  errorDeEjercicio.value = ''
  try {
    agregarEjercicio(nombre.value, grupo.value)
    nombre.value = ''
    grupo.value = ''
    agregando.value = false
  } catch (fallo) {
    errorDeEjercicio.value = fallo.mensaje
  }
}

// --- Terminar ---
const terminando = ref(false)
const nombreDeSesion = ref('')
const nota = ref('')
const errorAlTerminar = ref('')
const enviando = ref(false)

async function terminar() {
  errorAlTerminar.value = ''
  enviando.value = true
  try {
    await terminarSesion(nombreDeSesion.value, nota.value)
  } catch (fallo) {
    errorAlTerminar.value = fallo.mensaje
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <main v-if="sesion" class="pantalla">
    <header class="fila fila--separada">
      <div>
        <h1>Sesión en curso</h1>
        <p class="suave">{{ confirmadas }} {{ confirmadas === 1 ? 'serie confirmada' : 'series confirmadas' }}</p>
      </div>
      <!-- RF-007-02: la sesión sigue; se ve en la franja sobre la barra. -->
      <button class="boton boton--texto" type="button" @click="emit('volver')">Minimizar</button>
    </header>

    <EstadoDeSincronizacion />

    <TarjetaDeEjercicio v-for="ejercicio in sesion.ejercicios" :key="ejercicio.id" :ejercicio="ejercicio" />

    <p v-if="sesion.ejercicios.length === 0 && !agregando" class="suave">
      Aún no hay ejercicios. Agrega el primero para empezar a registrar.
    </p>

    <form v-if="agregando" class="tarjeta" @submit.prevent="guardarEjercicio">
      <h2>Nuevo ejercicio</h2>
      <BuscadorDeEjercicio v-model="nombre" :opciones="conocidos" @elegir="(conocido) => (grupo = conocido.grupo)" />
      <label class="campo">
        <span>Grupo muscular</span>
        <select v-model="grupo">
          <option value="" disabled>Elige uno</option>
          <option v-for="opcion in grupos" :key="opcion" :value="opcion">{{ opcion }}</option>
          <option v-if="grupo && !grupos.includes(grupo)" :value="grupo">{{ grupo }}</option>
        </select>
      </label>
      <p v-if="errorDeEjercicio" class="mensaje mensaje--error" role="alert">{{ errorDeEjercicio }}</p>
      <div class="fila">
        <button class="boton boton--principal" type="submit">Agregar</button>
        <button class="boton boton--texto" type="button" @click="agregando = false">Cancelar</button>
      </div>
    </form>
    <button v-else class="boton boton--ancho" type="button" @click="agregando = true">+ Ejercicio</button>

    <form v-if="terminando" class="tarjeta" @submit.prevent="terminar">
      <h2>Terminar sesión</h2>
      <p v-if="confirmadas === 0" class="mensaje mensaje--aviso">
        No confirmaste ninguna serie: esta sesión se descartará y no quedará en tu historial.
      </p>
      <template v-else>
        <label class="campo">
          <span>Nombre (opcional)</span>
          <input v-model="nombreDeSesion" type="text" :maxlength="LARGO_MAXIMO_NOMBRE" placeholder="Sesión libre" />
        </label>
        <label class="campo">
          <span>Nota (opcional)</span>
          <textarea v-model="nota" rows="2" :maxlength="LARGO_MAXIMO_NOTA" placeholder="¿Cómo te fue?"></textarea>
        </label>
      </template>
      <p v-if="errorAlTerminar" class="mensaje mensaje--error" role="alert">{{ errorAlTerminar }}</p>
      <div class="fila">
        <button class="boton boton--principal" type="submit" :disabled="enviando">
          {{ confirmadas === 0 ? 'Descartar sesión' : 'Terminar' }}
        </button>
        <button class="boton boton--texto" type="button" @click="terminando = false">Seguir entrenando</button>
      </div>
    </form>
    <button v-else class="boton boton--principal boton--ancho" type="button" @click="terminando = true">
      Terminar sesión
    </button>
  </main>
</template>
