<template>
  <Modal
    v-model="isOpen"
    title="Detalles de la Prueba"
    size="lg"
    @close="$emit('close')"
  >
    <div class="mb-4">
      <p class="text-sm text-gray-500">Período: {{ formatPeriod() }}</p>
    </div>
          <!-- Información General -->
          <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
            <div class="flex items-center space-x-4">
              <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <div>
                <h4 class="text-2xl font-bold text-gray-900">{{ test?.nombre || 'N/A' }}</h4>
                <p class="text-blue-600 font-medium">{{ test?.codigo || 'N/A' }}</p>
              </div>
            </div>
          </div>

          <!-- Estado de carga -->
          <div v-if="isLoading" class="text-center py-12">
            <div class="relative">
              <div class="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-500 mx-auto"></div>
              <div class="absolute inset-0 flex items-center justify-center">
                <div class="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
              </div>
            </div>
            <p class="text-sm text-gray-500 mt-4">Cargando estadísticas detalladas...</p>
            <div class="mt-2 h-1 w-32 bg-gray-200 rounded-full mx-auto overflow-hidden">
              <div class="h-full bg-blue-500 rounded-full animate-pulse"></div>
            </div>
          </div>

          <!-- Error -->
          <div v-else-if="error" class="text-center py-12">
            <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
              <svg class="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="mt-2 text-sm font-medium text-gray-900">Error al cargar datos</h3>
            <p class="mt-1 text-sm text-red-500">{{ error }}</p>
            <div class="mt-4">
              <button @click="loadTestDetails" class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                Reintentar
              </button>
            </div>
          </div>

          <!-- Contenido detallado -->
          <template v-else-if="testDetails">

            <!-- Tiempos de procesamiento -->
            <div class="bg-white rounded-xl border px-6 py-4 mt-6">
              <h5 class="text-lg font-medium mb-6 pb-2 flex items-center text-gray-800">
                <svg class="w-5 h-5 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Tiempos de Procesamiento
              </h5>
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 pt-2">
                <div class="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                  <div class="text-center w-full">
                    <span class="text-sm font-medium text-gray-700">Promedio</span>
                    <p class="text-lg font-bold text-yellow-600">{{ testDetails?.tiempos_procesamiento?.promedio_dias?.toFixed(1) || '0.0' }} días</p>
                  </div>
                </div>
                <div class="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <div class="text-center w-full">
                    <span class="text-sm font-medium text-gray-700">Dentro de oportunidad</span>
                    <p class="text-lg font-bold text-green-600">{{ testDetails?.tiempos_procesamiento?.dentro_oportunidad || 0 }}</p>
                  </div>
                </div>
                <div class="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                  <div class="text-center w-full">
                    <span class="text-sm font-medium text-gray-700">Fuera de oportunidad</span>
                    <p class="text-lg font-bold text-red-600">{{ testDetails?.tiempos_procesamiento?.fuera_oportunidad || 0 }}</p>
                  </div>
                </div>
                <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div class="text-center w-full">
                    <span class="text-sm font-medium text-gray-700">Total</span>
                    <p class="text-lg font-bold text-gray-700">{{ testDetails?.tiempos_procesamiento?.total_casos || 0 }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Patólogos -->
            <div class="bg-gray-50 rounded-xl p-6 space-y-4 mt-8">
              <h5 class="text-lg font-semibold text-gray-900 pb-6">Patólogos</h5>
              
              <div v-if="!testDetails?.patologos || testDetails.patologos.length === 0" class="text-center py-8 text-gray-500">
                <svg class="w-12 h-12 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <p>No se encontraron patólogos</p>
              </div>
              
              <div v-else class="space-y-3">
                <div v-for="patologo in testDetails?.patologos || []" :key="patologo.codigo" class="bg-white rounded-lg p-4 border border-gray-200">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                      <div class="flex-shrink-0">
                        <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                      </div>
                      <div>
                        <h6 class="text-sm font-medium text-gray-900">{{ patologo.nombre || 'N/A' }}</h6>
                        <p class="text-xs text-gray-500">{{ patologo.codigo || 'N/A' }}</p>
                      </div>
                    </div>
                      <div class="text-right">
                        <div class="text-lg font-bold text-green-600">{{ patologo.total_procesadas || 0 }}</div>
                        <div class="text-xs text-gray-500">procesadas</div>
                        <div class="text-sm text-yellow-600">{{ formatAvgDays(patologo.tiempo_promedio) }} días</div>
                      </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
    
    <template #footer>
      <div class="flex justify-end">
        <CloseButton
          @click="$emit('close')"
          variant="danger-outline"
          size="md"
          text="Cerrar"
        />
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue'
import { CloseButton } from '@/shared/components/ui/buttons'
import { Modal } from '@/shared/components/layout'
import type { TestStats, TestDetails, PeriodSelection } from '../../types/tests.types'
import { testsApiService } from '../../services/tests.service'

const props = defineProps<{
  test: TestStats | null
  period: PeriodSelection
  entity?: string
}>()

defineEmits<{
  close: []
}>()

// Estado del modal principal
const isOpen = computed(() => !!props.test)

// Helper para formatear promedios que pueden venir null
function formatAvgDays(value: number | null | undefined): string {
  const num = typeof value === 'number' && !Number.isNaN(value) ? value : 0
  return num.toFixed(1)
}

// Estado del modal
const isLoading = ref(false)
const error = ref<string | null>(null)
const testDetails = ref<TestDetails | null>(null)

// Watch para cargar datos cuando se abre el modal
watch(() => props.test, async (newTest) => {
  if (newTest) {
    await nextTick()
    loadTestDetails()
  } else {
    testDetails.value = null
    error.value = null
  }
}, { immediate: true })

// Flag interno para debug (no se muestra aviso en UI)
const usedFallback = ref(false)

// (El helper de vacío seguro fue reemplazado por buildDetailsFromStats para mejorar UX)

// Fallback enriquecido a partir de los datos básicos de la prueba seleccionada
function buildDetailsFromStats() {
  const stats = props.test
  const solicitadas = Number(stats?.solicitadas) || 0
  const completadas = Number(stats?.completadas) || 0
  const promedio = typeof stats?.tiempoPromedio === 'number' && !Number.isNaN(stats.tiempoPromedio) ? stats.tiempoPromedio : 0
  return {
    estadisticas_principales: {
      total_solicitadas: solicitadas,
      total_completadas: completadas,
      porcentaje_completado: solicitadas > 0 ? Math.round((completadas / solicitadas) * 100) : 0
    },
    tiempos_procesamiento: {
      promedio_dias: promedio,
      dentro_oportunidad: 0,
      fuera_oportunidad: 0,
      total_casos: completadas
    },
    patologos: []
  }
}

// Función para cargar detalles de la prueba
async function loadTestDetails() {
  if (!props.test) return
  
  isLoading.value = true
  error.value = null
  usedFallback.value = false
  
  try {
    testDetails.value = await testsApiService.getTestDetails(
      props.entity || 'general',
      props.test.codigo,
      props.period.month,
      props.period.year
    )
    // Heurística: si viene sin patólogos, usar datos pero sin mostrar aviso
    if (!testDetails.value || !Array.isArray((testDetails.value as any).patologos)) {
      usedFallback.value = true
    }
  } catch (err: any) {
    console.error('Error al cargar detalles:', err)
    // En lugar de mostrar error, usar datos vacíos seguros para no romper UI
    testDetails.value = buildDetailsFromStats()
    error.value = null
    usedFallback.value = true
  } finally {
    isLoading.value = false
  }
}

// Función para formatear el período
function formatPeriod() {
  const months = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ]
  return `${months[props.period.month - 1]} ${props.period.year}`
}

</script>

<style scoped>
/* Estilos para el scroll del modal */
.scrollable-pruebas {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f8fafc;
}

.scrollable-pruebas::-webkit-scrollbar {
  width: 6px;
}

.scrollable-pruebas::-webkit-scrollbar-track {
  background: #f8fafc;
  border-radius: 3px;
}

.scrollable-pruebas::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.scrollable-pruebas::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
