<script setup>
// Editor de rutina (T-002-15 · RF-002-03, 04, 08, 09, 20 · RNF-002-01).
import { computed, reactive, ref } from 'vue'

import PasoNumerico from '../componentes/PasoNumerico.vue'
import { guardarEjercicio, guardarRutina } from '../estado/rutinas.js'
import { estado } from '../estado/sesion.js'
import { claveDeEjercicio } from '../reglas/ejercicios.js'
import {
  DIAS_DE_LA_SEMANA,
  NOMBRES_DE_LOS_DIAS,
  validarDias,
  validarEjerciciosDeRutina,
  validarNombreDeRutina,
  validarSeriesPrevistas,
} from '../reglas/rutinas.js'
import { validarPeso, validarRepeticiones } from '../reglas/series.js'

const props = defineProps({ rutinaId: { type: String, default: null } })
const emit = defineEmits(['listo', 'cancelar'])

const original = estado.rutinas.find((rutina) => rutina.id === props.rutinaId)

// Copia de trabajo: nada cambia en la rutina guardada hasta que el servidor acepte.
const formulario = reactive({
  nombre: original?.nombre ?? '',
  dias: [...(original?.dias ?? [])],
  ejercicios: (original?.ejercicios ?? []).map((previsto) => ({ ...previsto })),
})

const error = ref('')
const guardando = ref(false)

// --- Días -------------------------------------------------------------------

function alternarDia(dia) {
  formulario.dias = formulario.dias.includes(dia) ? formulario.dias.filter((d) => d !== dia) : [...formulario.dias, dia]
}

// --- Agregar ejercicio ------------------------------------------------------

const nombreNuevo = ref('')
const grupoNuevo = ref('')
const nombreDeGrupo = (id) => estado.catalogo.grupos.find((grupo) => grupo.id === id)?.nombre ?? ''
const delCatalogo = computed(() =>
  estado.catalogo.ejercicios.find((ejercicio) => claveDeEjercicio(ejercicio.nombre) === claveDeEjercicio(nombreNuevo.value)),
)

async function agregarEjercicio() {
  error.value = ''
  try {
    let ejercicio = delCatalogo.value
    if (!ejercicio) {
      // RF-002-09: no está en el catálogo, se crea con el grupo elegido.
      if (!grupoNuevo.value) {
        error.value = 'Elige el grupo muscular del ejercicio nuevo.'
        return
      }
      ejercicio = await guardarEjercicio({ nombre: nombreNuevo.value, grupo: grupoNuevo.value })
    }
    if (formulario.ejercicios.some((previsto) => previsto.ejercicio === ejercicio.id)) {
      error.value = 'Ese ejercicio ya está en la rutina.'
      return
    }
    formulario.ejercicios.push({
      ejercicio: ejercicio.id,
      nombre: ejercicio.nombre,
      grupo: nombreDeGrupo(ejercicio.grupo),
      series: 3,
      reps: 10,
      peso: 0,
    })
    nombreNuevo.value = ''
    grupoNuevo.value = ''
  } catch (fallo) {
    error.value = fallo.sinConexion ? 'Para crear un ejercicio necesitas conexión.' : fallo.mensaje
  }
}

// --- Ordenar y quitar (RF-002-20) -------------------------------------------

function mover(indice, desplazamiento) {
  const destino = indice + desplazamiento
  if (destino < 0 || destino >= formulario.ejercicios.length) return
  const lista = formulario.ejercicios
  ;[lista[indice], lista[destino]] = [lista[destino], lista[indice]]
}

function quitar(indice) {
  formulario.ejercicios.splice(indice, 1)
}

// --- Guardar ----------------------------------------------------------------

function validar() {
  // Las mismas reglas que el servidor, para avisar sin esperar a la red.
  validarNombreDeRutina(formulario.nombre)
  validarDias(formulario.dias)
  validarEjerciciosDeRutina(formulario.ejercicios.map((previsto) => previsto.ejercicio))
  return formulario.ejercicios.map((previsto) => ({
    ejercicio: previsto.ejercicio,
    series: validarSeriesPrevistas(Number(previsto.series)),
    reps: validarRepeticiones(previsto.reps),
    peso: validarPeso(previsto.peso),
  }))
}

async function guardar() {
  error.value = ''
  let ejercicios
  try {
    ejercicios = validar()
  } catch (fallo) {
    error.value = fallo.mensaje
    return
  }
  guardando.value = true
  try {
    await guardarRutina({ id: props.rutinaId ?? undefined, nombre: formulario.nombre, dias: formulario.dias, ejercicios })
    emit('listo')
  } catch (fallo) {
    // RNF-002-01: sin conexión se avisa y lo escrito se conserva.
    error.value = fallo.sinConexion ? 'Sin conexión: tus cambios siguen aquí. Guárdalos cuando vuelva la señal.' : fallo.mensaje
  } finally {
    guardando.value = false
  }
}
</script>

