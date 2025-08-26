<!--
  AdminLayout
  Layout principal de la aplicación con sidebar y header.
  Incluye manejo de estado del sidebar, backdrop para móviles y atajos de teclado.
-->
<template>
  <div class="bg-gray-50">
    <!-- ===== Page Wrapper Start ===== -->
    <div class="flex h-screen overflow-hidden">
      <!-- ===== Sidebar Start ===== -->
      <AppSidebar />
      <!-- ===== Sidebar End ===== -->

      <!-- ===== Content Area Start ===== -->
      <div 
        class="relative flex flex-1 flex-col overflow-y-auto overflow-x-hidden transition-all duration-300 ease-in-out min-w-0"
        :class="[
          isExpanded && !isMobileOpen ? 'lg:ml-72' : 'lg:ml-20',
          isHovered && !isExpanded && !isMobileOpen ? 'lg:ml-72' : ''
        ]"
      >
        <!-- ===== Header Start ===== -->
        <AppHeader />
        <!-- ===== Header End ===== -->

        <!-- ===== Main Content Start ===== -->
        <main class="flex-1">
          <div class="mx-auto max-w-screen-2xl p-4 sm:p-6 2xl:p-10">
            <slot />
          </div>
        </main>
        <!-- ===== Main Content End ===== -->
      </div>
      <!-- ===== Content Area End ===== -->
    </div>
    <!-- ===== Page Wrapper End ===== -->

    <!-- ===== Backdrop Start ===== -->
    <Backdrop />
    <!-- ===== Backdrop End ===== -->
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useSidebarProvider } from '../composables/SidebarControl'
import AppSidebar from '../components/layout/AppSidebar.vue'
import AppHeader from '../components/layout/AppHeader.vue'
import Backdrop from '../components/layout/Backdrop.vue'

// Proporcionar el contexto del sidebar y obtener las funciones y estados directamente
const { toggleSidebar, isExpanded, isMobileOpen, isHovered } = useSidebarProvider()

// Manejo de atajos de teclado
const handleKeydown = (event: KeyboardEvent) => {
  // Ctrl/Cmd + B para toggle del sidebar
  if ((event.ctrlKey || event.metaKey) && event.key === 'b') {
    event.preventDefault()
    toggleSidebar()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
/* Focus visible styles */
.focus\:outline-hidden:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
}
</style>