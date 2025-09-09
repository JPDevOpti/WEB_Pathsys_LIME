<template>
  <div class="space-y-4">
    <!-- Header con botón de exportar -->
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-semibold text-gray-900">Pruebas</h3>
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
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Prueba
          </th>
          <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
            Solicitadas
          </th>
          <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
            Completadas
          </th>
          <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
            Tiempo Prom.
          </th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        <tr 
          v-for="test in datos" 
          :key="test.codigo"
          class="hover:bg-gray-50 transition-colors cursor-pointer"
          @click="$emit('test-click', test)"
          title="Clic para ver detalles"
        >
          <td class="px-6 py-4 whitespace-nowrap">
            <div class="flex items-center">
              <div>
                <div class="text-sm font-medium text-gray-900">{{ test.nombre }}</div>
                <div class="text-sm text-gray-500">{{ test.codigo }}</div>
              </div>
              <svg class="w-4 h-4 ml-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-center">
            <span class="text-sm font-semibold text-blue-600">{{ test.solicitadas.toLocaleString() }}</span>
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-center">
            <span class="text-sm font-semibold text-green-600">{{ test.completadas.toLocaleString() }}</span>
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-center">
            <span class="text-sm font-semibold text-yellow-600">{{ test.tiempoPromedio.toFixed(1) }} días</span>
          </td>
        </tr>
      </tbody>
      <tfoot class="bg-gray-50">
        <tr>
          <td class="px-6 py-4 text-sm font-bold text-gray-900">Total</td>
          <td class="px-6 py-4 text-center text-sm font-bold text-blue-600">{{ totalSolicitadas.toLocaleString() }}</td>
          <td class="px-6 py-4 text-center text-sm font-bold text-green-600">{{ totalCompletadas.toLocaleString() }}</td>
          <td class="px-6 py-4 text-center text-sm font-bold text-yellow-600">{{ tiempoPromedioTotal.toFixed(1) }} días</td>
        </tr>
      </tfoot>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { DocsIcon } from '@/assets/icons'
import { BaseButton } from '@/shared/components'
import type { TestStats } from '../../types/tests.types'
import * as XLSX from 'xlsx'

const props = defineProps<{
  datos: TestStats[]
}>()

const emit = defineEmits<{
  'test-click': [test: TestStats]
}>()

const totalSolicitadas = computed(() => 
  props.datos.reduce((sum, test) => sum + test.solicitadas, 0)
)

const totalCompletadas = computed(() => 
  props.datos.reduce((sum, test) => sum + test.completadas, 0)
)

const tiempoPromedioTotal = computed(() => {
  if (props.datos.length === 0) return 0
  const total = props.datos.reduce((sum, test) => sum + test.tiempoPromedio, 0)
  return total / props.datos.length
})

// Función de exportación a Excel
const exportToExcel = () => {
  if (!props.datos.length) return
  
  const data = props.datos.map(test => ({
    'Prueba': test.nombre,
    'Código': test.codigo,
    'Solicitadas': test.solicitadas,
    'Completadas': test.completadas,
    'Tiempo Promedio (días)': test.tiempoPromedio.toFixed(1)
  }))
  
  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Pruebas')
  
  const fileName = `pruebas_${new Date().toISOString().split('T')[0]}.xlsx`
  XLSX.writeFile(wb, fileName)
}
</script>
