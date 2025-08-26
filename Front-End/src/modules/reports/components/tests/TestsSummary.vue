<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
    <!-- Total Solicitudes -->
    <div class="bg-blue-50 border border-blue-200 rounded-xl p-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-blue-600 font-medium">Total de pruebas realizadas</p>
          <p class="text-2xl font-bold text-blue-700">{{ totalSolicitadas.toLocaleString() }}</p>
          <p class="text-xs text-blue-600">en el período</p>
        </div>
        <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
          <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Completadas -->
    <div class="bg-green-50 border border-green-200 rounded-xl p-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-green-600 font-medium">Completadas</p>
          <p class="text-2xl font-bold text-green-700">{{ totalCompletadas.toLocaleString() }}</p>
          <p class="text-xs text-green-600">{{ porcentajeCompletado }}% del total</p>
        </div>
        <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Tiempo Promedio -->
    <div class="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-yellow-600 font-medium">Tiempo Promedio</p>
          <p class="text-2xl font-bold text-yellow-700">{{ tiempoPromedioFormateado }}</p>
          <p class="text-xs text-yellow-600">por prueba</p>
        </div>
        <div class="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
          <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TestStats } from '../../types/tests.types'

const props = defineProps<{
  datos: TestStats[]
  resumen?: {
    totalSolicitadas: number
    totalCompletadas: number
    tiempoPromedio: number
  }
}>()

// Calcular totales desde los datos si no hay resumen
const totalSolicitadas = computed(() => {
  if (props.resumen?.totalSolicitadas) return props.resumen.totalSolicitadas
  return props.datos.reduce((sum, test) => sum + test.solicitadas, 0)
})

const totalCompletadas = computed(() => {
  if (props.resumen?.totalCompletadas) return props.resumen.totalCompletadas
  return props.datos.reduce((sum, test) => sum + test.completadas, 0)
})

const porcentajeCompletado = computed(() => {
  if (totalSolicitadas.value === 0) return 0
  return Math.round((totalCompletadas.value / totalSolicitadas.value) * 100)
})

const tiempoPromedioFormateado = computed(() => {
  const tiempo = props.resumen?.tiempoPromedio || 0
  if (tiempo === 0) return '0.0 días'
  return `${tiempo.toFixed(1)} días`
})
</script>
