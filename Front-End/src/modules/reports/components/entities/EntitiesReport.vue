<template>
  <div class="space-y-6">
    <!-- Card de selección de período y acciones -->
    <ComponentCard title="Reporte de entidades" description="Seleccione mes y año para generar el informe.">
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

    <!-- Contenido del reporte -->
    <div v-else class="space-y-4">
      <div class="px-2">
        <h2 class="text-xl font-bold text-brand-700">Reporte de Entidades - {{ monthLabel }} {{ selectedYear }}</h2>
      </div>

      <EntitiesSummary :datos="entitiesData" :resumen="summary" />

      <EntitiesPerformanceChart :datos="entitiesData" />

      <ComponentCard title="Detalle por Entidad" description="Tabla con métricas detalladas. Haz clic en una fila para ver detalles completos.">
        <div v-if="entitiesData.length === 0" class="text-gray-500">No hay entidades con datos para el período seleccionado.</div>
        <div v-else>
          <EntitiesDetailTable :datos="entitiesData" @entity-click="openEntityModal" />
        </div>
      </ComponentCard>
    </div>

    <!-- Modal de detalles de la entidad -->
    <EntityDetailsModal 
      :entity="selectedEntity"
      :period="{ month: Number(selectedMonth) + 1, year: Number(selectedYear) }"
      @close="closeEntityModal"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { FormSelect } from '@/shared/components'
import { SaveButton, ClearButton } from '@/shared/components/buttons'
import { ComponentCard } from '@/shared/components/common'
import { RefreshIcon } from '@/assets/icons'
import EntitiesSummary from './EntitiesSummary.vue'
import EntitiesPerformanceChart from './EntitiesPerformanceChart.vue'
import EntitiesDetailTable from './EntitiesDetailTable.vue'
import EntityDetailsModal from './EntityDetailsModal.vue'
import type { EntityStats } from '../../types/entities.types'
import { entitiesApiService } from '../../services/entities.service'

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

// Cargar por defecto el mes anterior al actual
const selectedMonth = ref<string>(String(defaultMonthIndex))
const selectedYear = ref<string>(String(defaultYear))
const isLoading = ref(false)
const showReport = ref(false)
const selectedEntity = ref<EntityStats | null>(null)

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

const monthLabel = computed(() => {
  const idx = Number(selectedMonth.value)
  return Number.isFinite(idx) && monthsFull[idx] ? monthsFull[idx] : ''
})

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

const entitiesData = ref<EntityStats[]>([])
const summary = ref<any>(null)

// Cargar desde backend al generar
async function loadFromApi() {
  const api = await entitiesApiService.getMonthlyEntities(
    Number(selectedMonth.value) + 1, 
    Number(selectedYear.value)
  )
  entitiesData.value = api.entities
  summary.value = api.summary
}

// Funciones para el modal
function openEntityModal(entity: EntityStats) {
  selectedEntity.value = entity
}

function closeEntityModal() {
  selectedEntity.value = null
}
</script>