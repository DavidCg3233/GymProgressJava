<script setup>
// Pantalla de inicio: lo primero es empezar o continuar la sesión (RNF-006-03).
// Orden de la spec 004 (T-004-12): continuar → rutinas de hoy → sesión libre → últimas sesiones.
// Todo sale de lo guardado en el celular: funciona sin señal (RNF-004-01).
import { computed, ref } from 'vue'

import EstadoDeSincronizacion from '../componentes/EstadoDeSincronizacion.vue'
import { acceso, salir } from '../estado/acceso.js'
import { empezarSesionDesdeRutina, empezarSesionLibre, estado, olvidarDatosLocales } from '../estado/sesion.js'
import { fechaLocal, rutinasHechasHoy } from '../reglas/progreso.js'

const emit = defineEmits(['sesion', 'historial', 'contrasena', 'rutinas', 'progreso'])

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
const confirmandoSalida = ref(false)

// RNF-ACC-04: al salir no queda nada de esta persona en el celular.
// Si hay cambios sin enviar, se perderían: primero se avisa (RNF-USA-04).
async function salirDeLaCuenta() {
  if (estado.pendientes > 0 && !confirmandoSalida.value) {
    confirmandoSalida.value = true
    return
  }
  error.value = ''
  try {
    await salir()
    await olvidarDatosLocales()
  } catch (fallo) {
    error.value = fallo.sinConexion ? 'Para salir de la cuenta necesitas conexión.' : fallo.mensaje
  }
}

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
    <header>
      <h1>Hola, {{ acceso.cuenta.nombre }}</h1>
    </header>

    <!-- RF-006-07: resumen de la sesión que se acaba de terminar. -->
    <section v-if="estado.resumen" class="tarjeta" role="status">
      <h2>Sesión guardada</h2>
      <p>
        {{ estado.resumen.nombre }} ·
        {{ estado.resumen.ejercicios.length }} {{ estado.resumen.ejercicios.length === 1 ? 'ejercicio' : 'ejercicios' }}
      </p>
      <ul class="resumen">
        <li v-for="ejercicio in estado.resumen.ejercicios" :key="ejercicio.id">
          <strong>{{ ejercicio.nombre }}</strong>
          <span class="suave">
            {{ ejercicio.series.filter((serie) => serie.confirmada).map((serie) => `${String(serie.peso).replace('.', ',')} × ${serie.reps}`).join(' · ') }}
          </span>
        </li>
      </ul>
    </section>

    <EstadoDeSincronizacion />
    <p v-if="error" class="mensaje mensaje--error" role="alert">{{ error }}</p>

    <!-- RF-004-02 / RF-006-02: si hay una sesión en curso, lo primero es continuarla. -->
    <button v-if="estado.sesion" class="boton boton--principal boton--ancho inicio__principal" type="button" @click="emit('sesion')">
      Continuar sesión{{ estado.sesion.nombre ? `: ${estado.sesion.nombre}` : '' }}
    </button>

    <template v-else>
      <!-- RF-004-01 y 10: las rutinas de hoy primero; la ya hecha queda marcada. -->
      <button
        v-for="rutina in rutinasDeHoy"
        :key="rutina.id"
        class="boton boton--ancho inicio__principal"
        :class="hechas.includes(rutina.id) ? 'inicio__hecha' : 'boton--principal'"
        type="button"
        @click="empezarRutina(rutina)"
      >
        <span>Hoy toca: {{ rutina.nombre }}</span>
        <small v-if="hechas.includes(rutina.id)">✓ Hecha hoy · tocar para repetir</small>
      </button>

      <!-- RF-004-03: sin rutina hoy, elegir cualquiera o ir libre. -->
      <section v-if="rutinasDeHoy.length === 0" class="tarjeta">
        <p>Hoy no tienes rutina asignada.</p>
        <button v-if="estado.rutinas.length > 0" class="boton boton--ancho" type="button" @click="emit('rutinas')">
          Elegir una rutina
        </button>
      </section>

      <button
        class="boton boton--ancho"
        :class="{ 'boton--principal inicio__principal': rutinasDeHoy.length === 0 }"
        type="button"
        @click="empezar"
      >
        Empezar sesión libre
      </button>
    </template>

    <!-- RF-004-07: las 3 últimas sesiones terminadas. -->
    <section v-if="estado.recientes.length > 0" class="tarjeta">
      <h2>Últimas sesiones</h2>
      <ul class="recientes">
        <li v-for="reciente in estado.recientes" :key="reciente.id" class="fila fila--separada">
          <span>{{ reciente.nombre || 'Sesión libre' }}</span>
          <span class="suave">{{ fecha(reciente.inicio) }}</span>
        </li>
      </ul>
    </section>

    <div class="inicio__menu">
      <button class="boton" type="button" @click="emit('rutinas')">Rutinas</button>
      <button class="boton" type="button" @click="emit('progreso')">Progreso</button>
      <button class="boton" type="button" @click="emit('historial')">Historial</button>
    </div>

    <section v-if="confirmandoSalida" class="tarjeta">
      <p>
        Tienes {{ estado.pendientes }} {{ estado.pendientes === 1 ? 'cambio' : 'cambios' }} sin enviar al servidor.
        Si sales ahora, se pierden.
      </p>
      <div class="fila">
        <button class="boton boton--peligro" type="button" @click="salirDeLaCuenta">Salir y perderlos</button>
        <button class="boton boton--texto" type="button" @click="confirmandoSalida = false">Cancelar</button>
      </div>
    </section>

    <footer class="fila fila--separada">
      <button class="boton boton--texto" type="button" @click="emit('contrasena')">Cambiar contraseña</button>
      <button class="boton boton--texto" type="button" @click="salirDeLaCuenta">Salir</button>
    </footer>
  </main>
</template>

<style scoped>
.inicio__principal {
  min-height: 4rem;
  font-size: 1.125rem;
}

.inicio__hecha {
  display: grid;
  gap: var(--espacio-1);
  background: var(--acento-tinte);
}

.inicio__hecha small {
  color: var(--tinta-suave);
  font-size: 0.875rem;
}

.inicio__menu {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--espacio-2);
}

.recientes {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--espacio-2);
}

.resumen {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: var(--espacio-2);
}

.resumen li {
  display: grid;
}
</style>
