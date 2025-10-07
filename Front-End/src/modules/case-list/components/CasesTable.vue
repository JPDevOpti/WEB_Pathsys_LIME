<template>
  <div class="overflow-hidden rounded-xl border border-gray-200 bg-white">
    <div v-if="selectedIds.length > 0" class="bg-blue-50 border-b border-blue-200 px-4 py-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <span class="text-sm font-medium text-blue-800">
            {{ selectedIds.length }} caso{{ selectedIds.length > 1 ? 's' : '' }} seleccionado{{ selectedIds.length > 1 ? 's' : '' }}
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
            @click="handleBatchDownloadExcel"
            :disabled="isDownloadingExcel"
            class="inline-flex items-center gap-2 px-3 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="isDownloadingExcel" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <DocsIcon v-else class="w-4 h-4" />
            {{ isDownloadingExcel ? 'Generando Excel...' : 'Exportar Excel Seleccionados' }}
          </button>
          
          <button
            v-if="!isPatologo && !isResidente && !isFacturacion"
            @click="handleBatchMarkDelivered"
            class="inline-flex items-center gap-2 px-3 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Marcar como entregados
          </button>
        </div>

        <BatchMarkDeliveredDrawer
          v-model="showMarkDeliveredDrawer"
          :selected="props.cases.filter(c => props.selectedIds.includes(c.id))"
          @close="showMarkDeliveredDrawer = false"
          @confirm="() => {}"
          @completed="handleBatchCompleted"
          @update-case="handleUpdateCase"
        />
      </div>
    </div>

    <div class="hidden lg:block max-w-full overflow-x-auto custom-scrollbar">
      <table class="min-w-full text-base">
        <thead>
          <tr class="border-b border-gray-200 bg-gray-50">
            <th class="px-2 py-2 text-center w-12">
              <div class="flex items-center justify-center">
                <FormCheckbox
                  :model-value="props.isAllSelected"
                  :id="`select-all-${props.selectedIds.length}-${props.cases.length}`"
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
          <tr v-for="(c, index) in props.cases" :key="`case-${c.id}-${index}`" class="hover:bg-gray-50" @click="toggleCaseSelection(c.id)">
            <td class="px-2 py-3 text-center">
              <div class="flex items-center justify-center">
                <FormCheckbox
                  :model-value="isCaseSelected(c.id)"
                  :id="`case-${c.id}-${props.selectedIds.includes(c.id)}`"
                  label=""
                  @update:model-value="() => toggleCaseSelection(c.id)"
                  @click.stop
                />
              </div>
            </td>
            <td class="px-1 py-3 text-center">
              <span class="font-medium text-gray-800">{{ c.caseCode || c.id }}</span>
            </td>
            <td class="px-2 py-3 text-center">
              <div class="flex flex-col items-center gap-1">
                <p class="text-gray-800 text-sm">{{ c.patient.fullName }}</p>
                <p class="text-gray-500 text-xs">{{ c.patient.dni }}</p>
              </div>
            </td>
            <td class="px-2 py-3 text-center">
              <p class="text-gray-800 text-sm">{{ c.entity }}</p>
              <p class="text-gray-500 text-xs">{{ c.pathologist || 'No asignado' }}</p>
            </td>
            <td class="px-3 py-3 text-center">
              <div v-if="getTestsLayout(c).totalTests > 0" class="space-y-1">
                <div class="grid grid-cols-2 gap-1">
                  <div class="flex flex-col gap-1 items-end">
                    <span v-for="(g, idx) in getTestsLayout(c).organized.column1" :key="`col1-${idx}`" class="inline-flex items-center text-nowrap min-w-0 flex-shrink-0" :title="getTestTooltip(c.tests, g.code, g.count)">
                      <span class="test-badge inline-flex items-center justify-center bg-gray-100 text-gray-700 font-mono text-xs px-2 py-1 rounded border relative min-w-0">
                        <span class="truncate test-code">{{ g.code }}</span>
                        <sub v-if="g.count > 1" class="absolute -top-1 -right-1 w-4 h-4 bg-blue-200 text-blue-800 text-[10px] font-bold rounded-full flex items-center justify-center">{{ g.count }}</sub>
                      </span>
                    </span>
                  </div>
                  <div class="flex flex-col gap-1 items-start">
                    <span v-for="(g, idx) in getTestsLayout(c).organized.column2" :key="`col2-${idx}`" class="inline-flex items-center text-nowrap min-w-0 flex-shrink-0" :title="getTestTooltip(c.tests, g.code, g.count)">
                      <span class="test-badge inline-flex items-center justify-center bg-gray-100 text-gray-700 font-mono text-xs px-2 py-1 rounded border relative min-w-0">
                        <span class="truncate test-code">{{ g.code }}</span>
                        <sub v-if="g.count > 1" class="absolute -top-1 -right-1 w-4 h-4 bg-blue-200 text-blue-800 text-[10px] font-bold rounded-full flex items-center justify-center">{{ g.count }}</sub>
                      </span>
                    </span>
                  </div>
                </div>
                <div v-if="getTestsLayout(c).organized.middle" class="flex justify-center">
                  <span class="inline-flex items-center text-nowrap min-w-0 flex-shrink-0" :title="getTestTooltip(c.tests, getTestsLayout(c).organized.middle!.code, getTestsLayout(c).organized.middle!.count)">
                    <span class="test-badge inline-flex items-center justify-center bg-gray-100 text-gray-700 font-mono text-xs px-2 py-1 rounded border relative min-w-0">
                      <span class="truncate test-code">{{ getTestsLayout(c).organized.middle!.code }}</span>
                      <sub v-if="getTestsLayout(c).organized.middle!.count > 1" class="absolute -top-1 -right-1 w-4 h-4 bg-blue-200 text-blue-800 text-[10px] font-bold rounded-full flex items-center justify-center">{{ getTestsLayout(c).organized.middle!.count }}</sub>
                    </span>
                  </span>
                </div>
                <div v-if="getTestsLayout(c).hasMore" class="flex justify-center mt-1">
                  <span class="inline-flex items-center justify-center bg-blue-50 text-blue-600 font-mono text-xs px-2 py-1 rounded border" :title="`${getTestsLayout(c).moreCount} pruebas más`">+{{ getTestsLayout(c).moreCount }}</span>
                </div>
              </div>
            </td>
            <td class="px-2 py-3 text-center">
              <span class="inline-flex items-center justify-center rounded-full px-3 py-1 text-xs font-medium w-full" :class="statusClass(c)">
                {{ statusLabel(c) }}
              </span>
            </td>
            <td class="px-2 py-3 text-center">
              <div class="flex flex-col items-center gap-1">
                <p class="text-gray-800 text-xs">{{ formatDate(c.receivedAt) }}</p>
                <p v-if="c.signedAt" class="text-gray-600 text-xs">{{ formatDate(c.signedAt) }}</p>
                <p v-else class="text-gray-400 text-xs">Pendiente</p>
              </div>
            </td>
            <td class="px-2 py-3 text-center">
              <div class="flex flex-col items-center gap-1">
                <span v-if="c.priority" class="inline-flex items-center justify-center rounded-full px-2 py-0.5 text-[10px] font-semibold"
                      :class="{
                        'bg-green-50 text-green-700': c.priority === 'Normal',
                        'bg-yellow-50 text-yellow-700': c.priority === 'Prioritario',
                        'bg-red-50 text-red-700': false
                      }">
                  {{ c.priority }}
                </span>
                <p v-if="c.receivedAt" class="text-xs font-medium px-2 py-0.5 rounded-full" :class="daysClass(c)" :title="`${elapsedDays(c)} días hábiles transcurridos (solo lunes a viernes)`">
                  {{ elapsedDays(c) }} días
                </p>
              </div>
            </td>
            <td class="px-2 py-3 text-center">
              <div class="flex gap-1 justify-center min-w-[120px]">
                <button class="p-1.5 rounded-md hover:bg-gray-100 text-gray-600" @click.stop="$emit('show-details', c)" title="Ver detalles"><InfoListIcon class="w-4 h-4" /></button>
                <button v-if="!isPatologo && !isResidente && !isFacturacion && c.status !== 'Completado'" class="p-1.5 rounded-md hover:bg-gray-100 text-gray-600" @click.stop="handleEdit(c)" title="Editar caso"><SettingsIcon class="w-4 h-4" /></button>
                <button v-if="c.status === 'En proceso' && !isFacturacion" class="p-1.5 rounded-md hover:bg-gray-100 text-gray-600" @click.stop="handlePerform(c)" title="Realizar resultados">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
                </button>
                <button v-if="['Por firmar','Por entregar'].includes(c.status) && !isFacturacion" class="p-1.5 rounded-md hover:bg-gray-100 text-gray-600" @click.stop="handleValidate(c)" :title="c.status === 'Por firmar' ? 'Realizar validación del informe' : 'Validar'">
                  <svg v-if="c.status === 'Por firmar'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path></svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="props.cases.length === 0">
            <td :colspan="props.columns.length + 1" class="px-5 py-8 text-center">
              <p class="text-gray-500 text-sm">{{ noResultsMessage }}</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="lg:hidden">
      <div class="space-y-3 p-4">
        <div
          v-for="(c, index) in props.cases" 
          :key="`case-mobile-${c.id}-${index}`"
          class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          @click="toggleCaseSelection(c.id)"
        >
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center gap-3 flex-1 min-w-0">
              <FormCheckbox
                :model-value="isCaseSelected(c.id)"
                :id="`case-mobile-${c.id}-${props.selectedIds.includes(c.id)}`"
                label=""
                @update:model-value="() => toggleCaseSelection(c.id)"
                @click.stop
              />
              <div>
                <div class="flex flex-col gap-1 mb-2">
                  <h4 class="font-semibold text-gray-800 text-sm truncate">{{ c.caseCode || c.id }}</h4>
                </div>
                <div class="flex flex-col gap-1">
                  <p class="text-gray-600 text-xs">{{ c.patient.fullName }}</p>
                  <p class="text-gray-500 text-xs">{{ c.patient.dni }}</p>
                  <span v-if="c.priority" class="inline-flex items-center justify-center rounded-full px-2 py-0.5 text-[10px] font-semibold self-start"
                        :class="{
                          'bg-green-50 text-green-700': c.priority === 'Normal',
                          'bg-yellow-50 text-yellow-700': c.priority === 'Prioritario',
                          'bg-red-50 text-red-700': false
                        }">
                    {{ c.priority }}
                  </span>
                </div>
              </div>
            </div>
            <div class="flex-shrink-0 ml-3">
              <span class="inline-flex items-center justify-center rounded-full px-2 py-1 text-xs font-medium" :class="statusClass(c)">
                {{ statusLabel(c) }}
              </span>
              <span v-if="c.priority" class="mt-1 inline-flex items-center justify-center rounded-full px-2 py-1 text-[10px] font-semibold w-full"
                    :class="{
                      'bg-green-50 text-green-700': c.priority === 'Normal',
                      'bg-yellow-50 text-yellow-700': c.priority === 'Prioritario',
                      'bg-red-50 text-red-700': false
                    }">
                {{ c.priority }}
              </span>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3 mb-3 text-xs">
            <div>
              <p class="text-gray-500">Entidad</p>
              <p class="text-gray-800 font-medium">{{ c.entity }}</p>
            </div>
            <div>
              <p class="text-gray-500">Patólogo</p>
              <p class="text-gray-800 font-medium">{{ c.pathologist || 'No asignado' }}</p>
            </div>
            <div>
              <p class="text-gray-500">Fecha recepción</p>
              <p class="text-gray-800 font-medium">{{ formatDate(c.receivedAt) }}</p>
            </div>
            <div>
              <p class="text-gray-500">Días hábiles</p>
              <p class="text-gray-800 font-medium" :class="daysClass(c)">
                {{ elapsedDays(c) }} días
              </p>
            </div>
            <div v-if="c.signedAt">
              <p class="text-gray-500">Fecha firma</p>
              <p class="text-gray-800 font-medium">{{ formatDate(c.signedAt) }}</p>
            </div>
          </div>

          <div class="mb-3">
            <p class="text-gray-500 text-xs mb-2">Pruebas</p>
            <div class="grid grid-cols-3 gap-1">
              <span
                v-for="(g, idx) in groupTests(c.tests).slice(0, 6)"
                :key="idx"
                class="inline-flex items-center text-nowrap min-w-0 flex-shrink-0"
                :title="getTestTooltip(c.tests, g.code, g.count)"
              >
                <span class="test-badge inline-flex items-center justify-center bg-gray-100 text-gray-700 font-mono text-xs px-2 py-1 rounded border relative min-w-0">
                  <span class="truncate test-code">{{ g.code }}</span>
                  <sub v-if="g.count > 1" class="absolute -top-1 -right-1 w-4 h-4 bg-blue-200 text-blue-800 text-[10px] font-bold rounded-full flex items-center justify-center">{{ g.count }}</sub>
                </span>
              </span>
              <span
                v-if="groupTests(c.tests).length > 6"
                class="inline-flex items-center justify-center bg-blue-50 text-blue-600 font-mono text-xs px-2 py-1 rounded border"
                :title="`${groupTests(c.tests).length - 6} pruebas más`"
              >
                +{{ groupTests(c.tests).length - 6 }}
              </span>
            </div>
          </div>

          <div class="flex gap-1 pt-2 border-t border-gray-100">
            <button class="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors text-xs font-medium" @click.stop="$emit('show-details', c)"><InfoListIcon class="w-3 h-3" />Ver detalles</button>
            <button v-if="!isPatologo && !isResidente && !isFacturacion && c.status !== 'Completado'" class="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors text-xs font-medium" @click.stop="handleEdit(c)"><SettingsIcon class="w-3 h-3" />Editar</button>
            <button v-if="c.status === 'En proceso' && !isFacturacion" class="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors text-xs font-medium" @click.stop="handlePerform(c)">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>Realizar
            </button>
            <button v-if="['Por firmar','Por entregar'].includes(c.status) && !isFacturacion" class="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors text-xs font-medium" @click.stop="handleValidate(c)">
              <svg v-if="c.status === 'Por firmar'" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path></svg>
              <svg v-else class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>Validar
            </button>
          </div>
        </div>

        <div v-if="props.cases.length === 0" class="text-center py-8">
          <div class="flex flex-col items-center space-y-2">
            <svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <div class="text-center"><p class="text-gray-500 text-sm font-medium">{{ noResultsMessage }}</p></div>
          </div>
        </div>
      </div>
    </div>

    <div class="px-4 sm:px-5 py-4 border-t border-gray-200 bg-gray-50">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div class="flex items-center gap-2 text-sm text-gray-500">
          <span>Mostrando</span>
          <select :value="itemsPerPage" @change="$emit('update-items-per-page', Number(($event.target as HTMLSelectElement)?.value))" class="h-8 rounded-lg border border-gray-300 bg-white px-2 py-1 text-sm text-gray-700">
            <option :value="5">5</option><option :value="10">10</option><option :value="20">20</option><option :value="50">50</option><option :value="100">100</option><option :value="totalItems">Todos</option>
          </select>
          <span>de {{ totalItems }} resultados</span>
        </div>
        <div class="flex items-center justify-center gap-2">
          <button @click="$emit('prev-page')" :disabled="currentPage === 1" class="px-3 py-1.5 border rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors">
            <span class="hidden sm:inline">Anterior</span><span class="sm:hidden">←</span>
          </button>
          <div class="flex items-center gap-1 text-sm text-gray-500">
            <span class="hidden sm:inline">Página</span><span class="font-medium">{{ currentPage }}</span><span class="hidden sm:inline">de</span><span class="hidden sm:inline">{{ totalPages }}</span><span class="sm:hidden">/ {{ totalPages }}</span>
          </div>
          <button @click="$emit('next-page')" :disabled="currentPage === totalPages" class="px-3 py-1.5 border rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors">
            <span class="hidden sm:inline">Siguiente</span><span class="sm:hidden">→</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Case } from '../../types/case.types'
