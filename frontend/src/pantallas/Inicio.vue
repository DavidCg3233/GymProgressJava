<script setup>
// Pantalla de inicio: lo primero es empezar o continuar la sesión (RNF-006-03).
import { ref } from 'vue'

import { acceso, salir } from '../estado/acceso.js'
import { empezarSesionLibre, estado } from '../estado/sesion.js'

const emit = defineEmits(['sesion', 'historial', 'contrasena'])

const error = ref('')

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

    <p v-if="estado.aviso" class="mensaje mensaje--aviso" role="status">{{ estado.aviso }}</p>
    <p v-if="error" class="mensaje mensaje--error" role="alert">{{ error }}</p>

    <!-- RF-006-02: si hay una sesión en curso, lo primero es continuarla. -->
    <button v-if="estado.sesion" class="boton boton--principal boton--ancho inicio__principal" type="button" @click="emit('sesion')">
      Continuar sesión
    </button>
    <button v-else class="boton boton--principal boton--ancho inicio__principal" type="button" @click="empezar">
      Empezar sesión libre
    </button>

    <button class="boton boton--ancho" type="button" @click="emit('historial')">Historial</button>

    <footer class="fila fila--separada">
      <button class="boton boton--texto" type="button" @click="emit('contrasena')">Cambiar contraseña</button>
      <button class="boton boton--texto" type="button" @click="salir">Salir</button>
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
