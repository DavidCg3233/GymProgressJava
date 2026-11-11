<script setup>
// Pantalla de inicio: lo primero es empezar o continuar la sesión (RNF-006-03).
import { computed, ref } from 'vue'

import EstadoDeSincronizacion from '../componentes/EstadoDeSincronizacion.vue'
import { acceso, salir } from '../estado/acceso.js'
import { empezarSesionDesdeRutina, empezarSesionLibre, estado, olvidarDatosLocales } from '../estado/sesion.js'

const emit = defineEmits(['sesion', 'historial', 'contrasena', 'rutinas'])

// Rutinas asignadas al día de hoy (1 = lunes ... 7 = domingo), para empezar en un toque (RNF-006-03).
const hoy = ((new Date().getDay() + 6) % 7) + 1
const rutinasDeHoy = computed(() => estado.rutinas.filter((rutina) => rutina.dias.includes(hoy)))

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

    <!-- RF-006-02: si hay una sesión en curso, lo primero es continuarla. -->
    <button v-if="estado.sesion" class="boton boton--principal boton--ancho inicio__principal" type="button" @click="emit('sesion')">
      Continuar sesión
    </button>
    <button v-else class="boton boton--principal boton--ancho inicio__principal" type="button" @click="empezar">
      Empezar sesión libre
    </button>

    <template v-if="!estado.sesion">
      <button
        v-for="rutina in rutinasDeHoy"
        :key="rutina.id"
        class="boton boton--principal boton--ancho inicio__principal"
        type="button"
        @click="empezarRutina(rutina)"
      >
        Hoy toca: {{ rutina.nombre }}
      </button>
    </template>

    <button class="boton boton--ancho" type="button" @click="emit('rutinas')">Mis rutinas</button>
    <button class="boton boton--ancho" type="button" @click="emit('historial')">Historial</button>

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
