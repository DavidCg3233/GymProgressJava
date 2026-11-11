<script setup>
// Peso corporal (T-003-11 a 13 · RF-003-01 a 13 · RN-003-09 · RNF-003-01, 02 · RNF-USA-04).
// Todo pide conexión: si falta, se dice y lo escrito se queda en su campo.
import { computed, onMounted, ref } from 'vue'

import GraficaDeLinea from '../componentes/GraficaDeLinea.vue'
import { cargarPeso, eliminarPeso, fijarEstatura, fijarObjetivo, mensajeDePeso, registrarPeso } from '../estado/cuerpo.js'
import { fechaLocal } from '../reglas/progreso.js'

const HOY = fechaLocal(new Date())

const datos = ref(null)
const errorDeCarga = ref('')
const error = ref('')
const ocupado = ref(false)

const kg = (valor) => `${Number(valor).toFixed(1).replace('.', ',')} kg`
const formatoDeFecha = new Intl.DateTimeFormat('es-CO', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })
const formatoCorto = new Intl.DateTimeFormat('es-CO', { day: 'numeric', month: 'short' })
const fecha = (dia) => formatoDeFecha.format(new Date(`${dia}T12:00:00`))
const fechaCorta = (dia) => formatoCorto.format(new Date(`${dia}T12:00:00`))

async function cargar() {
  errorDeCarga.value = ''
  try {
    datos.value = await cargarPeso()
  } catch (fallo) {
    errorDeCarga.value = mensajeDePeso(fallo)
  }
}

/** Corre una acción; si falla, muestra el motivo y no toca lo escrito. Devuelve si salió bien. */
async function intentar(accion) {
  error.value = ''
  ocupado.value = true
  try {
    await accion()
    return true
  } catch (fallo) {
    error.value = mensajeDePeso(fallo)
    return false
  } finally {
    ocupado.value = false
  }
}

// --- Registrar (RF-003-01, 02) ----------------------------------------------

const pesoNuevo = ref('')
const fechaNueva = ref(HOY)
const confirmando = ref('') // mensaje del servidor cuando ese día ya tiene peso

async function guardar(reemplazar = false) {
  let resultado
  const listo = await intentar(async () => {
    resultado = await registrarPeso({ fecha: fechaNueva.value, peso: pesoNuevo.value, reemplazar })
  })
  if (!listo) return
  if (resultado.confirmar) {
    confirmando.value = resultado.confirmar
    return
  }
  confirmando.value = ''
  pesoNuevo.value = ''
  fechaNueva.value = HOY
  await cargar()
}

// --- Estatura y objetivo (RF-003-08, 12) -------------------------------------

const estaturaNueva = ref('')
const objetivoNuevo = ref('')
const editandoEstatura = ref(false)

async function guardarEstatura() {
  if (await intentar(() => fijarEstatura(Number(estaturaNueva.value)))) {
    editandoEstatura.value = false
    estaturaNueva.value = ''
    await cargar()
  }
}

async function guardarObjetivo(valor) {
  if (await intentar(() => fijarObjetivo(valor))) {
    objetivoNuevo.value = ''
    await cargar()
  }
}

const textoDelObjetivo = computed(() => {
  const objetivo = datos.value?.resumen?.objetivo
  if (!objetivo) return ''
  if (objetivo.alcanzado) return 'Objetivo alcanzado'
  return `Te faltan ${kg(objetivo.faltan)} por ${objetivo.direccion}`
})

const textoDelCambio = computed(() => {
  const cambio = datos.value?.resumen?.cambio
  if (!cambio) return ''
  if (cambio.direccion === 'igual') return 'Sin cambio'
  return `${cambio.direccion === 'bajo' ? '↓' : '↑'} ${kg(cambio.kg)}`
})

// --- Gráfica (RF-003-07) ----------------------------------------------------

const enOrden = computed(() => [...(datos.value?.registros ?? [])].reverse())
const valores = computed(() => enOrden.value.map((registro) => registro.peso))
const detalles = computed(() => enOrden.value.map((registro) => `${fechaCorta(registro.fecha)} · ${kg(registro.peso)}`))

// --- Historial: corregir y eliminar (RF-003-10, 11) --------------------------