<template>
  <main class="pantalla">
    <header class="fila fila--separada">
      <h1>{{ props.rutinaId ? 'Editar rutina' : 'Nueva rutina' }}</h1>
      <button class="boton boton--texto" type="button" @click="emit('cancelar')">Cancelar</button>
    </header>

    <form class="tarjeta" @submit.prevent="guardar">
      <label class="campo">
        <span>Nombre</span>
        <input v-model="formulario.nombre" type="text" maxlength="50" placeholder="Ej.: Pecho" />
      </label>

      <fieldset class="dias">
        <legend class="suave">Días (opcional)</legend>
        <button
          v-for="dia in DIAS_DE_LA_SEMANA"
          :key="dia"
          class="dias__dia"
          :class="{ 'dias__dia--activo': formulario.dias.includes(dia) }"
          type="button"
          :aria-pressed="formulario.dias.includes(dia)"
          :aria-label="NOMBRES_DE_LOS_DIAS[dia - 1]"
          @click="alternarDia(dia)"
        >
          {{ NOMBRES_DE_LOS_DIAS[dia - 1].slice(0, 2) }}
        </button>
      </fieldset>

      <section v-for="(previsto, indice) in formulario.ejercicios" :key="previsto.ejercicio" class="previsto">
        <div class="fila fila--separada">
          <div>
            <strong>{{ indice + 1 }}. {{ previsto.nombre }}</strong>
            <p class="suave">{{ previsto.grupo }}</p>
          </div>
          <div class="fila">
            <button class="boton boton--texto" type="button" :aria-label="`Subir ${previsto.nombre}`" :disabled="indice === 0" @click="mover(indice, -1)">↑</button>
            <button
              class="boton boton--texto"
              type="button"
              :aria-label="`Bajar ${previsto.nombre}`"
              :disabled="indice === formulario.ejercicios.length - 1"
              @click="mover(indice, 1)"
            >
              ↓
            </button>
            <button class="boton boton--texto" type="button" :aria-label="`Quitar ${previsto.nombre}`" @click="quitar(indice)">✕</button>
          </div>
        </div>
        <div class="previsto__valores">
          <PasoNumerico v-model="previsto.series" etiqueta="series" :paso="1" :minimo="1" :maximo="10" />
          <PasoNumerico v-model="previsto.reps" etiqueta="reps" :paso="1" :minimo="1" :maximo="100" />
          <PasoNumerico v-model="previsto.peso" etiqueta="kg" :paso="0.5" :minimo="0" :maximo="500" decimales />
        </div>
      </section>

      <div class="tarjeta">
        <label class="campo">
          <span>Agregar ejercicio</span>
          <input v-model="nombreNuevo" type="text" list="catalogo-editor" maxlength="50" autocomplete="off" placeholder="Busca en tu catálogo" />
          <datalist id="catalogo-editor">
            <option v-for="ejercicio in estado.catalogo.ejercicios" :key="ejercicio.id" :value="ejercicio.nombre">
              {{ nombreDeGrupo(ejercicio.grupo) }}
            </option>
          </datalist>
        </label>
        <label v-if="nombreNuevo.trim() && !delCatalogo" class="campo">
          <span>Es nuevo: elige su grupo muscular</span>
          <select v-model="grupoNuevo">
            <option value="" disabled>Elige uno</option>
            <option v-for="grupo in estado.catalogo.grupos" :key="grupo.id" :value="grupo.id">{{ grupo.nombre }}</option>
          </select>
        </label>
        <button class="boton" type="button" :disabled="!nombreNuevo.trim()" @click="agregarEjercicio">Agregar</button>
      </div>

      <p v-if="error" class="mensaje mensaje--error" role="alert">{{ error }}</p>

      <button class="boton boton--principal boton--ancho" type="submit" :disabled="guardando">
        {{ guardando ? 'Guardando…' : 'Guardar rutina' }}
      </button>
    </form>
  </main>
</template>

<style scoped>
.dias {
  border: 0;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: var(--espacio-1);
}

.dias legend {
  margin-bottom: var(--espacio-2);
}

.dias__dia {
  min-height: var(--tamano-toque);
  border: 1px solid var(--color-borde);
  border-radius: var(--radio);
  background: var(--color-superficie);
  cursor: pointer;
  touch-action: manipulation;
}

.dias__dia--activo {
  background: var(--color-acento);
  border-color: var(--color-acento);
  color: var(--color-sobre-acento);
  font-weight: 600;
}

.previsto {
  display: grid;
  gap: var(--espacio-2);
  padding-bottom: var(--espacio-3);
  border-bottom: 1px solid var(--color-borde);
}

.previsto__valores {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--espacio-2);
}
</style>