import { InfoCircleIcon, SettingsIcon, DocsIcon } from '@/assets/icons'
import InfoListIcon from '@/assets/icons/InfoListIcon.vue'
import { useRouter } from 'vue-router'
import { ref } from 'vue'
import FormCheckbox from '@/shared/components/ui/forms/FormCheckbox.vue'
import BatchMarkDeliveredDrawer from './BatchMarkDeliveredDrawer.vue'
import { usePermissions } from '@/shared/composables/usePermissions'
import { useToasts } from '@/shared/composables/useToasts'

interface Column { 
  key: string
  label: string
  class?: string 
}

const props = defineProps<{
  cases: Case[]
  selectedIds: string[]
  isAllSelected: boolean
  columns: Column[]
  sortKey: string
  sortOrder: string
  currentPage: number
  totalPages: number
  itemsPerPage: number
  totalItems: number
  noResultsMessage: string
}>()

const emit = defineEmits<{
  'sort': [key: string]
  'show-details': [c: Case]
  'edit': [c: Case]
  'validate': [c: Case]
  'perform': [c: Case]
  'update-items-per-page': [value: number]
  'prev-page': []
  'next-page': []
  'toggle-select': [id: string]
  'toggle-select-all': []
  'clear-selection': []
  'refresh': []
  'update-case': [caseId: string, updatedCase: any]
}>()

