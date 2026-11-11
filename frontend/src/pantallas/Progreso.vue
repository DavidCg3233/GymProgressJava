<script setup>
// Progreso (T-004-13 · RF-004-04, 05, 06, 11, 12 · RNF-004-02, 03).
// Lo calcula el servidor: sin conexión se avisa y se puede reintentar.
import { computed, onMounted, ref } from 'vue'

import Explicacion from '../componentes/Explicacion.vue'
import { cargarProgreso, fijarMeta, mensajeDeProgreso } from '../estado/progreso.js'
import { EXPLICACIONES } from '../progreso/explicaciones.js'
import { META_MAXIMA, META_MINIMA } from '../reglas/progreso.js'
import Evolucion from './Evolucion.vue'

const emit = defineEmits(['volver'])

const datos = ref(null)
const error = ref('')
const errorDeMeta = ref('')
const ejercicio = ref(null) // el récord tocado: abre su evolución (RF-004-09)

const opcionesDeMeta = Array.from({ length: META_MAXIMA - META_MINIMA + 1 }, (_, n) => n + META_MINIMA)

const formatoCorto = new Intl.DateTimeFormat('es-CO', { day: 'numeric', month: 'short' })
const fecha = (dia) => formatoCorto.format(new Date(`${dia}T12:00:00`))
const kg = (valor) => `${String(valor).replace('.', ',')} kg`

const estaSemana = computed(() => datos.value?.semanas.at(-1)?.sesiones ?? 0)
const mayorSemana = computed(() =>
  Math.max(1, datos.value?.meta ?? 0, ...(datos.value?.semanas ?? []).map((semana) => semana.sesiones)),
)
const mayorGrupo = computed(() => Math.max(1, ...(datos.value?.grupos ?? []).map((grupo) => grupo.series)))

async function cargar() {
  error.value = ''
  try {
    datos.value = await cargarProgreso()
  } catch (fallo) {
    error.value = mensajeDeProgreso(fallo)
  }
}

async function cambiarMeta(evento) {
  errorDeMeta.value = ''
  const valor = evento.target.value === '' ? null : Number(evento.target.value)
  try {
    await fijarMeta(valor)
    await cargar()
  } catch (fallo) {
    errorDeMeta.value = mensajeDeProgreso(fallo)
    evento.target.value = datos.value?.meta ?? ''
  }
}

onMounted(cargar)
</script>

