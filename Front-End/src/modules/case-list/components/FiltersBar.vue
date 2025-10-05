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

    <div class="flex flex-col md:flex-row gap-3">
      <div class="flex-1">
        <label class="block text-sm font-medium text-gray-700 mb-1">Buscar por nombre, documento de identidad o caso</label>
        <FormInputField v-model="local.searchQuery" placeholder="Ejemplo 2025-00001, 123456789, Juan Pérez" @keydown.enter.prevent />
      </div>
      <div class="flex gap-3 items-end">
        <div class="w-44 md:w-56"><DateInputField v-model="local.dateFrom" label="Fecha desde" placeholder="DD/MM/AAAA" /></div>
        <div class="w-44 md:w-56"><DateInputField v-model="local.dateTo" label="Fecha hasta" placeholder="DD/MM/AAAA" /></div>
      </div>
    </div>

    <div class="flex flex-col md:flex-row gap-3 mt-3">
      <div class="flex-1">
        <PathologistList v-model="pathologistCode" label="Patólogo" :placeholder="isPatologo ? 'Patólogo fijo (usted)' : 'Buscar y seleccionar patólogo...'" :disabled="isPatologo" @pathologist-selected="onPathologistSelected" />
      </div>
      <div class="flex-1">
        <EntityList v-model="entityCode" label="Entidad" placeholder="Buscar y seleccionar entidad..." @entity-selected="onEntitySelected" />
      </div>
      <div class="flex-1">
        <TestList v-model="local.selectedTest" label="Pruebas" placeholder="Buscar y seleccionar prueba..." />
      </div>
      <div class="flex-1">
        <FormSelect v-model="local.selectedStatus" label="Estado" :options="statusOptions" placeholder="Seleccione estado" dense />
      </div>
    </div>

    <template #footer>
      <div class="flex flex-col sm:flex-row justify-end gap-2">
        <BaseButton size="sm" variant="outline" @click="clearAll"><template #icon-left><TrashIcon class="w-4 h-4 mr-1" /></template>Limpiar</BaseButton>
        <BaseButton size="sm" variant="outline" :disabled="!canExport" @click="$emit('export')"><template #icon-left><DocsIcon class="w-4 h-4 mr-1" /></template>Exportar a Excel</BaseButton>
        <BaseButton size="sm" variant="outline" :disabled="isLoading" @click="$emit('refresh')"><template #icon-left><RefreshIcon class="w-4 h-4 mr-1" /></template>Actualizar</BaseButton>
        <SearchButton text="Buscar" size="sm" :disabled="isLoading" @click="search" />
      </div>
    </template>
  </ComponentCard>
</template>

<script setup lang="ts">
import { reactive, ref, watch, computed, onMounted } from 'vue'
import { BaseButton, ComponentCard } from '@/shared/components'
import { RefreshIcon, DocsIcon, TrashIcon } from '@/assets/icons'
import { FormInputField, FormSelect, DateInputField } from '@/shared/components/ui/forms'
import { SearchButton } from '@/shared/components/ui/buttons'
import { EntityList, PathologistList, TestList } from '@/shared/components/ui/lists'
import type { Filters } from '../types/case.types'
import { getDefaultDateRange } from '../utils/dateUtils'
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
const emit = defineEmits<{ (e: 'update:modelValue', v: Filters): void; (e: 'refresh'): void; (e: 'export'): void; (e: 'search', v: Filters): void }>()

const { isPatologo } = usePermissions()
const authStore = useAuthStore()

const local = reactive<Filters>({ ...props.modelValue })
const pathologistCode = ref<string>('')
const entityCode = ref<string>('')