const router = useRouter()
const { isPatologo, isResidente, isFacturacion } = usePermissions()
const { warning } = useToasts()

const isDownloadingExcel = ref(false)
const showMarkDeliveredDrawer = ref(false)

const showWarningToast = (title: string, message: string) => {
  warning('generic', title, message, 5000)
}

const toggleSelectAll = () => {
  emit('toggle-select-all')
}

const toggleCaseSelection = (caseId: string) => {
  emit('toggle-select', caseId)
}

const clearSelection = () => {
  emit('clear-selection')
}

const isCaseSelected = (caseId: string) => {
  if (!caseId || caseId.trim() === '') {
    return false
  }
  const isSelected = props.selectedIds.includes(caseId)
  return isSelected
}

const exportCasesToExcel = async (_cases: Case[], _type: string) => {}

const handleBatchDownloadExcel = async () => {
  if (props.selectedIds.length === 0) {
    return
  }
  
  try {
    const selectedCases = props.cases.filter(c => props.selectedIds.includes(c.id))
    
    if (selectedCases.length === 0) {
      return
    }
    
    isDownloadingExcel.value = true
    
    await exportCasesToExcel(selectedCases, 'selected')
    
  } catch (error) {
    alert('Error al exportar a Excel. Por favor, intente nuevamente.')
  } finally {
    isDownloadingExcel.value = false
  }
}

