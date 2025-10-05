<template>
  <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
    <h3 class="text-lg font-semibold text-blue-800 mb-2">Prueba de Navegación</h3>
    <div class="space-y-2">
      <div><strong>Ruta actual:</strong> {{ $route.path }}</div>
      <div><strong>Usuario autenticado:</strong> {{ isAuthenticated ? 'Sí' : 'No' }}</div>
      <div><strong>Rol del usuario:</strong> {{ userRole || 'No definido' }}</div>
      <div><strong>Estado del store:</strong> {{ storeStatus }}</div>
    </div>
    <div class="mt-4 space-x-2">
      <button 
        @click="$router.push('/dashboard')" 
        class="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Ir a Dashboard
      </button>
      <button 
        @click="$router.push('/cases/list')" 
        class="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
      >
        Ir a Casos
      </button>
      <button 
        @click="$router.push('/results')" 
        class="px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700"
      >
        Ir a Resultados
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const userRole = computed(() => authStore.userRole)
const storeStatus = computed(() => {
  return {
    user: !!authStore.user,
    token: !!authStore.token,
    loading: authStore.isLoading
  }
})
</script>