const corrigiendo = ref(null) // { fecha, peso }
const eliminando = ref(null) // fecha

async function guardarCorreccion() {
  const { fecha: dia, peso } = corrigiendo.value
  if (await intentar(() => registrarPeso({ fecha: dia, peso, reemplazar: true }))) {
    corrigiendo.value = null
    await cargar()
  }
}

async function eliminar(dia) {
  if (await intentar(() => eliminarPeso(dia))) {
    eliminando.value = null
    await cargar()
  }
}

onMounted(cargar)
</script>

<template>
  <template v-if="errorDeCarga">
    <p class="mensaje mensaje--error" role="alert">{{ errorDeCarga }}</p>
    <button class="boton boton--ancho" type="button" @click="cargar">Reintentar</button>
  </template>

  <p v-else-if="!datos" class="suave">Cargando…</p>

  <template v-else>
    <!-- RF-003-01 y RNF-003-01: la fecha de hoy ya viene puesta. -->
    <form class="tarjeta" @submit.prevent="guardar()">
      <div class="registro">
        <label class="campo">
          <span>Peso (kg)</span>
          <input v-model="pesoNuevo" type="text" inputmode="decimal" autocomplete="off" placeholder="Ej.: 79,5" />
        </label>
        <label class="campo">
          <span>Fecha</span>
          <input v-model="fechaNueva" type="date" :max="HOY" />
        </label>
      </div>

      <!-- RF-003-02 -->
      <div v-if="confirmando" class="tarjeta" role="alertdialog" aria-label="Reemplazar el peso de ese día">
        <p>{{ confirmando }} ¿Reemplazarlo por {{ pesoNuevo }} kg?</p>
        <div class="fila">
          <button class="boton boton--principal" type="button" :disabled="ocupado" @click="guardar(true)">Reemplazar</button>
          <button class="boton boton--texto" type="button" @click="confirmando = ''">Cancelar</button>
        </div>
      </div>
      <button v-else class="boton boton--principal boton--ancho" type="submit" :disabled="ocupado || !pesoNuevo.trim()">
        {{ ocupado ? 'Guardando…' : 'Guardar' }}
      </button>
    </form>

    <p v-if="error" class="mensaje mensaje--error" role="alert">{{ error }}</p>

    <!-- Sin registros: una invitación, sin ceros ni guiones. -->
    <section v-if="!datos.resumen" class="tarjeta">
      <h2>Tu primer registro</h2>
      <p>Pésate y escribe tu peso arriba. Desde ahí verás tu cambio, tu IMC y tu avance.</p>
    </section>

    <template v-else>
      <!-- RF-003-03, 04, 05: tres datos sin desplazarse. -->
      <section class="tarjeta">
        <div class="datos">
          <div>
            <span class="suave">Actual</span>
            <strong>{{ kg(datos.resumen.actual) }}</strong>
          </div>
          <div>
            <span class="suave">Cambio</span>
            <strong v-if="textoDelCambio">{{ textoDelCambio }}</strong>
            <span v-else>Primer registro</span>
          </div>
          <div v-if="datos.resumen.imc">
            <span class="suave">IMC</span>
            <strong>{{ String(datos.resumen.imc.valor).replace('.', ',') }}</strong>
            <span class="suave">{{ datos.resumen.imc.categoria }}</span>
          </div>
        </div>
        <!-- RN-003-09 -->
        <p v-if="datos.resumen.imc" class="suave aclaracion">El IMC es orientativo: no distingue músculo de grasa.</p>

        <!-- Alterno 1a / RF-003-12: sin estatura no hay IMC. -->
        <form v-if="!datos.estatura || editandoEstatura" class="fila" @submit.prevent="guardarEstatura">
          <label class="campo crece">
            <span>{{ datos.estatura ? 'Nueva estatura (cm)' : 'Agrega tu estatura para ver tu IMC (cm)' }}</span>
            <input v-model="estaturaNueva" type="text" inputmode="numeric" placeholder="Ej.: 175" />
          </label>
          <button class="boton" type="submit" :disabled="ocupado || !estaturaNueva.trim()">Guardar</button>
        </form>
        <button v-else class="boton boton--texto" type="button" @click="editandoEstatura = true">
          Estatura: {{ datos.estatura }} cm · cambiar
        </button>
      </section>

      <!-- RF-003-08, 09 -->
      <section class="tarjeta">
        <h2>Peso objetivo</h2>
        <p v-if="datos.objetivo !== null" class="cifra">{{ textoDelObjetivo }}</p>
        <form class="fila" @submit.prevent="guardarObjetivo(objetivoNuevo)">
          <label class="campo crece">
            <span>{{ datos.objetivo !== null ? `Tu objetivo: ${kg(datos.objetivo)}` : 'Fija un peso objetivo (kg)' }}</span>
            <input v-model="objetivoNuevo" type="text" inputmode="decimal" placeholder="Ej.: 75" />
          </label>
          <button class="boton" type="submit" :disabled="ocupado || !objetivoNuevo.trim()">Guardar</button>
        </form>
        <button v-if="datos.objetivo !== null" class="boton boton--texto" type="button" :disabled="ocupado" @click="guardarObjetivo(null)">
          Quitar objetivo
        </button>
      </section>

      <!-- RF-003-07 -->
      <section class="tarjeta">
        <h2>Tu peso en el tiempo</h2>
        <GraficaDeLinea
          :valores="valores"
          :detalles="detalles"
          :formato="kg"
          :referencia="datos.objetivo"
          :texto-de-referencia="datos.objetivo !== null ? `Objetivo ${kg(datos.objetivo)}` : ''"
          unidad="registros de peso"
        />
      </section>

      <!-- RF-003-06, 10, 11 -->
      <section class="tarjeta">
        <h2>Historial</h2>
        <ul class="historial">
          <li v-for="registro in datos.registros" :key="registro.fecha">
            <form v-if="corrigiendo?.fecha === registro.fecha" class="fila" @submit.prevent="guardarCorreccion">
              <label class="campo crece">
                <span>{{ fecha(registro.fecha) }}</span>
                <input v-model="corrigiendo.peso" type="text" inputmode="decimal" aria-label="Peso corregido" />
              </label>
              <button class="boton boton--principal" type="submit" :disabled="ocupado">Guardar</button>
              <button class="boton boton--texto" type="button" @click="corrigiendo = null">Cancelar</button>
            </form>

            <div v-else-if="eliminando === registro.fecha" class="tarjeta">
              <p>¿Eliminar {{ kg(registro.peso) }} del {{ fecha(registro.fecha) }}? No se puede deshacer.</p>
              <div class="fila">
                <button class="boton boton--peligro" type="button" :disabled="ocupado" @click="eliminar(registro.fecha)">
                  Sí, eliminar
                </button>
                <button class="boton boton--texto" type="button" @click="eliminando = null">Cancelar</button>
              </div>
            </div>

            <div v-else class="fila fila--separada">
              <span>
                <strong>{{ kg(registro.peso) }}</strong>
                <span class="suave"> · {{ fecha(registro.fecha) }}</span>
              </span>
              <span class="fila">
                <button
                  class="boton boton--texto"
                  type="button"
                  @click="corrigiendo = { fecha: registro.fecha, peso: String(registro.peso).replace('.', ',') }"
                >
                  Corregir
                </button>
                <button class="boton boton--texto" type="button" :aria-label="`Eliminar el peso del ${fecha(registro.fecha)}`" @click="eliminando = registro.fecha">
                  ✕
                </button>
              </span>
            </div>
          </li>
        </ul>
      </section>
    </template>
  </template>
</template>

<style scoped>
.registro {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--espacio-2);
}

.registro input {
  width: 100%;
  min-width: 0;
}

.datos {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--espacio-2);
}

.datos > div {
  display: grid;
  gap: 2px;
}

.datos strong {
  font-size: 1.25rem;
}

.aclaracion {
  margin: 0;
  font-size: 0.875rem;
}

.cifra {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
}

.fila {
  flex-wrap: wrap;
  align-items: end;
}

.crece {
  flex: 1;
  min-width: 10rem;
}

.historial {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--espacio-2);
}

.historial li {
  border-top: 1px solid var(--linea);
  padding-top: var(--espacio-2);
}
</style>
