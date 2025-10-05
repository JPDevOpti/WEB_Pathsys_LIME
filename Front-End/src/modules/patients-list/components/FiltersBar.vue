<template>
  <ComponentCard 
    title="Filtros de Pacientes"
    :description="`${totalFiltered} de ${totalAll} pacientes`"
  >
    <template #icon>
      <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    </template>

    <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-4">
      <!-- Primera fila: Búsqueda general y fechas -->
      <!-- Búsqueda por texto general -->
      <div class="col-span-1 md:col-span-3 lg:col-span-3">
        <FormInputField
          v-model="local.search"
          label="Búsqueda general"
          placeholder="Buscar por nombre o número de identificación..."
          type="text"
        />
      </div>

      <!-- Fecha de creación desde -->
      <div class="col-span-1">
        <DateInputField
          v-model="local.date_from"
          label="Creado desde"
          placeholder="Seleccionar fecha"
        />
      </div>

      <!-- Fecha de creación hasta -->
      <div class="col-span-1">
        <DateInputField
          v-model="local.date_to"
          label="Creado hasta"
          placeholder="Seleccionar fecha"
        />
      </div>

      <!-- Segunda fila: Los 5 filtros restantes -->
      <!-- Entidad -->
      <div class="col-span-1">
        <EntityList
          v-model="entityCode"
          label="Entidad"
          placeholder="Todas las entidades"
          @update:model-value="handleEntityChange"
        />
      </div>

      <!-- Tipo de atención -->
      <div class="col-span-1">
        <FormSelect
          v-model="local.care_type"
          label="Tipo de Atención"
          placeholder="Todos"
          :options="careTypeOptions"
        />
      </div>

      <!-- Género -->
      <div class="col-span-1">
        <FormSelect
          v-model="local.gender"
          label="Género"
          placeholder="Todos"
          :options="genderOptions"
        />
      </div>

      <!-- Municipio -->
      <div class="col-span-1">
        <MunicipalityList
          v-model="municipalityCode"
          label="Municipio"
          placeholder="Seleccionar municipio..."
          @municipality-code-change="handleMunicipalityCodeChange"
          @municipality-name-change="handleMunicipalityNameChange"
          @subregion-change="handleSubregionChange"
        />
      </div>

      <!-- Subregión -->
      <div class="col-span-1">
        <FormSelect
          v-model="local.subregion"
          label="Subregión"
          placeholder="Todas"
          :options="subregionOptions"
        />
      </div>
    </div>

    <template #footer>
      <div class="flex flex-col sm:flex-row justify-end gap-2">
        <BaseButton size="sm" variant="outline" @click="handleClear">
          <template #icon-left><TrashIcon class="w-4 h-4 mr-1" /></template>
          Limpiar
        </BaseButton>
        <BaseButton size="sm" variant="outline" :disabled="!canExport" @click="handleExport">
          <template #icon-left><DocsIcon class="w-4 h-4 mr-1" /></template>
          Exportar a Excel
        </BaseButton>
        <BaseButton size="sm" variant="outline" :disabled="isLoading" @click="handleRefresh">
          <template #icon-left><RefreshIcon class="w-4 h-4 mr-1" /></template>
          Actualizar
        </BaseButton>
        <SearchButton text="Buscar" size="sm" :disabled="isLoading" @click="handleSearch" />
      </div>
    </template>
  </ComponentCard>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ComponentCard } from '@/shared/components'
import { RefreshIcon, DocsIcon, TrashIcon } from '@/assets/icons'
import { FormInputField, FormSelect, DateInputField } from '@/shared/components/ui/forms'
import { SearchButton, BaseButton } from '@/shared/components/ui/buttons'
import { EntityList, MunicipalityList } from '@/shared/components/ui/lists'
import type { PatientFilters, Gender, CareType } from '../types/patient.types'

interface Props {
  modelValue: PatientFilters
  totalFiltered: number
  totalAll: number
  isLoading?: boolean
  canExport?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: PatientFilters]
  'refresh': []
  'export': []
  'search': []
}>()

