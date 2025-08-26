<!--
  Layout de pantalla completa sin elementos de navegación.
  - Para páginas que requieren el espacio completo de la pantalla
  - Ideal para páginas de inicio de sesión, registro, etc.
  - No incluye header ni sidebar
-->
<template>
  <div class="min-h-screen">
    <main>
      <slot></slot>
    </main>
  </div>
</template>

<script setup lang="ts">
// No se requieren imports ni lógica adicional
</script>