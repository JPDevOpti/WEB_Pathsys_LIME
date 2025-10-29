<template>
  <Modal
    v-model="isOpen"
    title="Detalles de la Entidad"
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
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                </svg>
              </div>
              <div>
                <h4 class="text-2xl font-bold text-gray-900">{{ entity?.nombre || '' }}</h4>
                <p class="text-blue-600 font-medium">Entidad</p>
              </div>
            </div>
          </div>

          <!-- Métricas Principales -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 py-6">
            <div class="bg-green-50 border border-green-200 rounded-xl p-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-green-600 font-medium">Ambulatorios</p>
                  <p class="text-2xl font-bold text-green-700">{{ entity?.ambulatorios ?? 0 }}</p>
                  <p class="text-xs text-green-600">pacientes</p>
                </div>
                <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
              </div>
            </div>

            <div class="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-blue-600 font-medium">Hospitalizados</p>
                  <p class="text-2xl font-bold text-blue-700">{{ entity?.hospitalizados ?? 0 }}</p>
                  <p class="text-xs text-blue-600">pacientes</p>
                </div>
                <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                  </svg>
                </div>
              </div>
            </div>

            <div class="bg-gray-50 border border-gray-200 rounded-xl p-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-gray-600 font-medium">Total</p>
                  <p class="text-2xl font-bold text-gray-700">{{ entity?.total ?? 0 }}</p>
                  <p class="text-xs text-gray-600">pacientes</p>
                </div>
                <div class="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
                  <UserGroupIcon class="w-6 h-6 text-gray-600" />
                </div>
              </div>
            </div>
          </div>

          <!-- Pruebas y Patólogos -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
            <!-- Mensaje cuando no hay datos -->
            <div v-if="!isLoadingTests && !isLoadingPathologists && !hasData()" class="lg:col-span-2">
              <div class="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center">
                <svg class="w-12 h-12 mx-auto text-yellow-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                <h5 class="text-lg font-semibold text-yellow-800 mb-2">No hay datos disponibles</h5>
                <p class="text-yellow-700 mb-4">No se encontraron datos para la entidad <strong>{{ entity?.nombre || '' }}</strong> en {{ formatPeriod() }}.</p>
                <div class="text-sm text-yellow-600">
                  <p>Sugerencias:</p>
                  <ul class="mt-2 space-y-1">
                    <li>• Verifica que la entidad tenga casos registrados</li>
                    <li>• Intenta con un período diferente</li>
                    <li>• Asegúrate de que los datos estén cargados en el sistema</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <!-- Contenido cuando hay datos -->
            <template v-else>
              <!-- Pruebas más solicitadas -->
              <div class="bg-gray-50 rounded-xl p-6 space-y-4">
                <h5 class="text-lg font-semibold text-gray-900">Pruebas más solicitadas</h5>
                
                <div v-if="isLoadingTests" class="flex items-center justify-center py-8">
                  <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span class="ml-2 text-gray-600">Cargando pruebas...</span>
                </div>
                
                <div v-else-if="!entityDetails" class="text-center py-8 text-gray-500">
                  <svg class="w-12 h-12 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  <p class="font-medium text-gray-600">No se pudieron cargar los datos</p>
                  <p class="text-sm text-gray-400 mt-1">Error al obtener detalles de la entidad</p>
                </div>
                
                <div v-else-if="entityDetails?.pruebas_mas_solicitadas?.length === 0" class="text-center py-8 text-gray-500">
                  <svg class="w-12 h-12 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  <p class="font-medium text-gray-600">No se encontraron pruebas</p>
                  <p class="text-sm text-gray-400 mt-1">No hay datos de pruebas para {{ formatPeriod() }}</p>
                </div>
                
                <div v-else-if="entityDetails?.pruebas_mas_solicitadas" class="space-y-3">
                  <div v-for="prueba in entityDetails.pruebas_mas_solicitadas" :key="prueba.codigo" class="bg-white rounded-lg p-4 border border-gray-200">
                    <div class="flex items-center justify-between">
                      <div class="flex items-center space-x-3">
                        <div class="flex-shrink-0">
                          <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                          </svg>
                        </div>
                        <div>
                          <h6 class="text-sm font-medium text-gray-900">{{ prueba.nombre || prueba.codigo }}</h6>
                          <p class="text-xs text-gray-500">{{ prueba.codigo }}</p>
                        </div>
                      </div>
                      <div class="text-right">
                        <div class="text-lg font-bold text-blue-600">{{ prueba.total_solicitudes }}</div>
                        <div class="text-xs text-gray-500">solicitudes</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

                            <!-- Patólogos que han trabajado -->
              <div class="bg-gray-50 rounded-xl p-6 space-y-4">
                <h5 class="text-lg font-semibold text-gray-900">Patólogos</h5>
                
                <div v-if="isLoadingPathologists" class="flex items-center justify-center py-8">
                  <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
                  <span class="ml-2 text-gray-600">Cargando patólogos...</span>
                </div>
                
                <div v-else-if="pathologistsData.length === 0" class="text-center py-8 text-gray-500">
                  <svg class="w-12 h-12 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  <p class="font-medium text-gray-600">No se encontraron patólogos</p>
                  <p class="text-sm text-gray-400 mt-1">No hay datos de patólogos para {{ formatPeriod() }}</p>
                </div>
                
                <div v-else class="space-y-3">
                  <div v-for="pathologist in pathologistsData" :key="pathologist.name" class="bg-white rounded-lg p-4 border border-gray-200">
                    <div class="flex items-center justify-between">
                      <div class="flex items-center space-x-3">
                        <div class="flex-shrink-0">
                          <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                        </div>
                        <div>
                          <h6 class="text-sm font-medium text-gray-900">{{ pathologist.name }}</h6>
                          <p class="text-xs text-gray-500">{{ pathologist.codigo }}</p>
                        </div>
                      </div>
                      <div class="text-right">
                        <div class="text-lg font-bold text-green-600">{{ pathologist.casesCount }}</div>
                        <div class="text-xs text-gray-500">casos</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </div>
        
    
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
import { computed, ref, watch } from 'vue'
import { UserGroupIcon } from '@/assets/icons'
import { CloseButton } from '@/shared/components/ui/buttons'
import { Modal } from '@/shared/components/layout'
import type { EntityStats, EntityDetails, PeriodSelection } from '../../types/entities.types'
import { entitiesApiService } from '../../services/entities.service'