<template>
  <Evolucion v-if="ejercicio" :clave="ejercicio.clave" :nombre="ejercicio.nombre" @volver="ejercicio = null" />

  <main v-else class="pantalla">
    <header class="fila fila--separada">
      <h1>Progreso</h1>
      <button class="boton boton--texto" type="button" @click="emit('volver')">Inicio</button>
    </header>

    <!-- RNF-004-02 -->
    <template v-if="error">
      <p class="mensaje mensaje--error" role="alert">{{ error }}</p>
      <button class="boton boton--ancho" type="button" @click="cargar">Reintentar</button>
    </template>

    <p v-else-if="!datos" class="suave">Cargando…</p>

    <!-- RF-004-12: sin sesiones, una invitación y nada más. -->
    <section v-else-if="datos.vacio" class="tarjeta">
      <h2>Aún no hay nada que medir</h2>
      <p>Registra tu primera sesión y aquí verás tus récords, tus semanas y tus grupos musculares.</p>
      <button class="boton boton--principal boton--ancho" type="button" @click="emit('volver')">Ir a entrenar</button>
    </section>

    <template v-else>
      <!-- RF-004-05 y 11 -->
      <section class="tarjeta">
        <header class="fila fila--separada">
          <h2>Esta semana</h2>
          <Explicacion :texto="EXPLICACIONES.semana" />
        </header>
        <p class="cifra">
          <template v-if="datos.meta">{{ estaSemana }} de {{ datos.meta }} esta semana</template>
          <template v-else>{{ estaSemana }} {{ estaSemana === 1 ? 'sesión' : 'sesiones' }} esta semana</template>
        </p>

        <div class="fila">
          <label class="campo meta">
            <span>Meta semanal</span>
            <select :value="datos.meta ?? ''" @change="cambiarMeta">
              <option value="">Sin meta</option>
              <option v-for="opcion in opcionesDeMeta" :key="opcion" :value="opcion">
                {{ opcion }} {{ opcion === 1 ? 'sesión' : 'sesiones' }}
              </option>
            </select>
          </label>
          <Explicacion :texto="EXPLICACIONES.meta" />
        </div>
        <p v-if="errorDeMeta" class="mensaje mensaje--error" role="alert">{{ errorDeMeta }}</p>

        <ol class="semanas" aria-label="Sesiones de las últimas 12 semanas">
          <li
            v-for="semana in datos.semanas"
            :key="semana.inicio"
            class="semanas__semana"
            :class="{ 'semanas__semana--cumple': semana.cumple }"
            :aria-label="`Semana del ${fecha(semana.inicio)}: ${semana.sesiones}${semana.cumple ? ', cumplió la meta' : ''}`"
          >
            <span class="semanas__cifra">{{ semana.sesiones || '' }}</span>
            <span class="semanas__barra" :style="{ height: `${(semana.sesiones / mayorSemana) * 100}%` }" />
          </li>
        </ol>
        <p class="fila fila--separada suave semanas__pie">
          <span>{{ fecha(datos.semanas[0].inicio) }}</span>
          <span v-if="datos.meta"><span class="leyenda" aria-hidden="true">■</span> cumplió la meta</span>
          <span>esta semana</span>
        </p>
      </section>

      <!-- RF-004-06 -->
      <section class="tarjeta">
        <header class="fila fila--separada">
          <h2>Series por grupo esta semana</h2>
          <Explicacion :texto="EXPLICACIONES.grupos" />
        </header>
        <ul class="grupos">
          <li v-for="grupo in datos.grupos" :key="grupo.nombre" class="grupos__grupo">
            <span>{{ grupo.nombre }}</span>
            <span class="grupos__barra"><span :style="{ width: `${(grupo.series / mayorGrupo) * 100}%` }" /></span>
            <strong>{{ grupo.series }}</strong>
          </li>
        </ul>
      </section>

      <!-- RF-004-04: tocar un récord abre su gráfica (RF-004-09). -->
      <section class="tarjeta">
        <header class="fila fila--separada">
          <h2>Récords</h2>
          <Explicacion :texto="EXPLICACIONES.records" />
        </header>
        <button v-for="record in datos.records" :key="record.clave" class="record" type="button" @click="ejercicio = record">
          <span class="record__nombre">{{ record.nombre }}</span>
          <span class="record__valor">
            <strong>{{ record.peso_corporal ? 'peso corporal' : kg(record.peso) }} × {{ record.reps }}</strong>
            <span class="suave"> · {{ fecha(record.fecha) }}</span>
          </span>
          <span class="record__ir" aria-hidden="true">›</span>
        </button>
      </section>
    </template>
  </main>
</template>

<style scoped>
/* La explicación de un indicador baja a su propia línea (RNF-004-03). */
.tarjeta > header,
.fila {
  flex-wrap: wrap;
}

.leyenda {
  color: var(--color-acento);
}

.cifra {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.meta {
  flex: 1;
}

.semanas {
  list-style: none;
  margin: 0;
  padding: 0;
  height: 7rem;
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: var(--espacio-1);
  align-items: end;
}

.semanas__semana {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
  gap: 2px;
}

.semanas__cifra {
  font-size: 0.75rem;
  color: var(--color-texto-suave);
}

.semanas__barra {
  width: 100%;
  min-height: 2px;
  border-radius: 4px 4px 0 0;
  background: var(--color-borde);
}

.semanas__semana--cumple .semanas__barra {
  background: var(--color-acento);
}

.semanas__semana:last-child .semanas__cifra {
  color: var(--color-texto);
  font-weight: 700;
}

.semanas__pie {
  margin: 0;
  font-size: 0.75rem;
}

.grupos {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--espacio-2);
}

.grupos__grupo {
  display: grid;
  grid-template-columns: 6.5rem 1fr 2rem;
  align-items: center;
  gap: var(--espacio-2);
}

.grupos__grupo strong {
  text-align: right;
}

.grupos__barra {
  height: 0.6rem;
  border-radius: 999px;
  background: var(--color-fondo);
  overflow: hidden;
}

.grupos__barra span {
  display: block;
  height: 100%;
  background: var(--color-acento);
}

.record {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 2px var(--espacio-2);
  align-items: center;
  min-height: var(--tamano-toque);
  padding: var(--espacio-2) 0;
  border: 0;
  border-top: 1px solid var(--color-borde);
  background: none;
  color: var(--color-texto);
  text-align: left;
  font: inherit;
  cursor: pointer;
}

.record__nombre,
.record__valor {
  grid-column: 1;
}

.record__ir {
  grid-column: 2;
  grid-row: 1 / span 2;
  font-size: 1.5rem;
  color: var(--color-texto-suave);
}
</style>
