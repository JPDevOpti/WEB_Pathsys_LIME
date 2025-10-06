<template>
  <div class="relative">
    <button
      @click="toggleMenu"
      class="flex items-center justify-center w-8 h-8 rounded-lg hover:bg-gray-100 transition-colors"
      type="button"
    >
      <slot name="icon">
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M10.2441 6C10.2441 5.0335 11.0276 4.25 11.9941 4.25H12.0041C12.9706 4.25 13.7541 5.0335 13.7541 6C13.7541 6.9665 12.9706 7.75 12.0041 7.75H11.9941C11.0276 7.75 10.2441 6.9665 10.2441 6ZM10.2441 18C10.2441 17.0335 11.0276 16.25 11.9941 16.25H12.0041C12.9706 16.25 13.7541 17.0335 13.7541 18C13.7541 18.9665 12.9706 19.75 12.0041 19.75H11.9941C11.0276 19.75 10.2441 18.9665 10.2441 18ZM11.9941 10.25C11.0276 10.25 10.2441 11.0335 10.2441 12C10.2441 12.9665 11.0276 13.75 11.9941 13.75H12.0041C12.9706 13.75 13.7541 12.9665 13.7541 12C13.7541 11.0335 12.9706 10.25 12.0041 10.25H11.9941Z"
            fill="currentColor"
          />
        </svg>
      </slot>
    </button>

    <!-- Menú desplegable -->
    <div
      v-if="isOpen"
      class="absolute right-0 top-full mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-[9999]"
    >
      <div class="py-1">
        <button
          v-for="item in menuItems"
          :key="item.label"
          @click="handleItemClick(item)"
          class="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 transition-colors"
        >
          {{ item.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface MenuItem {
  label: string
  onClick: () => void
}

interface Props {
  menuItems: MenuItem[]
}

const props = defineProps<Props>()

const isOpen = ref(false)

const toggleMenu = () => {
  isOpen.value = !isOpen.value
}

const handleItemClick = (item: MenuItem) => {
  item.onClick()
  isOpen.value = false
}

// Cerrar menú al hacer clic fuera
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script> 