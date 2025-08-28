<template>
  <div class="space-y-6">
    <!-- Card de selección de período, entidad, estado y acciones -->
    <ComponentCard title="Reporte de pruebas realizadas" description="Seleccione período, entidad y estado para generar el informe.">

      
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <FormSelect v-model="selectedMonth" label="Mes" :options="monthOptions" placeholder="Seleccione mes" />
        <FormSelect v-model="selectedYear" label="Año" :options="yearOptions" placeholder="Seleccione año" />
        <EntityList 
          v-model="selectedEntity" 
          label="Entidad" 
          placeholder="Buscar y seleccionar entidad..."
          @entity-selected="handleEntitySelected"
          @load-error="handleEntityLoadError"
        />
        <div class="flex items-end gap-2">
          <SaveButton :loading="isLoading" :disabled="!selectedMonth || !selectedYear || !backendConnected" :text="isLoading ? 'Generando...' : 'Generar Informe'" @click="generateReport" />
          <ClearButton @click="clearSelection">
            <template #icon><RefreshIcon class="w-4 h-4 mr-2" /></template>
            Limpiar
          </ClearButton>
        </div>
      </div>
    </ComponentCard>

    <!-- Estado de conectividad con el backend -->
    <div v-if="!backendConnected" class="bg-red-50 border border-red-200 rounded-xl p-4">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <h3 class="text-sm font-medium text-red-800">Error de conectividad</h3>
          <p class="text-sm text-red-700 mt-1">No se puede conectar con el backend. Verifique que el servidor esté ejecutándose.</p>
        </div>
        <button @click="checkBackendConnection" class="ml-auto px-3 py-1 text-sm bg-red-100 text-red-700 rounded-md hover:bg-red-200">
          Reintentar
        </button>
      </div>
    </div>

    <!-- Card de vista previa (separada) -->
    <ComponentCard v-if="!showReport && !isLoading" title="Vista previa" description="Selecciona un período y genera el informe.">
      <div class="text-gray-600">Aún no se ha generado el informe. Selecciona mes y año y presiona "Generar Informe".</div>
    </ComponentCard>

    <!-- Estado de carga -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="relative">
        <div class="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-500 mx-auto"></div>
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
        </div>
      </div>
      <p class="text-sm text-gray-500 mt-4">Generando reporte...</p>
      <div class="mt-2 h-1 w-32 bg-gray-200 rounded-full mx-auto overflow-hidden">
        <div class="h-full bg-blue-500 rounded-full animate-pulse"></div>
      </div>
    </div>

    <!-- Error en la generación del reporte -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-4">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <h3 class="text-sm font-medium text-red-800">Error al generar reporte</h3>
          <p class="text-sm text-red-700 mt-1">{{ error }}</p>
        </div>
        <button @click="generateReport" class="ml-auto px-3 py-1 text-sm bg-red-100 text-red-700 rounded-md hover:bg-red-200">
          Reintentar
        </button>
      </div>
    </div>

    <!-- Contenido del reporte -->
    <div v-else-if="showReport && !isLoading" class="space-y-4">
      <div class="px-2">
        <h2 class="text-xl font-bold text-brand-700">
          Reporte de Pruebas - {{ monthLabel }} {{ selectedYear }}
          <span v-if="selectedEntityLabel" class="text-sm font-normal text-gray-600 ml-2">
            - {{ selectedEntityLabel }}
          </span>
        </h2>
      </div>

      <TestsSummary :datos="testsData" :resumen="summary" />

      <TestsPerformanceChart :datos="testsData" />

      <ComponentCard title="Detalle por Prueba" description="Tabla con métricas detalladas. Haz clic en una fila para ver detalles completos.">
        <div v-if="testsData.length === 0" class="text-gray-500">No hay pruebas con datos para el período seleccionado.</div>
        <div v-else>
          <TestsDetailTable :datos="testsData" @test-click="openTestModal" />
        </div>
      </ComponentCard>
    </div>

    <!-- Modal de detalles de la prueba -->
    <TestDetailsModal 
      :test="selectedTest"
      :period="{ month: Number(selectedMonth) + 1, year: Number(selectedYear) }"
      :entity="selectedEntity || ''"
      @close="closeTestModal"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue'
