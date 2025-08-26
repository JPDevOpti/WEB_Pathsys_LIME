<template>
  <div class="space-y-6">
    <!-- Card de selección de período y acciones -->
    <ComponentCard title="Reporte de Oportunidades general del laboratorio" description="Seleccione mes y año para generar el informe.">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
        <FormSelect v-model="selectedMonth" label="Mes" :options="monthOptions" placeholder="Seleccione mes" />
        <FormSelect v-model="selectedYear" label="Año" :options="yearOptions" placeholder="Seleccione año" />
        <div class="flex items-end gap-2">
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

    <!-- Contenido del reporte (placeholder inicial) -->
    <div v-else class="space-y-4">
      <div class="px-2">
        <h2 class="text-xl font-bold text-brand-700">Reporte de Oportunidad - {{ monthLabel }} {{ selectedYear }}</h2>
      </div>
      <OpportunitySummary :datos="testsForSelection" :monthlyPct="monthlyPct" :resumen="summary || undefined" />

      <PathologistsPerformancePanel :datos="pathologistsForSelection" />

      <ComponentCard title="Detalle por Procedimiento" description="Paneles por prueba.">
        <div v-if="testsForSelection.length === 0" class="text-gray-500">No hay procedimientos para el período seleccionado.</div>
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          <TestsOpportunityPanel v-for="t in testsForSelection" :key="t.code" :prueba="t" />
        </div>
      </ComponentCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { FormSelect } from '@/shared/components/ui'
import { SaveButton, ClearButton } from '@/shared/components/ui/buttons'
import { ComponentCard } from '@/shared/components/common'
import { RefreshIcon } from '@/assets/icons'
import OpportunitySummary from './OpportunitySummary.vue'
import TestsOpportunityPanel from './TestsOpportunityPanel.vue'
import PathologistsPerformancePanel from './PathologistsPerformancePanel.vue'
import type { OpportunityTest, PathologistPerformance } from '../../types/opportunity.types'
import { opportunityApiService } from '../../services/opportunity.service'

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

// imprimir desactivado por ahora

const apiTests = ref<OpportunityTest[]>([])
const apiPathologists = ref<PathologistPerformance[]>([])
const summary = ref<{ total: number; within: number; out: number } | null>(null)

const testsForSelection = computed<OpportunityTest[]>(() => apiTests.value)

const pathologistsForSelection = computed<PathologistPerformance[]>(() => apiPathologists.value)

const monthlyPct = ref<number[]>([])

// Cargar desde backend al generar
async function loadFromApi() {
  const api = await opportunityApiService.getMonthlyOpportunity(Number(selectedMonth.value) + 1, Number(selectedYear.value))
  apiTests.value = api.tests
  apiPathologists.value = api.pathologists
  summary.value = api.summary || null
  // Cargar serie anual para el gráfico de líneas (enero -> mes anterior)
  const year = Number(selectedYear.value)
  const yearly = await opportunityApiService.getYearlyOpportunity(year)
  monthlyPct.value = yearly
}


</script>


