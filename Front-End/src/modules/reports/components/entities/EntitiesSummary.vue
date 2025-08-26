<template>
  <ComponentCard title="Resumen de Entidades">
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      <div class="bg-yellow-50 p-4 rounded-md border border-yellow-100">
        <h4 class="text-sm font-semibold text-yellow-700 mb-1">Tiempo Promedio</h4>
        <div class="flex items-end justify-between">
          <span class="text-2xl font-bold text-yellow-600">{{ tiempoPromedioFormateado }}</span>
          <span class="text-sm text-yellow-500">por caso</span>
        </div>
      </div>
      <div class="bg-green-50 p-4 rounded-md border border-green-100">
        <h4 class="text-sm font-semibold text-green-700 mb-1">Ambulatorios</h4>
        <div class="flex items-end justify-between">
          <span class="text-2xl font-bold text-green-600">{{ totalAmbulatorios }}</span>
          <span class="text-sm text-green-500">{{ porcentajeAmbulatorios }}%</span>
        </div>
      </div>
      <div class="bg-blue-50 p-4 rounded-md border border-blue-100">
        <h4 class="text-sm font-semibold text-blue-700 mb-1">Hospitalizados</h4>
        <div class="flex items-end justify-between">
          <span class="text-2xl font-bold text-blue-600">{{ totalHospitalizados }}</span>
          <span class="text-sm text-blue-500">{{ porcentajeHospitalizados }}%</span>
        </div>
      </div>
      <div class="bg-gray-50 p-4 rounded-md border border-gray-200">
        <h4 class="text-sm font-semibold text-gray-700 mb-1">Total Pacientes</h4>
        <div class="flex items-end justify-between">
          <span class="text-2xl font-bold text-gray-700">{{ totalPacientes }}</span>
          <span class="text-sm text-gray-500">100%</span>
        </div>
      </div>
    </div>
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ComponentCard } from '@/shared/components/common'
import type { EntityStats } from '../../types/entities.types'

const props = defineProps<{
  datos: EntityStats[]
  resumen?: {
    total: number
    ambulatorios: number
    hospitalizados: number
    tiempoPromedio: number
  }
}>()

// Calcular totales desde los datos si no hay resumen
const totalPacientes = computed(() => {
  if (props.resumen?.total) return props.resumen.total
  return props.datos.reduce((sum, entity) => sum + entity.total, 0)
})

const totalAmbulatorios = computed(() => {
  if (props.resumen?.ambulatorios) return props.resumen.ambulatorios
  return props.datos.reduce((sum, entity) => sum + entity.ambulatorios, 0)
})

const totalHospitalizados = computed(() => {
  if (props.resumen?.hospitalizados) return props.resumen.hospitalizados
  return props.datos.reduce((sum, entity) => sum + entity.hospitalizados, 0)
})

const porcentajeAmbulatorios = computed(() => {
  if (totalPacientes.value === 0) return 0
  return Math.round((totalAmbulatorios.value / totalPacientes.value) * 100)
})

const porcentajeHospitalizados = computed(() => {
  if (totalPacientes.value === 0) return 0
  return Math.round((totalHospitalizados.value / totalPacientes.value) * 100)
})

const tiempoPromedioFormateado = computed(() => {
  const tiempo = props.resumen?.tiempoPromedio || 0
  if (tiempo === 0) return '0 días'
  return `${tiempo.toFixed(1)} días`
})
</script>
