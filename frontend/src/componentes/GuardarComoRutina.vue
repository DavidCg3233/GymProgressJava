<script setup>
// Guardar una sesión como rutina (T-008-14 · RF-008-06, 07 · RN-008-05 a 07 · RNF-008-03).
//
// Primero se ve la vista previa de los cambios (calculada por el servidor, igual
// a lo que se guardará); solo al confirmar se guarda.
import { computed, ref, watch } from 'vue'

import { sesionARutina } from '../estado/rutinas.js'
import { estado } from '../estado/sesion.js'
import { DIAS_DE_LA_SEMANA, NOMBRES_DE_LOS_DIAS } from '../reglas/rutinas.js'

const props = defineProps({
  idSesion: { type: String, required: true },
  // RN-008-06: se propone el nombre de la sesión, salvo "Sesión libre".
  nombreSugerido: { type: String, default: '' },
})
const emit = defineEmits(['cerrar', 'guardada'])

const modo = ref('nueva') // 'nueva' o 'actualizar'
const nombre = ref(props.nombreSugerido === 'Sesión libre' ? '' : props.nombreSugerido)
const dias = ref([])
const rutinaElegida = ref(estado.rutinas[0]?.id ?? '')

const cambios = ref(null)
const error = ref('')
const ocupado = ref(false)
const guardada = ref(null)

const kg = (valores) => `${valores.peso === 0 ? 'peso corporal' : `${String(valores.peso).replace('.', ',')} kg`} × ${valores.reps}`
const DESCRIPCION = {
  agrega: (c) => `Se agrega: ${c.series} ${c.series === 1 ? 'serie' : 'series'} de ${kg(c.despues)}`,
  mejora: (c) => `Mejora: de ${kg(c.antes)} a ${kg(c.despues)}`,
  igual: () => 'Queda igual',
}

const datos = (confirmar) =>
  modo.value === 'nueva'
    ? { modo: 'nueva', id_rutina: crypto.randomUUID(), nombre: nombre.value, dias: dias.value, confirmar }
    : { modo: 'actualizar', rutina: rutinaElegida.value, confirmar }

function mensajeDe(fallo) {
  return fallo.sinConexion || fallo.estado >= 500
    ? 'Para guardar la sesión como rutina necesitas conexión. Lo que elegiste sigue aquí.'
    : fallo.mensaje
}

async function verCambios() {
  error.value = ''
  cambios.value = null
  if (modo.value === 'actualizar' && !rutinaElegida.value) {
    return
  }
  ocupado.value = true
  try {
    cambios.value = (await sesionARutina(props.idSesion, datos(false))).cambios
  } catch (fallo) {
    error.value = mensajeDe(fallo)
  } finally {
    ocupado.value = false
  }
}

async function guardar() {
  error.value = ''
  ocupado.value = true
  try {
    const { rutina } = await sesionARutina(props.idSesion, datos(true))
    guardada.value = rutina
    emit('guardada', rutina)
  } catch (fallo) {
    error.value = mensajeDe(fallo)
  } finally {
    ocupado.value = false
  }
}

function alternarDia(dia) {
  dias.value = dias.value.includes(dia) ? dias.value.filter((d) => d !== dia) : [...dias.value, dia]
}

watch([modo, rutinaElegida], verCambios, { immediate: true })

const puedeGuardar = computed(
  () => !ocupado.value && cambios.value && (modo.value === 'nueva' ? nombre.value.trim() : rutinaElegida.value),
)
</script>

