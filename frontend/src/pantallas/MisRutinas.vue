<script setup>
// Mis rutinas (T-002-14 · RF-002-01, 06, 21 · RNF-USA-04).
import { ref } from 'vue'

import EstadoDeSincronizacion from '../componentes/EstadoDeSincronizacion.vue'
import { duplicarRutina, eliminarRutina } from '../estado/rutinas.js'
import { empezarSesionDesdeRutina, estado } from '../estado/sesion.js'
import { NOMBRES_DE_LOS_DIAS } from '../reglas/rutinas.js'

const emit = defineEmits(['volver', 'editar', 'sesion', 'catalogo'])

const error = ref('')
const confirmandoEliminar = ref(null)
const ocupado = ref(false)

const dias = (rutina) =>
  rutina.dias.length === 0 ? 'Sin día' : rutina.dias.map((dia) => NOMBRES_DE_LOS_DIAS[dia - 1].slice(0, 3)).join(' · ')

function mensajeDe(fallo) {
  return fallo.sinConexion ? 'Para cambiar tus rutinas necesitas conexión.' : fallo.mensaje
}

async function intentar(accion) {
  error.value = ''
  ocupado.value = true
  try {
    await accion()
  } catch (fallo) {
    error.value = mensajeDe(fallo)
  } finally {
    ocupado.value = false
  }
}

function empezar(rutina) {
  error.value = ''
  try {
    // Funciona sin señal: usa la rutina guardada en el celular.
    empezarSesionDesdeRutina(rutina)
    emit('sesion')
  } catch (fallo) {
    error.value = fallo.mensaje
  }
}

function eliminar(rutina) {
  return intentar(async () => {
    await eliminarRutina(rutina.id)
    confirmandoEliminar.value = null
  })
}
</script>

<template>
  <main class="pantalla">
    <header class="fila fila--separada">
      <h1>Mis rutinas</h1>
      <button class="boton boton--texto" type="button" @click="emit('volver')">Inicio</button>
    </header>

    <EstadoDeSincronizacion />
    <p v-if="error" class="mensaje mensaje--error" role="alert">{{ error }}</p>

    <p v-if="estado.rutinas.length === 0" class="suave">
      Aún no tienes rutinas. Crea la primera para empezar tus sesiones con los ejercicios ya listos.
    </p>

    <section v-for="rutina in estado.rutinas" :key="rutina.id" class="tarjeta">
      <header>
        <h2>{{ rutina.nombre }}</h2>
        <p class="suave">
          {{ dias(rutina) }} · {{ rutina.ejercicios.length }} {{ rutina.ejercicios.length === 1 ? 'ejercicio' : 'ejercicios' }}
        </p>
      </header>

      <button
        class="boton boton--principal boton--ancho"
        type="button"
        :disabled="Boolean(estado.sesion)"
        @click="empezar(rutina)"
      >
        Empezar
      </button>

      <!-- RNF-USA-04: eliminar no se puede deshacer. -->
      <div v-if="confirmandoEliminar === rutina.id" class="tarjeta">
        <p>¿Eliminar "{{ rutina.nombre }}"? Tus sesiones pasadas con esta rutina se conservan.</p>
        <div class="fila">
          <button class="boton boton--peligro" type="button" :disabled="ocupado" @click="eliminar(rutina)">Sí, eliminar</button>
          <button class="boton boton--texto" type="button" @click="confirmandoEliminar = null">Cancelar</button>
        </div>
      </div>
      <div v-else class="fila fila--separada">
        <button class="boton boton--texto" type="button" @click="emit('editar', rutina.id)">Editar</button>
        <button class="boton boton--texto" type="button" :disabled="ocupado" @click="intentar(() => duplicarRutina(rutina.id))">
          Duplicar
        </button>
        <button class="boton boton--texto" type="button" @click="confirmandoEliminar = rutina.id">Eliminar</button>
      </div>
    </section>

    <p v-if="estado.sesion" class="suave">Tienes una sesión en curso: termínala para empezar otra.</p>

    <button class="boton boton--ancho" type="button" @click="emit('editar', null)">+ Nueva rutina</button>
    <button class="boton boton--texto" type="button" @click="emit('catalogo')">Mi catálogo de ejercicios</button>
  </main>
</template>
