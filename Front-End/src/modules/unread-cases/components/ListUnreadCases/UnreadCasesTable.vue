<template>
  <div class="overflow-hidden rounded-xl border border-gray-200 bg-white">
    <!-- Barra de selección múltiple -->
    <div v-if="selectedIds.length > 0" class="bg-blue-50 border-b border-blue-200 px-4 py-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <span class="text-sm font-medium text-blue-800">
            {{ selectedIds.length }} caso{{ selectedIds.length !== 1 ? 's' : '' }} sin lectura seleccionado{{ selectedIds.length !== 1 ? 's' : '' }}
          </span>
          <button
            @click="clearSelection"
            class="text-sm text-blue-600 hover:text-blue-800 underline"
          >
            Deseleccionar todo
          </button>
        </div>
        
        <div class="flex items-center gap-2">
          <button
            @click="handleBatchMarkDelivered"
            class="inline-flex items-center gap-2 px-3 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Marcar como completadas
          </button>
        </div>

        <BatchMarkDeliveredDrawer
          v-model="showMarkDeliveredDrawer"
          :selected="props.unreadCases.filter(t => props.selectedIds.includes(t.id))"
          @close="showMarkDeliveredDrawer = false"
          @completed="handleBatchCompleted"
        />
      </div>
    </div>

    <!-- Tabla Desktop -->
    <div class="hidden lg:block max-w-full overflow-x-auto custom-scrollbar">
      <table class="min-w-full text-base">
        <thead>
          <tr class="border-b border-gray-200 bg-gray-50">
            <th class="px-2 py-2 text-center w-12">
              <div class="flex items-center justify-center">
                <FormCheckbox
                  :model-value="props.isAllSelected"
                  :id="`select-all-${props.selectedIds.length}-${props.unreadCases.length}`"
                  label=""
                  @update:model-value="toggleSelectAll"
                />
              </div>
            </th>
            <th v-for="column in props.columns" :key="column.key" class="px-2 py-2 text-center text-gray-700" :class="column.class">
              <button class="flex items-center gap-1 font-medium text-gray-600 text-sm hover:text-gray-700 justify-center w-full" @click="$emit('sort', column.key)">
                {{ column.label }}
                <span v-if="sortKey === column.key">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
              </button>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-if="props.unreadCases.length === 0">
            <td :colspan="props.columns.length + 1" class="px-4 py-12 text-center">
              <div class="flex flex-col items-center justify-center gap-3">
                <svg class="w-16 h-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p class="text-gray-500 text-base">{{ props.noResultsMessage }}</p>
              </div>
            </td>
          </tr>
          <tr v-for="(unreadCase, index) in props.unreadCases" :key="`unreadCase-${unreadCase.id}-${index}`" class="hover:bg-gray-50 cursor-pointer" @click="$emit('show-details', unreadCase)">
            <td class="px-2 py-3 text-center" @click.stop>
              <div class="flex items-center justify-center">
                <FormCheckbox
                  :model-value="isUnreadCaseSelected(unreadCase.id)"
                  :id="`unreadCase-${unreadCase.id}-${props.selectedIds.includes(unreadCase.id)}`"
                  label=""
                  @update:model-value="() => toggleUnreadCaseSelection(unreadCase.id)"
                />
              </div>
            </td>
            <td class="px-1 py-3 text-center">
              <span class="font-medium text-gray-800">{{ unreadCase.caseCode || unreadCase.id }}</span>
            </td>
            <td class="px-2 py-3 text-center">
              <div class="flex flex-col items-center gap-1">
                <p class="text-gray-800 text-sm font-medium">{{ unreadCase.patientName || (unreadCase.isSpecialCase ? 'Caso Especial' : '-') }}</p>
                <p class="text-gray-500 text-xs">{{ unreadCase.patientDocument || (unreadCase.isSpecialCase ? 'Lab. Externo' : 'Sin documento') }}</p>
              </div>
            </td>
            <td class="px-2 py-3 text-center">
              <p class="text-gray-800 text-sm">{{ unreadCase.institution || '—' }}</p>
            </td>
            <td class="px-3 py-3 text-center">
              <div v-if="hasAnyTest(unreadCase)" class="space-y-2">
                <!-- Mostrar testGroups si existen (nuevo formato) -->
                <template v-if="unreadCase.testGroups && unreadCase.testGroups.length > 0">
                  <div v-for="(group, idx) in unreadCase.testGroups" :key="idx" class="space-y-1">
                    <!-- Tipo de prueba arriba -->
                    <div :class="['text-xs font-semibold px-2 py-1 rounded border inline-block', getTestTypeColor(group.type)]">
                      {{ getTestTypeLabel(group.type) }}
                    </div>
                    <!-- Códigos de pruebas debajo -->
                    <div class="flex flex-wrap gap-1 justify-center">
                      <span 
                        v-for="(test, testIdx) in group.tests.slice(0, 4)" 
                        :key="testIdx"
                        class="test-badge inline-flex items-center justify-center bg-gray-100 text-gray-700 font-mono text-xs px-2 py-1 rounded border relative min-w-0"
                        :title="getTestTooltip(test)"
                      >
                        <span class="truncate test-code">{{ test.code }}</span>
                        <sub v-if="test.quantity > 1" class="absolute -top-1 -right-1 w-4 h-4 bg-blue-200 text-blue-800 text-[10px] font-bold rounded-full flex items-center justify-center">{{ test.quantity }}</sub>
                      </span>
                      <span
                        v-if="group.tests.length > 4"
                        class="inline-flex items-center justify-center bg-blue-50 text-blue-600 font-mono text-xs px-2 py-1 rounded border"
                        :title="`${group.tests.length - 4} pruebas más`"
                      >
                        +{{ group.tests.length - 4 }}
                      </span>
                    </div>
                  </div>
                </template>
                
                <!-- Formato antiguo (retrocompatibilidad) -->
                <template v-else>
                  <div class="space-y-1">
                    <span v-if="unreadCase.lowComplexityIHQ" class="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded border border-blue-200 block" :title="unreadCase.lowComplexityIHQ">
                      IHQ Baja ({{ unreadCase.lowComplexityPlates || 0 }})
                    </span>
                    <span v-if="unreadCase.highComplexityIHQ" class="text-xs bg-purple-50 text-purple-700 px-2 py-1 rounded border border-purple-200 block" :title="unreadCase.highComplexityIHQ">
                      IHQ Alta ({{ unreadCase.highComplexityPlates || 0 }})
                    </span>
                    <span v-if="unreadCase.specialIHQ" class="text-xs bg-orange-50 text-orange-700 px-2 py-1 rounded border border-orange-200 block" :title="unreadCase.specialIHQ">
                      IHQ Especial ({{ unreadCase.specialPlates || 0 }})
                    </span>
                    <span v-if="unreadCase.histochemistry" class="text-xs bg-green-50 text-green-700 px-2 py-1 rounded border border-green-200 block" :title="unreadCase.histochemistry">
                      Histoquímica ({{ unreadCase.histochemistryPlates || 0 }})
                    </span>
                  </div>
                </template>
              </div>
              <span v-else class="text-xs text-gray-400">
                Sin pruebas
              </span>
            </td>
            <td class="px-2 py-3 text-center">
              <p class="text-gray-800 text-sm font-semibold">{{ unreadCase.numberOfPlates ?? 0 }}</p>
            </td>
            <td class="px-2 py-3 text-center">
              <div class="flex flex-col items-center gap-1">
                <p class="text-gray-700 text-sm">{{ formatDate(unreadCase.entryDate) }}</p>
                <p class="text-gray-700 text-sm">
                  {{ unreadCase.deliveryDate ? formatDate(unreadCase.deliveryDate) : 'Pendiente' }}
                </p>
              </div>
            </td>
            <td class="px-2 py-3 text-center">
              <span :class="['px-2 py-1 rounded-full text-xs font-medium', getStatusClass(unreadCase.status)]">
                {{ unreadCase.status }}
              </span>
            </td>
            <td class="px-2 py-3 text-center">
              <div class="flex gap-1 justify-center min-w-[80px]">
                <button
                  @click.stop="$emit('show-details', unreadCase)"
                  class="p-1.5 rounded-md hover:bg-gray-100 text-gray-600"
                  title="Ver detalles"
                >
                  <InfoListIcon class="w-4 h-4" />
                </button>
                <button
                  @click.stop="$emit('edit', unreadCase)"
                  class="p-1.5 rounded-md hover:bg-gray-100 text-gray-600"
                  title="Editar caso sin lectura"
                >
                  <SettingsIcon class="w-4 h-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Vista Mobile -->
    <div class="lg:hidden divide-y divide-gray-200">
      <div v-if="props.unreadCases.length === 0" class="px-4 py-12 text-center">
        <div class="flex flex-col items-center justify-center gap-3">
          <svg class="w-16 h-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="text-gray-500 text-sm">{{ props.noResultsMessage }}</p>
        </div>
      </div>
      <div v-for="unreadCase in props.unreadCases" :key="unreadCase.id" class="p-4 hover:bg-gray-50" @click="$emit('show-details', unreadCase)">
        <div class="flex items-start gap-3">
          <input
            type="checkbox"
            :checked="isUnreadCaseSelected(unreadCase.id)"
            @change.stop="() => toggleUnreadCaseSelection(unreadCase.id)"
            class="mt-1 rounded border-gray-300"
          />
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between gap-2 mb-2">
              <div>
                <p class="font-semibold text-gray-900">
                  {{ unreadCase.patientName || (unreadCase.isSpecialCase ? 'Caso Especial' : 'Sin nombre') }}
                  <span v-if="unreadCase.isSpecialCase" class="ml-2 text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded-full">Externo</span>
                </p>
                <p class="text-sm text-gray-500">{{ unreadCase.caseCode }} - {{ unreadCase.patientDocument || (unreadCase.isSpecialCase ? 'Lab. Externo' : 'Sin documento') }}</p>
              </div>
              <span :class="['px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap', getStatusClass(unreadCase.status)]">
                {{ unreadCase.status }}
              </span>
            </div>
            <div class="space-y-1 text-sm">
              <p class="text-gray-600"><span class="font-medium">Institución:</span> {{ unreadCase.institution }}</p>
                <p class="text-gray-600"><span class="font-medium">Placas:</span> {{ unreadCase.numberOfPlates ?? 0 }} | <span class="font-medium">Entrega:</span> {{ unreadCase.deliveredTo || 'Pendiente' }}</p>
              <p class="text-gray-600"><span class="font-medium">Ingreso:</span> <span class="text-gray-700">{{ formatDate(unreadCase.entryDate) }}</span></p>
              <p class="text-gray-600"><span class="font-medium">Entrega:</span> <span class="text-gray-700">{{ unreadCase.deliveryDate ? formatDate(unreadCase.deliveryDate) : 'Pendiente' }}</span></p>
              
              <!-- Mostrar testGroups si existen (nuevo formato) -->
              <div v-if="unreadCase.testGroups && unreadCase.testGroups.length > 0" class="space-y-2 mt-2">
                <div v-for="(group, idx) in unreadCase.testGroups" :key="idx" class="space-y-1">
                  <!-- Tipo de prueba arriba -->
                  <div :class="['text-xs font-semibold px-2 py-1 rounded border inline-block', getTestTypeColor(group.type)]">
                    {{ getTestTypeLabel(group.type) }}
                  </div>
                  <!-- Códigos de pruebas debajo -->
                  <div class="flex flex-wrap gap-1">
                    <span 
                      v-for="(test, testIdx) in group.tests.slice(0, 6)" 
                      :key="testIdx"
                      class="test-badge inline-flex items-center justify-center bg-gray-100 text-gray-700 font-mono text-xs px-2 py-1 rounded border relative min-w-0"
                      :title="getTestTooltip(test)"
                    >
                      <span class="truncate test-code">{{ test.code }}</span>
                      <sub v-if="test.quantity > 1" class="absolute -top-1 -right-1 w-4 h-4 bg-blue-200 text-blue-800 text-[10px] font-bold rounded-full flex items-center justify-center">{{ test.quantity }}</sub>
                    </span>
                    <span
                      v-if="group.tests.length > 6"
                      class="inline-flex items-center justify-center bg-blue-50 text-blue-600 font-mono text-xs px-2 py-1 rounded border"
                      :title="`${group.tests.length - 6} pruebas más`"
                    >
                      +{{ group.tests.length - 6 }}
                    </span>
                  </div>
                </div>
              </div>
              
              <!-- Formato antiguo (retrocompatibilidad) -->
              <div v-else-if="hasAnyTest(unreadCase)" class="flex flex-wrap gap-1 mt-2">
                <span v-if="unreadCase.lowComplexityIHQ" class="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded border border-blue-200">IHQ Baja</span>
                <span v-if="unreadCase.highComplexityIHQ" class="text-xs bg-purple-50 text-purple-700 px-2 py-1 rounded border border-purple-200">IHQ Alta</span>
                <span v-if="unreadCase.specialIHQ" class="text-xs bg-orange-50 text-orange-700 px-2 py-1 rounded border border-orange-200">IHQ Especial</span>
                <span v-if="unreadCase.histochemistry" class="text-xs bg-green-50 text-green-700 px-2 py-1 rounded border border-green-200">Histoquímica</span>
              </div>
            </div>
            <div class="flex gap-1 pt-2 border-t border-gray-100">
              <button
                @click.stop="$emit('show-details', unreadCase)"
                class="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors text-xs font-medium"
              >
                <InfoListIcon class="w-3 h-3" />
                Ver detalles
              </button>
              <button
                @click.stop="$emit('edit', unreadCase)"
                class="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors text-xs font-medium"
              >
                <SettingsIcon class="w-3 h-3" />
                Editar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Paginación -->
    <div v-if="props.unreadCases.length > 0" class="border-t border-gray-200 px-4 py-3 bg-gray-50">
      <div class="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div class="flex items-center gap-2 text-sm text-gray-600">
          <span>Mostrando</span>
          <select
            :value="props.itemsPerPage"
            @change="$emit('update-items-per-page', Number(($event.target as HTMLSelectElement).value))"
            class="border border-gray-300 rounded px-2 py-1"
          >
            <option :value="10">10</option>
            <option :value="25">25</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
          <span>de {{ props.totalItems }} resultados</span>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="$emit('prev-page')"
            :disabled="props.currentPage === 1"
            class="px-3 py-1 border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Anterior
          </button>
          <span class="text-sm text-gray-600">Página {{ props.currentPage }} de {{ props.totalPages }}</span>
          <button
            @click="$emit('next-page')"
            :disabled="props.currentPage >= props.totalPages"
            class="px-3 py-1 border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Siguiente
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import InfoListIcon from '@/assets/icons/InfoListIcon.vue'
import SettingsIcon from '@/assets/icons/SettingsIcon.vue'
import type { UnreadCase } from '../../types'
import FormCheckbox from '@/shared/components/ui/forms/FormCheckbox.vue'
import BatchMarkDeliveredDrawer from './BatchMarkDeliveredDrawer.vue'

