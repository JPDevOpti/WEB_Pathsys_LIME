<template>
  <ComponentCard 
    title="Listado de Casos"
    description="Filtre los casos actuales por caso, paciente, patólogo, rango de fechas de creación, entidad, estado y pruebas."
  >
    <template #icon>
      <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </template>

    <!-- Fila de búsqueda principal -->
    <div class="flex flex-col md:flex-row gap-3">
      <div class="flex-1">
        <label class="block text-sm font-medium text-gray-700 mb-1">Buscar por nombre, documento de identidad o caso</label>
        <FormInputField
          v-model="local.searchQuery"
          placeholder="Ejemplo 2025-00001, 123456789, Juan Pérez"
          @keydown.enter.prevent
        />
      </div>
      <div class="w-full md:w-auto flex items-end">
        <SearchButton text="Buscar" size="md" :disabled="isLoading" @click="$emit('refresh')" />
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

    <!-- Fila de filtros secundarios -->
    <div class="flex flex-col md:flex-row gap-3 mt-3">
      <div class="flex-1">
        <PathologistList 
          v-model="pathologistCode" 
          label="Patólogo" 
          :placeholder="isPatologo ? 'Patólogo fijo (usted)' : 'Buscar y seleccionar patólogo...'" 
          :disabled="isPatologo"
          @pathologist-selected="onPathologistSelected" 
        />
      </div>
      <div class="flex-1">
        <EntityList v-model="entityCode" label="Entidad" placeholder="Buscar y seleccionar entidad..." @entity-selected="onEntitySelected" />
      </div>
      <div class="flex-1">
        <TestList v-model="local.selectedTest" label="Pruebas" placeholder="Buscar y seleccionar prueba..." />
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

    <!-- Footer con acciones -->
    <template #footer>
      <div class="flex flex-col sm:flex-row justify-end gap-2">
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
      </div>
    </template>
  </ComponentCard>
</template>

<script setup lang="ts">
import { reactive, ref, watch, computed, onMounted } from 'vue'
import { BaseButton, ComponentCard } from '@/shared/components'
import { RefreshIcon, DocsIcon, TrashIcon } from '@/assets/icons'
import { FormInputField, FormSelect, DateInputField } from '@/shared/components/forms'
import { SearchButton } from '@/shared/components/buttons'
import { EntityList, PathologistList, TestList } from '@/shared/components/List'
import type { Filters } from '../types/case.types'
import { getDefaultDateRange } from '../../utils/dateUtils'
import { usePermissions } from '@/shared/composables/usePermissions'
import { useAuthStore } from '@/stores/auth.store'

interface Props {
  modelValue: Filters
  totalFiltered: number
  totalAll: number
  isLoading?: boolean
  canExport?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{ (e: 'update:modelValue', v: Filters): void; (e: 'refresh'): void; (e: 'export'): void }>()

// Composable para permisos y autenticación
const { isPatologo } = usePermissions()
const authStore = useAuthStore()

const local = reactive<Filters>({ ...props.modelValue })

// Valores intermedios de componentes reutilizables
const pathologistCode = ref<string>('')
const entityCode = ref<string>('')

// Computed para obtener el nombre del patólogo logueado
const currentPathologistName = computed(() => {
  if (!isPatologo.value || !authStore.user) return null
  
  // Para patólogos, comparamos por NOMBRE
  let userName = (authStore.user as any).username || // username tiene el nombre completo
    authStore.user.nombre ||
    (authStore.user as any).nombres ||
    (authStore.user as any).nombre_completo ||
    (authStore.user as any).full_name ||
    null

  // Si no hay nombre completo, intentar construir desde nombres + apellidos
  if (!userName && ((authStore.user as any).nombres || (authStore.user as any).apellidos)) {
    const nombres = (authStore.user as any).nombres || ''
    const apellidos = (authStore.user as any).apellidos || ''
    userName = `${nombres} ${apellidos}`.trim()
  }

  // Si no hay nombre completo, intentar construir desde first_name + last_name
  if (!userName && ((authStore.user as any).first_name || (authStore.user as any).last_name)) {
    const firstName = (authStore.user as any).first_name || ''
    const lastName = (authStore.user as any).last_name || ''
    userName = `${firstName} ${lastName}`.trim()
  }

  return userName
})
const statusOptions = [
  { value: '', label: 'Todos' },
  { value: 'En proceso', label: 'En proceso' },
  { value: 'Por firmar', label: 'Por firmar' },
  { value: 'Por entregar', label: 'Por entregar' },
  { value: 'Completado', label: 'Completado' }
]

watch(() => props.modelValue, (v) => Object.assign(local, v))
watch(local, () => emit('update:modelValue', { ...local }), { deep: true })

// Watcher para mantener el patólogo logueado como filtro fijo
watch(currentPathologistName, (newName) => {
  if (newName && isPatologo.value) {
    local.searchPathologist = newName
  }
}, { immediate: true })

onMounted(() => {
  // Al montar el componente, si es patólogo, establecer su nombre como filtro
  if (currentPathologistName.value && isPatologo.value) {
    local.searchPathologist = currentPathologistName.value
  }
})

function clearAll() {
  const defaultDates = getDefaultDateRange()
  
  local.searchQuery = ''
  // NO limpiar el patólogo si el usuario es patólogo
  if (!isPatologo.value) {
    local.searchPathologist = ''
  } else if (currentPathologistName.value) {
    local.searchPathologist = currentPathologistName.value
  }
  local.dateFrom = defaultDates.dateFrom
  local.dateTo = defaultDates.dateTo
  local.selectedEntity = ''
  local.selectedStatus = ''
  local.selectedTest = ''
  pathologistCode.value = ''
  entityCode.value = ''
}

function onPathologistSelected(p: any | null) {
  // Si el usuario es patólogo, no permitir cambiar el patólogo seleccionado
  if (isPatologo.value && currentPathologistName.value) {
    // Mantener el patólogo logueado como filtro fijo
    local.searchPathologist = currentPathologistName.value
    return
  }
  
  local.searchPathologist = p?.nombre || ''
}

function onEntitySelected(e: any | null) {
  local.selectedEntity = e?.nombre || ''
}
</script>


