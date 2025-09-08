<template>
  <div class="space-y-6">
    <!-- Card de selección de período y acciones -->
    <ComponentCard title="Reporte de patólogos" description="Seleccione mes y año para generar el informe.">
      <div class="flex flex-wrap items-end gap-4">
        <!-- Mes -->
        <div class="flex-grow sm:flex-grow-0 sm:w-48">
          <FormSelect v-model="selectedMonth" label="Mes" :options="monthOptions" placeholder="Seleccione mes" />
        </div>
        <!-- Año -->
        <div class="flex-grow sm:flex-grow-0 sm:w-48">
          <FormSelect v-model="selectedYear" label="Año" :options="yearOptions" placeholder="Seleccione año" />
        </div>
        <!-- Botones -->
        <div class="flex items-center gap-2 flex-wrap">
          <SaveButton :loading="isLoading" :disabled="!selectedMonth || !selectedYear" :text="isLoading ? 'Generando...' : 'Generar Informe'" @click="generateReport" />
          <ClearButton @click="clearSelection">
            <template #icon><RefreshIcon class="w-4 h-4 mr-2" /></template>
            Limpiar
          </ClearButton>
        </div>
      </div>
    </ComponentCard>

    <!-- Card de vista previa (separada) -->
    <ComponentCard v-if="!showReport" title="Vista previa" description="Selecciona un período y genera el informe.">
      <div class="text-gray-600">Aún no se ha generado el informe. Selecciona mes y año y presiona "Generar Informe".</div>
    </ComponentCard>

    <!-- Contenido del reporte -->
    <div v-else class="space-y-4">
      <div class="px-2">
        <h2 class="text-xl font-bold text-brand-700">Reporte de Patólogos - {{ monthLabel }} {{ selectedYear }}</h2>
      </div>

      <PathologistPerformanceChart :datos="pathologistsData" />

      <ComponentCard title="Detalle por Patólogo" description="Tabla con métricas detalladas. Haz clic en una fila para ver detalles completos.">
        <div v-if="pathologistsData.length === 0" class="text-gray-500">No hay patólogos con datos para el período seleccionado.</div>
        <div v-else>
          <PathologistDetailTable :datos="pathologistsData" @pathologist-click="openPathologistModal" />
        </div>
      </ComponentCard>
    </div>

    <!-- Modal de detalles del patólogo -->
    <PathologistDetailsModal 
      :pathologist="selectedPathologist"
      :period="{ month: Number(selectedMonth) + 1, year: Number(selectedYear) }"
      @close="closePathologistModal"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { FormSelect } from '@/shared/components'
import { SaveButton, ClearButton } from '@/shared/components/buttons'
import { ComponentCard } from '@/shared/components/common'
import { RefreshIcon } from '@/assets/icons'
import PathologistPerformanceChart from './PathologistPerformanceChart.vue'
import PathologistDetailTable from './PathologistDetailTable.vue'
import PathologistDetailsModal from './PathologistDetailsModal.vue'
import type { PathologistMetrics } from '../../types/pathologists.types'
import { pathologistsApiService } from '../../services/pathologists.service'

const monthsFull = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
] as const

const now = new Date()
const currentYear = now.getFullYear()
const years = Array.from({ length: 5 }, (_, i) => currentYear - i)

// Selección por defecto: mes anterior al actual (ajustando año si corresponde)
const nowMonth = now.getMonth()
const defaultMonthIndex = (nowMonth + 11) % 12
const defaultYear = nowMonth === 0 ? currentYear - 1 : currentYear

const selectedMonth = ref<string>(String(defaultMonthIndex))
const selectedYear = ref<string>(String(defaultYear))
const isLoading = ref(false)
const showReport = ref(false)
const selectedPathologist = ref<PathologistMetrics | null>(null)

const monthOptions = computed(() => {
  const now = new Date()
  const currentYear = now.getFullYear()
  const currentMonth = now.getMonth()
  
  return monthsFull.map((m, idx) => {
    // Si estamos en el año actual, solo mostrar meses hasta el anterior al actual
    if (Number(selectedYear.value) === currentYear) {
      if (idx >= currentMonth) {
        return null // No mostrar meses futuros
      }
    }
    // Si es un año anterior, mostrar todos los meses
    return { value: String(idx), label: m }
  }).filter(option => option !== null) // Filtrar opciones nulas
})
const yearOptions = computed(() => years.map((y) => ({ value: String(y), label: String(y) })))

// Watcher para ajustar el mes cuando se cambie el año
watch(selectedYear, (newYear) => {
  const now = new Date()
  const currentYear = now.getFullYear()
  const currentMonth = now.getMonth()
  
  // Si se selecciona el año actual, verificar que el mes no sea futuro
  if (Number(newYear) === currentYear) {
    const selectedMonthIndex = Number(selectedMonth.value)
    if (selectedMonthIndex >= currentMonth) {
      // Si el mes seleccionado es futuro, cambiar al mes anterior al actual
      const previousMonth = (currentMonth + 11) % 12
      selectedMonth.value = String(previousMonth)
    }
  }
})

const monthLabel = computed(() => {
  const idx = Number(selectedMonth.value)
  return Number.isFinite(idx) && monthsFull[idx] ? monthsFull[idx] : ''
})

const generateReport = async () => {
  if (!selectedMonth.value || !selectedYear.value) return
  
  // Validar que no se esté intentando generar un reporte de un mes futuro
  const now = new Date()
  const currentYear = now.getFullYear()
  const currentMonth = now.getMonth()
  const selectedYearNum = Number(selectedYear.value)
  const selectedMonthNum = Number(selectedMonth.value)
  
  if (selectedYearNum > currentYear || (selectedYearNum === currentYear && selectedMonthNum >= currentMonth)) {
    console.warn('No se puede generar reporte para un mes futuro')
    return
  }
  
  isLoading.value = true
  try {
    await loadFromApi()
    showReport.value = true
  } finally {
    isLoading.value = false
  }
}

const clearSelection = () => {
  selectedMonth.value = ''
  selectedYear.value = ''
  showReport.value = false
}

const pathologistsData = ref<PathologistMetrics[]>([])

// Cargar desde backend al generar
async function loadFromApi() {
  const api = await pathologistsApiService.getMonthlyPathologists(Number(selectedMonth.value) + 1, Number(selectedYear.value))
  pathologistsData.value = api.pathologists
}

// Funciones para el modal
function openPathologistModal(pathologist: PathologistMetrics) {
  selectedPathologist.value = pathologist
}

function closePathologistModal() {
  selectedPathologist.value = null
}


</script>