interface Column {
  key: string
  label: string
  class?: string
}

interface Props {
  unreadCases: UnreadCase[]
  selectedIds: string[]
  isAllSelected: boolean
  columns: Column[]
  sortKey: string
  sortOrder: 'asc' | 'desc'
  currentPage: number
  totalPages: number
  itemsPerPage: number
  totalItems: number
  noResultsMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  noResultsMessage: 'No hay casos sin lectura disponibles'
})

const emit = defineEmits<{
  (e: 'toggle-select', id: string): void
  (e: 'toggle-select-all'): void
  (e: 'clear-selection'): void
  (e: 'sort', key: string): void
  (e: 'show-details', unreadCase: UnreadCase): void
  (e: 'edit', unreadCase: UnreadCase): void
  (e: 'update-items-per-page', value: number): void
  (e: 'prev-page'): void
  (e: 'next-page'): void
  (e: 'refresh'): void
  (e: 'update-unread-case', unreadCaseId: string, updatedUnreadCase: UnreadCase): void
  (e: 'batch-delivered', payload: { caseCodes: string[]; deliveredTo: string; deliveryDate: string }): void
}>()

const showMarkDeliveredDrawer = ref(false)

const handleBatchMarkDelivered = () => {
  const selectedUnreadCases = props.unreadCases.filter(t => props.selectedIds.includes(t.id))
  const invalidUnreadCases = selectedUnreadCases.filter(t => t.status === 'Completado')
  
  if (invalidUnreadCases.length > 0) {
    alert('Algunos casos sin lectura seleccionados ya están completados')
    return
  }
  
  showMarkDeliveredDrawer.value = true
}

