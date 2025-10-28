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
      <div class="col-span-1 md:col-span-2 lg:col-span-4">
        <FormInputField
          v-model="local.search"
          label="Búsqueda general"
          placeholder="Buscar por nombre o número de identificación..."
          type="text"
        />
      </div>

      <div class="col-span-1 md:col-span-1 lg:col-span-1">
        <DateInputField
          v-model="local.created"
          label="Creado desde"
          placeholder="Seleccionar fecha"
          min="01/01/2000"
          :minYear="2000"
        />
      </div>

      <div class="col-span-1">
        <EntityList
          v-model="entityCode"
          label="Entidad"
          placeholder="Todas las entidades"
          @update:model-value="handleEntityChange"
          @entity-selected="handleEntitySelected"
        />
      </div>

      <div class="col-span-1">
        <FormSelect
          v-model="local.care_type"
          label="Tipo de Atención"
          placeholder="Todos"
          :options="careTypeOptions"
        />
      </div>

      <div class="col-span-1">
        <FormSelect
          v-model="local.gender"
          label="Género"
          placeholder="Todos"
          :options="genderOptions"
        />
      </div>

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

const local = reactive({
  search: props.modelValue.search || '',
  municipality_code: props.modelValue.municipality_code || '',
  municipality_name: props.modelValue.municipality_name || '',
  subregion: props.modelValue.subregion || '',
  entity: props.modelValue.entity || '',
  gender: props.modelValue.gender || '',
  care_type: props.modelValue.care_type || '',
  created: props.modelValue.date_from && props.modelValue.date_to && props.modelValue.date_from === props.modelValue.date_to 
    ? props.modelValue.date_from 
    : '',
  date_from: props.modelValue.date_from || '',
  date_to: props.modelValue.date_to || '',
  skip: props.modelValue.skip || 0,
  limit: props.modelValue.limit || 100
})

const entityCode = ref<string>('')
const municipalityCode = ref<string>('')

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

watch(() => props.modelValue, (newValue) => {
  Object.assign(local, {
    search: newValue.search || '',
    municipality_code: newValue.municipality_code || '',
    municipality_name: newValue.municipality_name || '',
    subregion: newValue.subregion || '',
    entity: newValue.entity || '',
    gender: newValue.gender || '',
    care_type: newValue.care_type || '',
    created: (newValue.date_from && newValue.date_to && newValue.date_from === newValue.date_to) 
      ? newValue.date_from 
      : '',
    date_from: newValue.date_from || '',
    date_to: newValue.date_to || '',
    skip: newValue.skip || 0,
    limit: newValue.limit || 100
  })
})

const buildFilters = (): PatientFilters => {
  if (local.created) {
    local.date_from = local.created
    local.date_to = local.created
  } else if (!local.date_from && !local.date_to) {
    local.date_from = ''
    local.date_to = ''
  }

  return {
    search: local.search || undefined,
    municipality_code: local.municipality_code || undefined,
    municipality_name: local.municipality_name || undefined,
    subregion: local.subregion || undefined,
    entity: local.entity || undefined,
    gender: (local.gender || undefined) as Gender | undefined,
    care_type: (local.care_type || undefined) as CareType | undefined,
    date_from: local.date_from || undefined,
    date_to: local.date_to || undefined,
    skip: local.skip,
    limit: local.limit
  }
}

const handleEntityChange = (value: string) => {
  local.entity = value
}

const handleEntitySelected = (entity: any | null) => {
  if (!entity) {
    local.entity = ''
    return
  }
  const nombre = (entity as any).nombre || (entity as any).name || ''
  local.entity = nombre
}

const handleMunicipalityCodeChange = (code: string) => {
  local.municipality_code = code
}

const handleMunicipalityNameChange = (name: string) => {
  local.municipality_name = name
}

const handleSubregionChange = (subregion: string) => {
  local.subregion = subregion
}

const handleRefresh = () => {
  emit('refresh')
}

const handleExport = () => {
  emit('export')
}

const handleSearch = () => {
  const filters = buildFilters()
  emit('update:modelValue', filters)
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
    created: '',
    date_from: '',
    date_to: '',
    skip: 0,
    limit: 100
  })

  entityCode.value = ''
  municipalityCode.value = ''

  const cleanedFilters = buildFilters()
  emit('update:modelValue', cleanedFilters)
  emit('search')
}
</script>