import { FormSelect } from '@/shared/components'
import { EntityList } from '@/shared/components/List'
import { SaveButton, ClearButton } from '@/shared/components/buttons'
import { ComponentCard } from '@/shared/components/common'
import { RefreshIcon } from '@/assets/icons'
import TestsSummary from './TestsSummary.vue'
import TestsPerformanceChart from './TestsPerformanceChart.vue'
import TestsDetailTable from './TestsDetailTable.vue'
import TestDetailsModal from './TestDetailsModal.vue'
import type { TestStats } from '../../types/tests.types'
import type { EntityInfo } from '@/modules/cases/types/case'
import { testsApiService } from '../../services/tests.service'

// Configuración de meses y años
const monthsFull = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
] as const

const now = new Date()
const currentYear = now.getFullYear()
const years = Array.from({ length: 5 }, (_, i) => currentYear - i)

// Selección por defecto: mes anterior al actual pero manteniendo el año actual
const nowMonth = now.getMonth()
const defaultMonthIndex = (nowMonth + 11) % 12
const defaultYear = currentYear  // Siempre usar el año actual (2025)

const selectedMonth = ref<string>(String(defaultMonthIndex))
const selectedYear = ref<string>(String(defaultYear))
const selectedEntity = ref<string>('')
const isLoading = ref(false)
const showReport = ref(false)
const selectedTest = ref<TestStats | null>(null)
const error = ref<string | null>(null)
const backendConnected = ref(true)
const isCheckingConnection = ref(false)

// Datos del reporte
const testsData = ref<TestStats[]>([])
const summary = ref<any>(null)

// Estado para la entidad seleccionada
const selectedEntityInfo = ref<EntityInfo | null>(null)

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

const selectedEntityLabel = computed(() => {
  return selectedEntityInfo.value?.nombre || ''
})

// Verificar conectividad con el backend al montar el componente
onMounted(async () => {
  await checkBackendConnection()
})

// Función para verificar la conectividad con el backend
async function checkBackendConnection() {
  isCheckingConnection.value = true
  try {
    backendConnected.value = await testsApiService.checkBackendConnection()
  } catch (error) {
    console.error('Error al verificar conectividad:', error)
    backendConnected.value = false
  } finally {
    isCheckingConnection.value = false
  }
}

// Handlers para EntityList
const handleEntitySelected = (entity: EntityInfo | null) => {
  selectedEntityInfo.value = entity
  selectedEntity.value = entity?.codigo || ''
}

const handleEntityLoadError = (error: string) => {
  console.error('Error al cargar entidades:', error)
  // Aquí podrías mostrar una notificación al usuario si lo deseas
}

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
  error.value = null
  showReport.value = false
  
  try {
    await loadFromApi()
    showReport.value = true
  } catch (err: any) {
    error.value = err.message || 'Error al generar el reporte'
    showReport.value = false
  } finally {
    isLoading.value = false
  }
}

const clearSelection = () => {
  selectedMonth.value = String(defaultMonthIndex)
  selectedYear.value = String(defaultYear)
  selectedEntity.value = ''
  selectedEntityInfo.value = null
  showReport.value = false
  error.value = null
}

// Cargar desde backend al generar
async function loadFromApi() {
  const api = await testsApiService.getMonthlyTests(
    Number(selectedMonth.value) + 1, 
    Number(selectedYear.value),
    selectedEntity.value || undefined
  )
  testsData.value = api.tests
  summary.value = api.summary
}

// Funciones para el modal
function openTestModal(test: TestStats) {
  selectedTest.value = test
}

function closeTestModal() {
  selectedTest.value = null
}
</script>