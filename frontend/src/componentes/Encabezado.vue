<script setup>
// Encabezado de pantalla (T-007-03 · DESIGN.md, sección 5).
// Título grande a la izquierda y, como mucho, una acción a la derecha.
// Opcional: "atrás" a la izquierda, para las pantallas dentro de una sección.
import Icono from './Icono.vue'

defineProps({
  titulo: { type: String, required: true },
  subtitulo: { type: String, default: '' },
  // Texto del botón "atrás"; vacío = sin botón.
  atras: { type: String, default: '' },
})
const emit = defineEmits(['atras'])
</script>

<template>
  <header class="encabezado">
    <button v-if="atras" class="encabezado__atras boton boton--texto" type="button" @click="emit('atras')">
      <Icono nombre="izquierda" :tamano="22" />
      <span>{{ atras }}</span>
    </button>
    <div class="encabezado__fila">
      <div class="encabezado__textos">
        <h1>{{ titulo }}</h1>
        <p v-if="subtitulo" class="encabezado__subtitulo">{{ subtitulo }}</p>
      </div>
      <div class="encabezado__accion">
        <slot name="accion" />
      </div>
    </div>
  </header>
</template>

<style scoped>
.encabezado {
  display: grid;
  gap: var(--espacio-1);
}

.encabezado__atras {
  justify-self: start;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  margin-left: calc(-1 * var(--espacio-2));
  padding-left: var(--espacio-1);
}

.encabezado__fila {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--espacio-3);
}

.encabezado__textos {
  min-width: 0;
}

.encabezado__textos h1 {
  overflow-wrap: anywhere;
}

.encabezado__subtitulo {
  margin-top: 2px;
  font-size: 15px;
  color: var(--tinta-suave);
}

.encabezado__accion {
  flex: none;
  display: flex;
  align-items: center;
}
</style>
