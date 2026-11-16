<script setup>
// Pantalla de inicio: lo primero es empezar o continuar la sesión (RNF-006-03).
// Orden de la spec 004 (T-004-12): continuar → rutinas de hoy → sesión libre → últimas sesiones.
// Todo sale de lo guardado en el celular: funciona sin señal (RNF-004-01).
import { computed, ref } from 'vue'

import Encabezado from '../componentes/Encabezado.vue'
import EstadoDeSincronizacion from '../componentes/EstadoDeSincronizacion.vue'
import GuardarComoRutina from '../componentes/GuardarComoRutina.vue'
import MenuDeCuenta from '../componentes/MenuDeCuenta.vue'
import { acceso } from '../estado/acceso.js'
import { empezarSesionDesdeRutina, empezarSesionLibre, estado } from '../estado/sesion.js'
import { fechaLocal, rutinasHechasHoy } from '../reglas/progreso.js'

// Las demás secciones se abren desde la barra inferior (RF-007-01).
const emit = defineEmits(['sesion', 'contrasena', 'rutinas'])

// RF-004-01 y RN-004-11: rutinas que tienen marcado hoy (1 = lunes ... 7 = domingo).
const ahora = new Date()
const hoy = ((ahora.getDay() + 6) % 7) + 1
const rutinasDeHoy = computed(() => estado.rutinas.filter((rutina) => rutina.dias.includes(hoy)))
// RF-004-10.
const hechas = computed(() => rutinasHechasHoy(estado.hechasHoy, fechaLocal(ahora)))

const formatoDeFecha = new Intl.DateTimeFormat('es-CO', { weekday: 'short', day: 'numeric', month: 'short' })
const fecha = (iso) => formatoDeFecha.format(new Date(iso))

function empezarRutina(rutina) {
  error.value = ''
  try {
    empezarSesionDesdeRutina(rutina)
    emit('sesion')
  } catch (fallo) {
    error.value = fallo.mensaje
  }
}

const error = ref('')
// RF-008-06, 07: guardar la sesión que se acaba de terminar como rutina.
const guardandoComoRutina = ref(false)

const formatoDeHoy = new Intl.DateTimeFormat('es-CO', { weekday: 'long', day: 'numeric', month: 'long' })
const textoDeHoy = (() => {
  const texto = formatoDeHoy.format(ahora)
  return texto.charAt(0).toUpperCase() + texto.slice(1)
})()

function empezar() {
  error.value = ''
  try {
    empezarSesionLibre()
    emit('sesion')
  } catch (fallo) {
    error.value = fallo.mensaje
  }
}
</script>

<template>
  <main class="pantalla">
    <Encabezado :titulo="`Hola, ${acceso.cuenta.nombre}`" :subtitulo="textoDeHoy">
      <template #accion>
        <!-- RF-007-07 -->
        <MenuDeCuenta @contrasena="emit('contrasena')" />
      </template>
    </Encabezado>

    <!-- RF-006-07: resumen de la sesión que se acaba de terminar. -->
    <section v-if="estado.resumen" class="seccion" role="status">
      <h2 class="etiqueta">Sesión guardada</h2>
      <ul class="grupo">
        <li class="grupo__fila">
          <strong>{{ estado.resumen.nombre }}</strong>
          <span class="grupo__detalle">
            {{ estado.resumen.ejercicios.length }} {{ estado.resumen.ejercicios.length === 1 ? 'ejercicio' : 'ejercicios' }}
          </span>
        </li>
        <li v-for="ejercicio in estado.resumen.ejercicios" :key="ejercicio.id" class="grupo__fila">
          <span class="grupo__texto">
            <span>{{ ejercicio.nombre }}</span>
            <span class="suave numeros">
              {{ ejercicio.series.filter((serie) => serie.confirmada).map((serie) => `${String(serie.peso).replace('.', ',')} × ${serie.reps}`).join(' · ') }}
            </span>
          </span>
        </li>
      </ul>
      <button v-if="!guardandoComoRutina" class="boton boton--secundario boton--ancho" type="button" @click="guardandoComoRutina = true">
        Guardar como rutina
      </button>
    </section>

    <GuardarComoRutina
      v-if="estado.resumen && guardandoComoRutina"
      :id-sesion="estado.resumen.id"
      :nombre-sugerido="estado.resumen.nombre"
      @cerrar="guardandoComoRutina = false"
    />

    <EstadoDeSincronizacion />
    <p v-if="error" class="mensaje mensaje--error" role="alert">{{ error }}</p>

    <!-- RF-004-02 / RF-006-02: si hay una sesión en curso, lo primero es continuarla. -->
    <button v-if="estado.sesion" class="boton boton--principal boton--ancho" type="button" @click="emit('sesion')">
      Continuar sesión{{ estado.sesion.nombre ? `: ${estado.sesion.nombre}` : '' }}
    </button>

    <template v-else>
      <!-- RF-004-01 y 10: las rutinas de hoy primero; la ya hecha queda marcada. -->
      <section v-if="rutinasDeHoy.length > 0" class="seccion">
        <h2 class="etiqueta">Hoy toca</h2>
        <div v-for="rutina in rutinasDeHoy" :key="rutina.id" class="grupo inicio__hoy">
          <div class="inicio__rutina">
            <strong class="inicio__nombre">{{ rutina.nombre }}</strong>
            <span class="suave">
              {{ rutina.ejercicios.length }} {{ rutina.ejercicios.length === 1 ? 'ejercicio' : 'ejercicios' }}
            </span>
            <span v-if="hechas.includes(rutina.id)" class="logrado">✓ Hecha hoy</span>
          </div>
          <button
            class="boton boton--ancho"
            :class="hechas.includes(rutina.id) ? 'boton--secundario' : 'boton--principal'"
            type="button"
            @click="empezarRutina(rutina)"
          >
            {{ hechas.includes(rutina.id) ? `Repetir ${rutina.nombre}` : `Empezar ${rutina.nombre}` }}
          </button>
        </div>
      </section>

      <!-- RF-004-03: sin rutina hoy, elegir cualquiera o ir libre. -->
      <section v-else class="seccion">
        <h2 class="etiqueta">Hoy</h2>
        <div class="grupo inicio__hoy">
          <p>Hoy no tienes rutina asignada.</p>
          <button v-if="estado.rutinas.length > 0" class="boton boton--secundario boton--ancho" type="button" @click="emit('rutinas')">
            Elegir una rutina
          </button>
        </div>
      </section>

      <button class="boton boton--ancho" :class="{ 'boton--principal': rutinasDeHoy.length === 0 }" type="button" @click="empezar">
        Empezar sesión libre
      </button>
    </template>

    <!-- RF-004-07: las 3 últimas sesiones terminadas. -->
    <section v-if="estado.recientes.length > 0" class="seccion">
      <h2 class="etiqueta">Últimas sesiones</h2>
      <ul class="grupo">
        <li v-for="reciente in estado.recientes" :key="reciente.id" class="grupo__fila">
          <span>{{ reciente.nombre || 'Sesión libre' }}</span>
          <span class="grupo__detalle">{{ fecha(reciente.inicio) }}</span>
        </li>
      </ul>
    </section>
  </main>
</template>

<style scoped>
.inicio__hoy {
  display: grid;
  gap: var(--espacio-3);
  padding: var(--espacio-4);
}

.inicio__rutina {
  display: grid;
  gap: 2px;
}

.inicio__nombre {
  font-size: 24px;
  line-height: 28px;
  font-weight: 600;
}
</style>
