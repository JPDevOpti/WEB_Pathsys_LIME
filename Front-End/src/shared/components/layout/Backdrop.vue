<!--
  Componente BackdropOverlay
  Componente que actúa como un fondo oscuro que cubre la pantalla cuando el sidebar está abierto.
  - Se muestra cuando el sidebar móvil está abierto
  - Al hacer clic en él, cierra el sidebar móvil
  - Solo visible en dispositivos móviles (oculto en lg y superiores)
-->
<template>
  <div
    v-if="isMobileOpen"
    class="fixed inset-0 bg-gray-900/50 z-9999 lg:hidden"
    @click="toggleMobileSidebar"
  ></div>
</template>

<script setup lang="ts">
import { useSidebar } from '@/shared/composables/SidebarControl'

// Obtener el estado y funciones del sidebar
const { toggleMobileSidebar, isMobileOpen } = useSidebar()

defineOptions({
  name: 'BackdropOverlay'
})
</script>