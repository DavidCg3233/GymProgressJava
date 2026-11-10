<script setup>
// RF-006-18: muestra si hay cambios guardados en el celular que el servidor aún no tiene.
import { computed } from 'vue'

import { estado } from '../estado/sesion.js'

const cambios = computed(() => `${estado.pendientes} ${estado.pendientes === 1 ? 'cambio' : 'cambios'}`)
</script>

<template>
  <p v-if="estado.aviso" class="mensaje mensaje--error" role="alert">{{ estado.aviso }}</p>

  <p v-else-if="estado.sinConexion" class="mensaje mensaje--aviso sincronizacion" role="status">
    <strong>Sin conexión.</strong>
    <span v-if="estado.pendientes > 0">{{ cambios }} guardados en el celular; se enviarán cuando vuelva la señal.</span>
    <span v-else>Puedes seguir registrando; se guarda en el celular.</span>
  </p>

  <p v-else-if="estado.pendientes > 0" class="suave sincronizacion" role="status">Enviando {{ cambios }}…</p>
</template>

<style scoped>
.sincronizacion {
  display: grid;
  gap: var(--espacio-1);
}
</style>
