<!--
  Componente AppHeader (PanelSuperior)
  Encabezado principal de la aplicación.
  Incluye toggle del sidebar, logo, barra de búsqueda y menú de usuario.
  Incluye soporte para tema oscuro y responsive.
-->
<template>
  <header
    class="sticky top-0 flex w-full bg-white border-gray-200 z-99999 lg:border-b transition-colors duration-200"
  >
    <div class="flex items-center justify-between w-full px-4 py-3 lg:px-6 lg:py-4">
      <!-- Left side - Toggle button and logo -->
      <div class="flex items-center gap-4">
        <button
          @click="handleToggle"
          class="flex items-center justify-center w-10 h-10 text-gray-500 rounded-lg hover:bg-gray-100 transition-colors duration-200 lg:hidden"
          aria-label="Toggle sidebar"
          :aria-expanded="isMobileOpen"
        >
          <svg
            v-if="isMobileOpen"
            class="fill-current transform transition-transform duration-200"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M6.21967 7.28131C5.92678 6.98841 5.92678 6.51354 6.21967 6.22065C6.51256 5.92775 6.98744 5.92775 7.28033 6.22065L11.999 10.9393L16.7176 6.22078C17.0105 5.92789 17.4854 5.92788 17.7782 6.22078C18.0711 6.51367 18.0711 6.98855 17.7782 7.28144L13.0597 12L17.7782 16.7186C18.0711 17.0115 18.0711 17.4863 17.7782 17.7792C17.4854 18.0721 17.0105 18.0721 16.7176 17.7792L11.999 13.0607L7.28033 17.7794C6.98744 18.0722 6.51256 18.0722 6.21967 17.7794C5.92678 17.4865 5.92678 17.0116 6.21967 16.7187L10.9384 12L6.21967 7.28131Z"
              fill=""
            />
          </svg>
          <svg
            v-else
            class="transform transition-transform duration-200"
            width="16"
            height="12"
            viewBox="0 0 16 12"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M0.583252 1C0.583252 0.585788 0.919038 0.25 1.33325 0.25H14.6666C15.0808 0.25 15.4166 0.585786 15.4166 1C15.4166 1.41421 15.0808 1.75 14.6666 1.75L1.33325 1.75C0.919038 1.75 0.583252 1.41422 0.583252 1ZM0.583252 11C0.583252 10.5858 0.919038 10.25 1.33325 10.25L14.6666 10.25C15.0808 10.25 15.4166 10.5858 15.4166 11C15.4166 11.4142 15.0808 11.75 14.6666 11.75L1.33325 11.75C0.919038 11.75 0.583252 11.4142 0.583252 11ZM1.33325 5.25C0.919038 5.25 0.583252 5.58579 0.583252 6C0.583252 6.41421 0.919038 6.75 1.33325 6.75L7.99992 6.75C8.41413 6.75 8.74992 6.41421 8.74992 6C8.74992 5.58579 8.41413 5.25 7.99992 5.25L1.33325 5.25Z"
              fill="currentColor"
            />
          </svg>
        </button>
        <HeaderLogo />
      </div>

      <!-- Center - Search bar -->
      <div class="flex-1 max-w-md mx-4 hidden sm:block">
        <SearchBar />
      </div>

      <!-- Right side - User menu -->
      <div class="flex items-center gap-4">
        <!-- Mobile menu toggle -->
        <button
          @click="toggleApplicationMenu"
          class="flex items-center justify-center w-10 h-10 text-gray-700 rounded-lg hover:bg-gray-100 sm:hidden transition-colors duration-200"
          aria-label="Toggle application menu"
          :aria-expanded="isApplicationMenuOpen"
        >
          <svg
            class="transform transition-transform duration-200"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fillRule="evenodd"
              clipRule="evenodd"
              d="M5.99902 10.4951C6.82745 10.4951 7.49902 11.1667 7.49902 11.9951V12.0051C7.49902 12.8335 6.82745 13.5051 5.99902 13.5051C5.1706 13.5051 4.49902 12.8335 4.49902 12.0051V11.9951C4.49902 11.1667 5.1706 10.4951 5.99902 10.4951ZM17.999 10.4951C18.8275 10.4951 19.499 11.1667 19.499 11.9951V12.0051C19.499 12.8335 18.8275 13.5051 17.999 13.5051C17.1706 13.5051 16.499 12.8335 16.499 12.0051V11.9951C16.499 11.1667 17.1706 10.4951 17.999 10.4951ZM13.499 11.9951C13.499 11.1667 12.8275 10.4951 11.999 10.4951C11.1706 10.4951 10.499 11.1667 10.499 11.9951V12.0051C10.499 12.8335 11.1706 13.5051 11.999 13.5051C12.8275 13.5051 13.499 12.8335 13.499 12.0051V11.9951Z"
              fill="currentColor"
            />
          </svg>
        </button>
        
        <!-- Desktop user menu -->
        <div class="hidden sm:flex items-center gap-4">
          <UserMenu />
        </div>
      </div>
    </div>

    <!-- Mobile dropdown menu -->
    <div
      v-if="isApplicationMenuOpen"
      class="sm:hidden border-t border-gray-200 bg-white animate-slideDown"
    >
      <div class="px-4 py-3">
        <SearchBar />
      </div>
      <div class="flex items-center justify-between px-4 py-3 border-t border-gray-200">
        <UserMenu />
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useSidebar } from '../../composables/SidebarControl'
import SearchBar from './SearchBar.vue'
import HeaderLogo from './HeaderLogo.vue'
import UserMenu from './UserMenu.vue'

const { toggleSidebar, toggleMobileSidebar, isMobileOpen } = useSidebar()
const isApplicationMenuOpen = ref(false)

// Handle responsive sidebar toggle
const handleToggle = () => {
  if (window.innerWidth >= 1024) {
    toggleSidebar()
  } else {
    toggleMobileSidebar()
  }
}

const toggleApplicationMenu = () => {
  isApplicationMenuOpen.value = !isApplicationMenuOpen.value
}

// Handle window resize to close mobile menu
const handleResize = () => {
  if (window.innerWidth >= 1024) {
    isApplicationMenuOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.animate-slideDown {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.shadow-theme-md {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
</style>