const props = defineProps<{
  entity: EntityStats | null
  period: PeriodSelection
}>()

const emit = defineEmits<{
  close: []
}>()

// Estado del modal principal
const isOpen = computed(() => !!props.entity)

// Estado del modal
const entityDetails = ref<EntityDetails | null>(null)

// Estado para patólogos
const pathologistsData = ref<Array<{name: string, codigo: string, casesCount: number}>>([])
const isLoadingPathologists = ref(false)
const isLoadingTests = ref(false)

// Watch para cargar datos cuando se abre el modal
watch(() => props.entity, async (newEntity) => {
  if (newEntity) {
    await Promise.all([
      loadEntityDetails(),
      loadPathologists()
    ])
  } else {
    entityDetails.value = null
    pathologistsData.value = []
  }
}, { immediate: true })

// Función para cargar detalles de la entidad
const loadEntityDetails = async () => {
  if (!props.entity) return
  
  try {
    isLoadingTests.value = true
    const periodString = `${props.period.year}-${props.period.month.toString().padStart(2, '0')}`
    const response = await entitiesApiService.getEntityDetails(props.entity.codigo, periodString)
    entityDetails.value = response
  } catch (error) {
    console.error('Error al cargar detalles de la entidad:', error)
  } finally {
    isLoadingTests.value = false
  }
}

// Función para cargar patólogos de la entidad
const loadPathologists = async () => {
  if (!props.entity) return
  
  try {
    isLoadingPathologists.value = true
    const periodString = `${props.period.year}-${props.period.month.toString().padStart(2, '0')}`
    const response = await entitiesApiService.getEntityPathologists(
      props.entity.codigo,
      periodString
    )
    
    pathologistsData.value = response.map((patologo: any) => ({
      name: patologo.nombre,
      codigo: patologo.codigo,
      casesCount: patologo.totalCasos || patologo.casesCount || 0
    }))
  } catch (error) {
    console.error('Error al cargar patólogos de la entidad:', error)
  } finally {
    isLoadingPathologists.value = false
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

// Función para verificar si hay datos disponibles
function hasData() {
  // Si el listado ya reporta casos para la entidad en el período, considerar que hay datos
  const totalsFromList = (
    (props.entity?.total ?? 0) > 0 ||
    (props.entity?.ambulatorios ?? 0) > 0 ||
    (props.entity?.hospitalizados ?? 0) > 0
  )
  if (totalsFromList) return true

  // Si no hay detalles cargados aún y el listado no muestra casos, no hay datos
  if (!entityDetails.value) return false

  // Evaluar datos provenientes del endpoint de detalles
  const basicas = entityDetails.value.estadisticas_basicas
  return basicas.total_pacientes > 0 || 
         basicas.ambulatorios > 0 || 
         basicas.hospitalizados > 0 ||
         (entityDetails.value.pruebas_mas_solicitadas && entityDetails.value.pruebas_mas_solicitadas.length > 0) ||
         pathologistsData.value.length > 0
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

/* Estilos para el gráfico de ApexCharts */
:deep(.apexcharts-tooltip) {
  background: #fff !important;
  border: 1px solid #e5e7eb !important;
  border-radius: 8px !important;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
}

:deep(.apexcharts-tooltip-title) {
  background: #f9fafb !important;
  border-bottom: 1px solid #e5e7eb !important;
  font-weight: 600 !important;
  color: #374151 !important;
}

:deep(.apexcharts-legend-text) {
  font-size: 14px !important;
  font-weight: 500 !important;
  color: #6b7280 !important;
}

:deep(.apexcharts-datalabel-label) {
  font-size: 12px !important;
  font-weight: 600 !important;
}

:deep(.apexcharts-datalabel-value) {
  font-size: 14px !important;
  font-weight: 700 !important;
}
</style>