const handleBatchMarkDelivered = () => {
  if (isPatologo?.value || isResidente?.value || isFacturacion?.value) return
  
  const selectedCases = props.cases.filter(c => props.selectedIds.includes(c.id))
  const invalidCases = selectedCases.filter(c => c.status !== 'Por entregar')
  
  if (invalidCases.length > 0) {
    const invalidCodes = invalidCases.map(c => c.caseCode || c.id).join(', ')
    showWarningToast('Casos en estado inválido', `Los siguientes casos no están en estado "Por entregar" y no se pueden marcar como entregados: ${invalidCodes}`)
    return
  }
  
  showMarkDeliveredDrawer.value = true
}

const handleBatchCompleted = (_result: any) => {
  clearSelection()
  emit('refresh')
}

const handleUpdateCase = (caseId: string, updatedCase: any) => {
  emit('update-case', caseId, updatedCase)
}

const handleEdit = (c: Case) => {
  const code = c?.caseCode || ''
  if (!code) return
  
  emit('edit', c)
  router.push({ name: 'cases-edit', params: { code } })
}

const handlePerform = (c: Case) => {
  const code = c?.caseCode || ''
  if (!code) return
  
  emit('perform', c)
  router.push({ name: 'results-perform', query: { case: code, auto: '1' } })
}

