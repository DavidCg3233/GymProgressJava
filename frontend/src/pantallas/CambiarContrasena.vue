<script setup>
// Cambio de contraseña. Obligatorio si se entró con una temporal (RNF-ACC-08, RNF-ACC-09).
import { computed, ref } from 'vue'

import { cambiarContrasena, salir } from '../estado/acceso.js'

const props = defineProps({ obligatorio: { type: Boolean, default: false } })
const emit = defineEmits(['listo', 'cancelar'])

const actual = ref('')
const nueva = ref('')
const repetida = ref('')
const error = ref('')
const enviando = ref(false)

const noCoinciden = computed(() => repetida.value !== '' && nueva.value !== repetida.value)

async function enviar() {
  if (nueva.value !== repetida.value) {
    error.value = 'Las dos contraseñas nuevas no coinciden.'
    return
  }
  error.value = ''
  enviando.value = true
  try {
    await cambiarContrasena(actual.value, nueva.value)
    emit('listo')
  } catch (fallo) {
    error.value = fallo.mensaje
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <main class="pantalla">
    <h1>{{ props.obligatorio ? 'Crea tu contraseña' : 'Cambiar contraseña' }}</h1>
    <p v-if="props.obligatorio" class="mensaje mensaje--aviso">
      Entraste con una contraseña temporal. Cámbiala por una tuya para continuar.
    </p>

    <form class="tarjeta" @submit.prevent="enviar">
      <label class="campo">
        <span>{{ props.obligatorio ? 'Contraseña temporal' : 'Contraseña actual' }}</span>
        <input v-model="actual" type="password" autocomplete="current-password" required />
      </label>

      <label class="campo">
        <span>Contraseña nueva (mínimo 10 caracteres)</span>
        <input v-model="nueva" type="password" autocomplete="new-password" minlength="10" required />
      </label>

      <label class="campo">
        <span>Repite la contraseña nueva</span>
        <input v-model="repetida" type="password" autocomplete="new-password" required />
      </label>

      <p v-if="noCoinciden" class="suave">Aún no coinciden.</p>
      <p v-if="error" class="mensaje mensaje--error" role="alert">{{ error }}</p>

      <button class="boton boton--principal boton--ancho" type="submit" :disabled="enviando">
        {{ enviando ? 'Guardando…' : 'Guardar contraseña' }}
      </button>
    </form>

    <button v-if="props.obligatorio" class="boton boton--texto" type="button" @click="salir">Salir</button>
    <button v-else class="boton boton--texto" type="button" @click="emit('cancelar')">Volver</button>
  </main>
</template>
