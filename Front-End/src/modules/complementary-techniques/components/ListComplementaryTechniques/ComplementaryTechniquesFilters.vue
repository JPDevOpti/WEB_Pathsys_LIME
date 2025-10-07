<template>
  <ComponentCard 
    title="Listado de Técnicas Complementarias"
    description="Filtre las técnicas complementarias por código, nombre, tipo, estado y rango de fechas."
  >
    <template #icon>
      <TestIcon class="w-5 h-5 mr-2 text-blue-600" />
    </template>

    <div class="flex flex-col md:flex-row gap-3">
      <div class="flex-1">
        <label class="block text-sm font-medium text-gray-700 mb-1">Buscar por código, documento o nombre del paciente</label>
        <FormInputField v-model="local.searchQuery" placeholder="Ejemplo: 25IW008823, 1234567890, Juan Pérez" @keydown.enter.prevent />
      </div>
      <div class="flex gap-3 items-end">
        <div class="w-44 md:w-56">
          <DateInputField v-model="local.dateFrom" label="Fecha desde" placeholder="DD/MM/AAAA" />
        </div>
        <div class="w-44 md:w-56">
          <DateInputField v-model="local.dateTo" label="Fecha hasta" placeholder="DD/MM/AAAA" />
        </div>
      </div>
    </div>

    <div class="flex flex-col md:flex-row gap-3 mt-3">
      <div class="flex-1">
        <FormInputField 
          v-model="local.selectedInstitution" 
          label="Institución" 
          placeholder="Ejemplo: SURA, CES, AMERICAS" 
        />
      </div>
      <div class="flex-1">
        <FormSelect 
          v-model="local.selectedTestType" 
          label="Tipo de prueba" 
          :options="testTypeOptions" 
          placeholder="Seleccione tipo de prueba" 
          dense 
        />
      </div>
      <div class="flex-1">
        <FormSelect 
          v-model="local.selectedStatus" 
          label="Estado" 
          :options="statusOptions" 
          placeholder="Seleccione estado" 
          dense 
        />
      </div>
    </div>

    <template #footer>
      <div class="flex flex-col sm:flex-row justify-between gap-3">
        <!-- Botón de Nuevo Caso Especial (Izquierda) -->
        <div class="flex">
          <button
            @click="$emit('new-technique')"
            class="inline-flex items-center px-4 py-2 text-sm font-medium text-green-600 bg-transparent border border-green-600 rounded-lg hover:bg-green-50 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          >
            <SpecialCaseIcon class="w-4 h-4 mr-1.5" />
            Nuevo Caso Especial
          </button>
        </div>

        <!-- Botones de Acción (Derecha) -->
        <div class="flex flex-wrap gap-2">
          <BaseButton size="sm" variant="outline" @click="clearAll">
            <template #icon-left>
              <TrashIcon class="w-4 h-4 mr-1" />
            </template>
            Limpiar
          </BaseButton>
          <BaseButton size="sm" variant="outline" :disabled="!canExport" @click="$emit('export')">
            <template #icon-left>
              <DocsIcon class="w-4 h-4 mr-1" />
            </template>
            Exportar a Excel
          </BaseButton>
          <BaseButton size="sm" variant="outline" :disabled="isLoading" @click="$emit('refresh')">
            <template #icon-left>
              <RefreshIcon class="w-4 h-4 mr-1" />
            </template>
            Actualizar
          </BaseButton>
          <SearchButton text="Buscar" size="sm" :disabled="isLoading" @click="search" />
        </div>
      </div>
    </template>
  </ComponentCard>
</template>

<script setup lang="ts">
import { reactive, watch, onMounted } from 'vue'
import { BaseButton, ComponentCard } from '@/shared/components'
import { RefreshIcon, DocsIcon, TrashIcon } from '@/assets/icons'
import TestIcon from '@/assets/icons/TestIcon.vue'
import SpecialCaseIcon from '@/assets/icons/SpecialCaseIcon.vue'
import { FormInputField, FormSelect, DateInputField } from '@/shared/components/ui/forms'
import { SearchButton } from '@/shared/components/ui/buttons'

interface Filters {
  searchQuery: string
  dateFrom: string
  dateTo: string
  selectedInstitution: string
  selectedTestType: string
  selectedStatus: string
}

interface Props {
  modelValue: Filters
  totalFiltered: number
  totalAll: number
  isLoading?: boolean
  canExport?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:modelValue', v: Filters): void
  (e: 'refresh'): void
  (e: 'export'): void
  (e: 'search', v: Filters): void
  (e: 'new-technique'): void
}>()

const local = reactive<Filters>({ ...props.modelValue })

const testTypeOptions = [
  { value: '', label: 'Todas las pruebas' },
  { value: 'low_complexity', label: 'IHQ Baja Complejidad' },
  { value: 'high_complexity', label: 'IHQ Alta Complejidad' },
  { value: 'special', label: 'IHQ Especiales' },
  { value: 'histochemistry', label: 'Histoquímicas' }
]

const statusOptions = [
  { value: '', label: 'Todos' },
  { value: 'En proceso', label: 'En proceso' },
  { value: 'Completado', label: 'Completado' }
]

watch(() => props.modelValue, (v) => Object.assign(local, v))

onMounted(() => {
  // Establecer fechas por defecto si no existen
  if (!local.dateFrom) {
    const date = new Date()
    date.setMonth(date.getMonth() - 1)
    local.dateFrom = date.toLocaleDateString('es-ES')
  }
  if (!local.dateTo) {
    local.dateTo = new Date().toLocaleDateString('es-ES')
  }
})

const clearAll = () => {
  local.searchQuery = ''
  local.selectedInstitution = ''
  local.selectedTestType = ''
  local.selectedStatus = ''
  const date = new Date()
  date.setMonth(date.getMonth() - 1)
  local.dateFrom = date.toLocaleDateString('es-ES')
  local.dateTo = new Date().toLocaleDateString('es-ES')
  emit('update:modelValue', { ...local })
  emit('refresh')
}

const search = () => {
  emit('update:modelValue', { ...local })
  emit('search', { ...local })
}
</script>