const currentPathologistName = computed(() => {
  if (!isPatologo.value || !authStore.user) return null
  let userName = (authStore.user as any).name || (authStore.user as any).username || (authStore.user as any).nombre || (authStore.user as any).nombres || (authStore.user as any).nombre_completo || (authStore.user as any).full_name || null
  if (!userName && ((authStore.user as any).nombres || (authStore.user as any).apellidos)) {
    const nombres = (authStore.user as any).nombres || ''
    const apellidos = (authStore.user as any).apellidos || ''
    userName = `${nombres} ${apellidos}`.trim()
  }
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

watch(currentPathologistName, (newName) => {
  if (newName && isPatologo.value) {
    local.searchPathologist = newName
  }
}, { immediate: true })

onMounted(() => {
  if (currentPathologistName.value && isPatologo.value) {
    local.searchPathologist = currentPathologistName.value
  }
  const defaults = getDefaultDateRange()
  local.dateFrom = normalizeToDDMMYYYY(local.dateFrom || defaults.dateFrom)
  local.dateTo = normalizeToDDMMYYYY(local.dateTo || defaults.dateTo)
})

const clearAll = () => {
  const defaultDates = getDefaultDateRange()
  local.searchQuery = ''
  if (!isPatologo.value) {
    local.searchPathologist = ''
  } else if (currentPathologistName.value) {
    local.searchPathologist = currentPathologistName.value
  }
  local.dateFrom = normalizeToDDMMYYYY(defaultDates.dateFrom)
  local.dateTo = normalizeToDDMMYYYY(defaultDates.dateTo)
  local.selectedEntity = ''
  local.selectedStatus = ''
  local.selectedTest = ''
  pathologistCode.value = ''
  entityCode.value = ''
  emit('update:modelValue', { ...local })
  emit('refresh')
}

const onPathologistSelected = (p: any | null) => {
  if (isPatologo.value && currentPathologistName.value) {
    local.searchPathologist = currentPathologistName.value
    return
  }
  local.searchPathologist = p?.nombre || ''
}

const onEntitySelected = (e: any | null) => {
  local.selectedEntity = e?.nombre || ''
}

const search = () => {
  emit('search', { ...local })
}



const normalizeToDDMMYYYY = (value: string | null | undefined): string => {
  if (!value) return ''
  const isoMatch = /^\d{4}-\d{2}-\d{2}/.test(value)
  if (isoMatch) {
    const [y, m, d] = value.slice(0, 10).split('-').map((v) => Number(v))
    return pad2(d) + '/' + pad2(m) + '/' + String(y)
  }
  const ddmmyyyy = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(value)
  if (ddmmyyyy) return value
  return ''
}

const pad2 = (n: number): string => n < 10 ? '0' + n : String(n)

const parseDDMMYYYY = (s: string): Date | null => {
  const m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(s)
  if (!m) return null
  const d = Number(m[1]), mo = Number(m[2]) - 1, y = Number(m[3])
  const dt = new Date(y, mo, d)
  return dt.getFullYear() === y && dt.getMonth() === mo && dt.getDate() === d ? dt : null
}

const clampToToday = (s: string): string => {
  const dt = parseDDMMYYYY(s)
  if (!dt) return ''
  const today = new Date(); today.setHours(0,0,0,0)
  if (dt > today) return normalizeToDDMMYYYY(`${today.getFullYear()}-${pad2(today.getMonth()+1)}-${pad2(today.getDate())}`)
  return s
}

watch(() => local.dateFrom, (v) => {
  if (!v) return
  const norm = clampToToday(normalizeToDDMMYYYY(v))
  if (norm !== v) local.dateFrom = norm
  if (local.dateTo) {
    const a = parseDDMMYYYY(local.dateFrom)
    const b = parseDDMMYYYY(local.dateTo)
    if (a && b && a > b) local.dateTo = local.dateFrom
  }
})

watch(() => local.dateTo, (v) => {
  if (!v) return
  const norm = clampToToday(normalizeToDDMMYYYY(v))
  if (norm !== v) local.dateTo = norm
  if (local.dateFrom) {
    const a = parseDDMMYYYY(local.dateFrom)
    const b = parseDDMMYYYY(local.dateTo)
    if (a && b && b < a) local.dateFrom = local.dateTo
  }
})
</script>


