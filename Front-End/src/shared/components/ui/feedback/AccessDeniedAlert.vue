<template>
  <div v-if="showAlert" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
    <div class="flex items-center gap-2 mb-2">
      <svg class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
      </svg>
      <span class="text-sm font-medium text-red-800">Acceso Denegado</span>
    </div>
    <p class="text-sm text-red-700">{{ message }}</p>
    <button 
      @click="dismissAlert" 
      class="mt-2 text-xs text-red-600 hover:text-red-800 underline"
    >
      Cerrar
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const dismissed = ref(false)

const showAlert = computed(() => {
  return !dismissed.value && route.query.error === 'access-denied' && route.query.message
})

const message = computed(() => {
  return route.query.message as string || 'No tienes permisos para acceder a esta página.'
})

const dismissAlert = () => {
  dismissed.value = true
}
</script>
