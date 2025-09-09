<template>
  <div class="space-y-4">
    <!-- Header con botón de exportar -->
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-semibold text-gray-900">Patólogos</h3>
      <BaseButton 
        v-if="datos.length > 0"
        size="sm" 
        variant="outline" 
        @click="exportToExcel"
      >
        <template #icon-left>
          <DocsIcon class="w-4 h-4 mr-1" />
        </template>
        Exportar Excel
      </BaseButton>
    </div>
    
    <div class="overflow-x-auto -mx-4 sm:mx-0">
      <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Patólogo
          </th>
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Total
          </th>
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Dentro
          </th>
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Fuera
          </th>
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            % Cumplimiento
          </th>
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Tiempo Promedio
          </th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        <tr 
          v-for="pathologist in sortedPathologists" 
          :key="pathologist.name" 
          class="hover:bg-gray-50 cursor-pointer transition-colors duration-200"
          @click="$emit('pathologistClick', pathologist)"
        >
          <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
            <div class="flex items-center space-x-2">
              <span>{{ pathologist.name }}</span>
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </div>
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
            {{ pathologist.withinOpportunity + pathologist.outOfOpportunity }}
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">
            {{ pathologist.withinOpportunity }}
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-red-600 font-medium">
            {{ pathologist.outOfOpportunity }}
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
            <span :class="getComplianceClass(compliancePercentage(pathologist))">
              {{ compliancePercentage(pathologist) }}%
            </span>
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
            {{ pathologist.avgTime.toFixed(1) }} días
          </td>
        </tr>
      </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { DocsIcon } from '@/assets/icons'
import { BaseButton } from '@/shared/components'
import type { PathologistMetrics } from '../../types/pathologists.types'
import * as XLSX from 'xlsx'

const props = defineProps<{ datos: PathologistMetrics[] }>()
defineEmits<{ (e: 'pathologistClick', pathologist: PathologistMetrics): void }>()

const compliancePercentage = (pathologist: PathologistMetrics): number => {
  const total = pathologist.withinOpportunity + pathologist.outOfOpportunity
  return total > 0 ? Math.round((pathologist.withinOpportunity / total) * 100) : 0
}

const getComplianceClass = (percentage: number): string => {
  if (percentage >= 80) return 'text-green-600 font-semibold'
  if (percentage >= 60) return 'text-yellow-600 font-semibold'
  return 'text-red-600 font-semibold'
}

const sortedPathologists = computed(() => {
  return [...props.datos].sort((a, b) => {
    const aTotal = a.withinOpportunity + a.outOfOpportunity
    const bTotal = b.withinOpportunity + b.outOfOpportunity
    return bTotal - aTotal // Ordenar por total descendente
  })
})

// Función de exportación a Excel
const exportToExcel = () => {
  if (!props.datos.length) return
  
  const data = props.datos.map(pathologist => {
    const total = pathologist.withinOpportunity + pathologist.outOfOpportunity
    const compliance = total > 0 ? Math.round((pathologist.withinOpportunity / total) * 100) : 0
    
    return {
      'Patólogo': pathologist.name,
      'Total': total,
      'Dentro de Oportunidad': pathologist.withinOpportunity,
      'Fuera de Oportunidad': pathologist.outOfOpportunity,
      '% Cumplimiento': `${compliance}%`,
      'Tiempo Promedio (días)': pathologist.avgTime.toFixed(1)
    }
  })
  
  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Patólogos')
  
  const fileName = `patologos_${new Date().toISOString().split('T')[0]}.xlsx`
  XLSX.writeFile(wb, fileName)
}
</script>
