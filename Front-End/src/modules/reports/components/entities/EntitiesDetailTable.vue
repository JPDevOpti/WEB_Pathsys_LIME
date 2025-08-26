<template>
  <div class="overflow-x-auto -mx-4 sm:mx-0">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Entidad
          </th>
          <th scope="col" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
            Ambulatorios
          </th>
          <th scope="col" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
            Hospitalizados
          </th>
          <th scope="col" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
            Total
          </th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        <tr 
          v-for="entity in sortedEntities" 
          :key="entity.nombre"
          class="hover:bg-gray-50 transition-colors cursor-pointer"
          @click="$emit('entity-click', entity)"
          title="Clic para ver detalles"
        >
          <td class="px-6 py-4 whitespace-nowrap">
            <div class="flex items-center space-x-2">
              <span class="text-sm font-medium text-gray-900">{{ entity.nombre }}</span>
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-center">
            <span class="text-sm font-semibold text-green-600">{{ entity.ambulatorios.toLocaleString() }}</span>
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-center">
            <span class="text-sm font-semibold text-blue-600">{{ entity.hospitalizados.toLocaleString() }}</span>
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-center">
            <span class="text-sm font-bold text-gray-900">{{ entity.total.toLocaleString() }}</span>
          </td>
        </tr>
      </tbody>
      <tfoot class="bg-gray-50">
        <tr>
          <td class="px-6 py-4 text-sm font-bold text-gray-900">Total</td>
          <td class="px-6 py-4 text-center text-sm font-bold text-green-600">{{ totalAmbulatorios.toLocaleString() }}</td>
          <td class="px-6 py-4 text-center text-sm font-bold text-blue-600">{{ totalHospitalizados.toLocaleString() }}</td>
          <td class="px-6 py-4 text-center text-sm font-bold text-gray-900">{{ totalPacientes.toLocaleString() }}</td>
        </tr>
      </tfoot>
    </table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { EntityStats } from '../../types/entities.types'

const props = defineProps<{
  datos: EntityStats[]
}>()

const emit = defineEmits<{
  'entity-click': [entity: EntityStats]
}>()

const totalPacientes = computed(() => 
  props.datos.reduce((sum, entity) => sum + entity.total, 0)
)

const totalAmbulatorios = computed(() => 
  props.datos.reduce((sum, entity) => sum + entity.ambulatorios, 0)
)

const totalHospitalizados = computed(() => 
  props.datos.reduce((sum, entity) => sum + entity.hospitalizados, 0)
)

const sortedEntities = computed(() => {
  return [...props.datos].sort((a, b) => b.total - a.total) // Ordenar por total descendente
})
</script>
