<script setup>
// Esqueleto de la app (T-006-04). Las pantallas llegan con las tareas de la fase 5.
</script>

<template>
  <main class="pantalla">
    <h1 class="pantalla__titulo">GymProgress</h1>
    <p class="pantalla__estado">En construcción.</p>
  </main>
</template>

<style scoped>
.pantalla {
  min-height: 100dvh;
  display: grid;
  place-content: center;
  gap: var(--espacio-2);
  padding: var(--espacio-4);
  text-align: center;
}

.pantalla__titulo {
  font-size: 1.75rem;
  font-weight: 700;
}

.pantalla__estado {
  color: var(--color-texto-suave);
}
</style>
