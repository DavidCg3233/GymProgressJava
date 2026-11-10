<script setup>
// Pantalla de acceso (T-006-14 · RNF-ACC-01).
import { ref } from 'vue'

import { entrar } from '../estado/acceso.js'

const identificador = ref('')
const contrasena = ref('')
const error = ref('')
const enviando = ref(false)

async function enviar() {
  error.value = ''
  enviando.value = true
  try {
    await entrar(identificador.value, contrasena.value)
  } catch (fallo) {
    // El servidor ya entrega un mensaje sin detalles técnicos (RNF-SEG-09).
    error.value = fallo.mensaje
    contrasena.value = ''
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <main class="pantalla acceso">
    <h1>GymProgress</h1>

    <form class="tarjeta" @submit.prevent="enviar">
      <label class="campo">
        <span>Usuario o correo</span>
        <input
          v-model="identificador"
          type="text"
          autocomplete="username"
          autocapitalize="none"
          autocorrect="off"
          spellcheck="false"
          required
        />
      </label>

      <label class="campo">
        <span>Contraseña</span>
        <input v-model="contrasena" type="password" autocomplete="current-password" required />
      </label>

      <p v-if="error" class="mensaje mensaje--error" role="alert">{{ error }}</p>

      <button class="boton boton--principal boton--ancho" type="submit" :disabled="enviando">
        {{ enviando ? 'Entrando…' : 'Entrar' }}
      </button>
    </form>

    <p class="suave">Las cuentas las crea el dueño de la app. Si olvidaste tu contraseña, pídele una temporal.</p>
  </main>
</template>

<style scoped>
.acceso {
  min-height: 90dvh;
  align-content: center;
}
</style>