const handleValidate = (c: Case) => {
  const code = c?.caseCode || ''
  if (!code) return
  
  emit('validate', c)
  router.push({ name: 'results-sign', query: { case: code, auto: '1' } })
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  const d = new Date(dateString)
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const groupedTestsCache = new Map<string, { code: string; count: number }[]>()
const testsLayoutCache = new Map<string, { organized: { column1: { code: string; count: number }[]; column2: { code: string; count: number }[]; middle: { code: string; count: number } | null }; totalTests: number; hasMore: boolean; moreCount: number }>()

const getTestsKeyFromStrings = (tests: string[]): string => `${tests.length}|${tests.slice(0, 3).join('|')}||${tests.slice(-3).join('|')}`

const groupTests = (tests: string[]): { code: string; count: number }[] => {
  const key = getTestsKeyFromStrings(tests)
  const cached = groupedTestsCache.get(key)
  if (cached) return cached
  const counts: Record<string, number> = {}
  const seenOrder: string[] = []
  tests.forEach((test) => {
    const trimmed = (test || '').trim()
    if (!trimmed) return
    let code = trimmed.split(/[\s-]/)[0]
    if (!code) code = trimmed.substring(0, 10)
    if (!counts[code]) { counts[code] = 0; seenOrder.push(code) }
    counts[code] += 1
  })
  const result = seenOrder.map(code => ({ code, count: counts[code] }))
  groupedTestsCache.set(key, result)
  return result
}

const organizeTestsInTwoColumns = (tests: { code: string; count: number }[]): {
  column1: { code: string; count: number }[]
  column2: { code: string; count: number }[]
  middle: { code: string; count: number } | null
} => {
  const visibleTests = tests.slice(0, 6)
  const totalTests = visibleTests.length
  if (totalTests === 0) return { column1: [], column2: [], middle: null }
  if (totalTests % 2 === 0) {
    const half = totalTests / 2
    return { column1: visibleTests.slice(0, half), column2: visibleTests.slice(half), middle: null }
  }
  const half = Math.floor(totalTests / 2)
  return { column1: visibleTests.slice(0, half), column2: visibleTests.slice(half + 1), middle: visibleTests[half] }
}

const getTestsLayout = (c: Case) => {
  const id = c.id || c.caseCode || ''
  const key = `${id}|${getTestsKeyFromStrings(c.tests)}`
  const cached = testsLayoutCache.get(key)
  if (cached) return cached
  const groupedTests = groupTests(c.tests)
  const organized = organizeTestsInTwoColumns(groupedTests)
  const totalTests = groupedTests.length
  const hasMore = totalTests > 6
  const moreCount = hasMore ? totalTests - 6 : 0
  const result = { organized, totalTests, hasMore, moreCount }
  testsLayoutCache.set(key, result)
  return result
}

const getTestTooltip = (tests: string[], code: string, count: number): string => {
  const matching = tests.filter(t => t.trim().startsWith(code))
  const names = matching.map(t => t.includes(' - ') ? t.split(' - ').slice(1).join(' - ') : t).filter(Boolean)
  const uniqueNames = Array.from(new Set(names))
  const nameStr = uniqueNames.length ? uniqueNames.join(', ') : `Código ${code}`
  return `${nameStr} • ${count} vez${count > 1 ? 'es' : ''}`
}

const elapsedDays = (c: Case): number => {
  if (!c.receivedAt) return 0
  return calculateBusinessDays(c.receivedAt, c.deliveredAt)
}

const calculateBusinessDays = (startDate: string, endDate?: string): number => {
  const start = new Date(startDate)
  const end = endDate ? new Date(endDate) : new Date()
  if (isNaN(start.getTime()) || isNaN(end.getTime())) return 0
  const fromDate = start <= end ? start : end
  const toDate = start <= end ? end : start
  let businessDays = 0
  const currentDate = new Date(fromDate)
  while (currentDate.getDay() === 0 || currentDate.getDay() === 6) {
    currentDate.setDate(currentDate.getDate() + 1)
    if (currentDate > toDate) return 0
  }
  const firstBusinessDay = new Date(currentDate)
  if (firstBusinessDay.toDateString() === toDate.toDateString()) return 0
  currentDate.setDate(currentDate.getDate() + 1)
  while (currentDate <= toDate) {
    const dayOfWeek = currentDate.getDay()
    if (dayOfWeek >= 1 && dayOfWeek <= 5) businessDays++
    currentDate.setDate(currentDate.getDate() + 1)
  }
  return Math.max(0, businessDays)
}

const statusLabel = (c: Case): string => c.status

const statusClass = (c: Case): string => {
  if (c.status === 'Por entregar') return 'bg-red-50 text-red-700 font-semibold'
  if (c.status === 'Por firmar') return 'bg-yellow-50 text-yellow-700'
  if (c.status === 'En proceso') return 'bg-blue-50 text-blue-700'
  if (c.status === 'Completado') return 'bg-green-50 text-green-700'
  return ''
}

const daysClass = (c: Case): string => {
  const days = elapsedDays(c)
  if (days > 4 && c.status !== 'Completado') return 'bg-red-50 text-red-700'
  if (days > 3 && c.status !== 'Completado') return 'bg-yellow-50 text-yellow-700'
  return 'bg-brand-50 text-brand-700'
}
</script>

<style scoped>
/* Scrollbar personalizado */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Mejoras para accesibilidad */
button:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

select:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Mejoras para la columna de pruebas */
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
}

/* Animaciones para las tarjetas móviles */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.lg\:hidden > div > div {
  animation: fadeIn 0.3s ease-out;
}

/* Mejoras para botones de acción en móvil */
.lg\:hidden button {
  transition: all 0.2s ease-in-out;
}

.lg\:hidden button:active {
  transform: scale(0.95);
}

/* Mejoras para el grid de pruebas en móvil */
.grid-cols-3 {
  grid-template-columns: repeat(3, 1fr);
}

@media (max-width: 640px) {
  .grid-cols-3 {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>