// Local state with default empty strings to avoid undefined warnings
const local = reactive({
  search: props.modelValue.search || '',
  municipality_code: props.modelValue.municipality_code || '',
  municipality_name: props.modelValue.municipality_name || '',
  subregion: props.modelValue.subregion || '',
  entity: props.modelValue.entity || '',
  gender: props.modelValue.gender || '',
  care_type: props.modelValue.care_type || '',
  date_from: props.modelValue.date_from || '',
  date_to: props.modelValue.date_to || '',
  skip: props.modelValue.skip || 0,
  limit: props.modelValue.limit || 100
})
const entityCode = ref<string>('')
const municipalityCode = ref<string>('')

// Opciones para los selects
const subregionOptions = [
  { value: '', label: 'Todas' },
  { value: 'Valle de Aburrá', label: 'Valle de Aburrá' },
  { value: 'Oriente', label: 'Oriente' },
  { value: 'Occidente', label: 'Occidente' },
  { value: 'Norte', label: 'Norte' },
  { value: 'Nordeste', label: 'Nordeste' },
  { value: 'Suroeste', label: 'Suroeste' },
  { value: 'Bajo Cauca', label: 'Bajo Cauca' },
  { value: 'Urabá', label: 'Urabá' }
]

const genderOptions = [
  { value: '', label: 'Todos' },
  { value: 'Masculino', label: 'Masculino' },
  { value: 'Femenino', label: 'Femenino' }
]

const careTypeOptions = [
  { value: '', label: 'Todos' },
  { value: 'Ambulatorio', label: 'Ambulatorio' },
  { value: 'Hospitalizado', label: 'Hospitalizado' }
]

// Watchers para sincronizar con el padre
watch(() => props.modelValue, (newValue) => {
  local.search = newValue.search || ''
  local.municipality_code = newValue.municipality_code || ''
  local.municipality_name = newValue.municipality_name || ''
  local.subregion = newValue.subregion || ''
  local.entity = newValue.entity || ''
  local.gender = newValue.gender || ''
  local.care_type = newValue.care_type || ''
  local.date_from = newValue.date_from || ''
  local.date_to = newValue.date_to || ''
  local.skip = newValue.skip || 0
  local.limit = newValue.limit || 100
  
  if (newValue.municipality_code) {
    municipalityCode.value = newValue.municipality_code
  }
}, { deep: true })

watch(local, (newValue) => {
  // Convert empty strings back to undefined for optional fields
  const filters: PatientFilters = {
    search: newValue.search || undefined,
    municipality_code: newValue.municipality_code || undefined,
    municipality_name: newValue.municipality_name || undefined,
    subregion: newValue.subregion || undefined,
    entity: newValue.entity || undefined,
    gender: (newValue.gender || undefined) as Gender | undefined,
    care_type: (newValue.care_type || undefined) as CareType | undefined,
    date_from: newValue.date_from || undefined,
    date_to: newValue.date_to || undefined,
    skip: newValue.skip,
    limit: newValue.limit
  }
  emit('update:modelValue', filters)
}, { deep: true })

// Handlers
const handleEntityChange = (value: string) => {
  local.entity = value
}

const handleMunicipalityCodeChange = (code: string) => {
  local.municipality_code = code
}

const handleMunicipalityNameChange = (name: string) => {
  local.municipality_name = name
}

const handleSubregionChange = (subregion: string) => {
  // Actualizar siempre la subregión cuando cambia el municipio
  local.subregion = subregion
}

const handleRefresh = () => {
  emit('refresh')
}

const handleExport = () => {
  emit('export')
}

const handleSearch = () => {
  emit('search')
}

const handleClear = () => {
  Object.assign(local, {
    search: '',
    municipality_code: '',
    municipality_name: '',
    subregion: '',
    entity: '',
    gender: '',
    care_type: '',
    date_from: '',
    date_to: '',
    skip: 0,
    limit: 100
  })
  
  entityCode.value = ''
  municipalityCode.value = ''
  
  // Emitir búsqueda con filtros limpios
  handleSearch()
}
</script>