<template>
  <section class="tarjeta guardar" aria-label="Guardar como rutina">
    <header class="fila fila--separada">
      <h2>Guardar como rutina</h2>
      <button class="boton boton--texto" type="button" @click="emit('cerrar')">Cerrar</button>
    </header>

    <p v-if="guardada" class="guardar__listo" role="status">
      Listo: "{{ guardada.nombre }}" quedó en tus rutinas.
    </p>

    <template v-else>
      <div class="guardar__modos" role="group" aria-label="Qué hacer con la sesión">
        <button
          class="guardar__modo"
          :class="{ 'guardar__modo--activo': modo === 'nueva' }"
          type="button"
          :aria-pressed="modo === 'nueva'"
          @click="modo = 'nueva'"
        >
          Rutina nueva
        </button>
        <button
          class="guardar__modo"
          :class="{ 'guardar__modo--activo': modo === 'actualizar' }"
          type="button"
          :aria-pressed="modo === 'actualizar'"
          :disabled="estado.rutinas.length === 0"
          @click="modo = 'actualizar'"
        >
          Actualizar una
        </button>
      </div>

      <template v-if="modo === 'nueva'">
        <label class="campo">
          <span>Nombre</span>
          <input v-model="nombre" type="text" maxlength="50" placeholder="Ej.: Pierna B" />
        </label>
        <fieldset class="guardar__dias">
          <legend class="suave">Días (opcional)</legend>
          <button
            v-for="dia in DIAS_DE_LA_SEMANA"
            :key="dia"
            class="guardar__dia"
            :class="{ 'guardar__dia--activo': dias.includes(dia) }"
            type="button"
            :aria-pressed="dias.includes(dia)"
            :aria-label="NOMBRES_DE_LOS_DIAS[dia - 1]"
            @click="alternarDia(dia)"
          >
            {{ NOMBRES_DE_LOS_DIAS[dia - 1].slice(0, 2) }}
          </button>
        </fieldset>
      </template>

      <label v-else class="campo">
        <span>Rutina</span>
        <select v-model="rutinaElegida">
          <option v-for="rutina in estado.rutinas" :key="rutina.id" :value="rutina.id">{{ rutina.nombre }}</option>
        </select>
      </label>

      <!-- RF-008-07: antes de guardar se ve exactamente qué va a cambiar. -->
      <p v-if="ocupado && !cambios" class="suave">Calculando…</p>
      <ul v-if="cambios" class="guardar__cambios" aria-label="Cambios">
        <li v-for="cambio in cambios" :key="cambio.nombre" :class="`guardar__cambio--${cambio.tipo}`">
          <strong>{{ cambio.nombre }}</strong>
          <span class="suave">{{ DESCRIPCION[cambio.tipo](cambio) }}</span>
        </li>
      </ul>
      <p v-if="modo === 'actualizar' && cambios" class="suave">Ningún ejercicio se quita de la rutina.</p>

      <p v-if="error" class="mensaje mensaje--error" role="alert">{{ error }}</p>

      <button class="boton boton--principal boton--ancho" type="button" :disabled="!puedeGuardar" @click="guardar">
        {{ ocupado && cambios ? 'Guardando…' : modo === 'nueva' ? 'Guardar rutina' : 'Actualizar rutina' }}
      </button>
    </template>
  </section>
</template>

<style scoped>
.guardar__modos {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border-radius: var(--radio);
  background: var(--superficie-2);
  padding: 3px;
  gap: 3px;
}

.guardar__modo {
  min-height: var(--tamano-toque);
  border: 0;
  border-radius: calc(var(--radio) - 3px);
  background: transparent;
  color: var(--tinta);
  font-weight: 500;
  cursor: pointer;
}

.guardar__modo--activo {
  background: var(--superficie);
  font-weight: 600;
}

.guardar__modo:disabled {
  opacity: 0.45;
}

.guardar__dias {
  border: 0;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: var(--espacio-1);
}

.guardar__dias legend {
  margin-bottom: var(--espacio-2);
}

.guardar__dia {
  min-height: var(--tamano-toque);
  border: 0;
  border-radius: var(--radio);
  background: var(--superficie-2);
  color: var(--tinta);
  cursor: pointer;
}

.guardar__dia--activo {
  background: var(--acento);
  color: var(--sobre-acento);
  font-weight: 600;
}

.guardar__cambios {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--espacio-2);
}

.guardar__cambios li {
  display: grid;
  gap: 2px;
  padding-left: var(--espacio-3);
  border-left: 3px solid var(--linea);
}

.guardar__cambio--agrega,
.guardar__cambio--mejora {
  border-left-color: var(--dorado) !important;
}

.guardar__listo {
  font-weight: 600;
  color: var(--dorado);
}
</style>