const handleBatchCompleted = (payload: { caseCodes: string[]; deliveredTo: string; deliveryDate: string }) => {
  emit('batch-delivered', payload)
  clearSelection()
}

const isUnreadCaseSelected = (id: string) => {
  return props.selectedIds.includes(id)
}

const toggleUnreadCaseSelection = (id: string) => {
  emit('toggle-select', id)
}

const toggleSelectAll = () => {
  emit('toggle-select-all')
}

const clearSelection = () => {
  emit('clear-selection')
}

const getStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    'En proceso': 'bg-blue-100 text-blue-800',
    'Completado': 'bg-green-100 text-green-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const formatDate = (date: string) => {
  if (!date) return '—'
  try {
    return new Date(date).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  } catch {
    return date
  }
}

const hasAnyTest = (unreadCase: UnreadCase) => {
  if (unreadCase.testGroups && unreadCase.testGroups.length > 0) {
    return unreadCase.testGroups.some((group: any) => group.tests && group.tests.length > 0)
  }
  return !!(unreadCase.lowComplexityIHQ || unreadCase.highComplexityIHQ || unreadCase.specialIHQ || unreadCase.histochemistry)
}

const getTestTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    'LOW_COMPLEXITY_IHQ': 'IHQ Baja Complejidad',
    'HIGH_COMPLEXITY_IHQ': 'IHQ Alta Complejidad',
    'SPECIAL_IHQ': 'IHQ Especiales',
    'HISTOCHEMISTRY': 'Histoquímicas'
  }
  return labels[type] || type
}

const getTestTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    'LOW_COMPLEXITY_IHQ': 'bg-blue-50 text-blue-700 border-blue-200',
    'HIGH_COMPLEXITY_IHQ': 'bg-purple-50 text-purple-700 border-purple-200',
    'SPECIAL_IHQ': 'bg-orange-50 text-orange-700 border-orange-200',
    'HISTOCHEMISTRY': 'bg-green-50 text-green-700 border-green-200'
  }
  return colors[type] || 'bg-gray-50 text-gray-700 border-gray-200'
}

const getTestTooltip = (test: any): string => {
  const name = test.name || test.code
  const quantity = test.quantity || 1
  return `${name} • ${quantity} vez${quantity > 1 ? 'es' : ''}`
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  height: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Estilos para los códigos de pruebas */
.test-code {
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  line-height: 1;
}

.test-badge {
  transition: all 0.2s ease-in-out;
}

.test-badge:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Mejoras para tooltips */
[title] {
  position: relative;
}

[title]:hover::after {
  content: attr(title);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  white-space: nowrap;
  z-index: 1000;
  pointer-events: none;
  margin-bottom: 0.25rem;
}
</style>
