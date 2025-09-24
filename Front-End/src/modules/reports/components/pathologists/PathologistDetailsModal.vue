<template>
  <Modal
    v-model="isOpen"
    title="Detalles del Patólogo"
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
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
              </div>
              <div>
                <h4 class="text-2xl font-bold text-gray-900">{{ pathologist?.name || 'N/A' }}</h4>
                <p class="text-blue-600 font-medium">Patólogo</p>
              </div>
            </div>
          </div>

          <!-- Métricas Principales -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8 mt-4">
            <div class="bg-green-50 border border-green-200 rounded-xl p-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-green-600 font-medium">Dentro de Oportunidad</p>
                  <p class="text-2xl font-bold text-green-700">{{ pathologist?.withinOpportunity || 0 }}</p>
                  <p class="text-xs text-green-600">casos</p>
                </div>
                <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                  <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                </div>
              </div>
            </div>

            <div class="bg-red-50 border border-red-200 rounded-xl p-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-red-600 font-medium">Fuera de Oportunidad</p>
                  <p class="text-2xl font-bold text-red-700">{{ pathologist?.outOfOpportunity || 0 }}</p>
                  <p class="text-xs text-red-600">casos</p>
                </div>
                <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                  <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </div>
              </div>
            </div>

            <div class="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-blue-600 font-medium">Tiempo Promedio</p>
                  <p class="text-2xl font-bold text-blue-700">{{ pathologist?.averageDays || 0 }} días</p>
                  <p class="text-xs text-blue-600">por caso</p>
                </div>
                <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- Entidades y Pruebas -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8 mt-4">
            <!-- Entidades donde trabaja -->
            <div class="bg-gray-50 rounded-xl p-6 space-y-4">
              <h5 class="text-lg font-semibold text-gray-900">Entidades donde trabaja</h5>
              
              <div v-if="isLoadingEntities" class="flex items-center justify-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span class="ml-2 text-gray-600">Cargando entidades...</span>
              </div>
              
              <div v-else-if="entitiesData.length === 0" class="text-center py-8 text-gray-500">
                <svg class="w-12 h-12 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                </svg>
                <p>No se encontraron entidades</p>
              </div>
              
              <div v-else class="space-y-3">
                <div v-for="entity in entitiesData" :key="entity.name" class="bg-white rounded-lg p-4 border border-gray-200">
                  <div class="flex items-center justify-between">
                                      <div class="flex items-center space-x-3">
                    <div class="flex-shrink-0">
                      <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                      </svg>
                    </div>
                      <div>
                        <h6 class="text-sm font-medium text-gray-900">{{ entity.name }}</h6>
                        <p class="text-xs text-gray-500">{{ entity.codigo }}</p>
                      </div>
                    </div>
                    <div class="text-right">
                      <div class="text-lg font-bold text-blue-600">{{ entity.casesCount }}</div>
                      <div class="text-xs text-gray-500">casos</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Pruebas realizadas -->
            <div class="bg-gray-50 rounded-xl p-6 space-y-4">
              <h5 class="text-lg font-semibold text-gray-900">Pruebas realizadas</h5>
              
              <div v-if="isLoadingTests" class="flex items-center justify-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
                <span class="ml-2 text-gray-600">Cargando pruebas...</span>
              </div>
              
              <div v-else-if="testsData.length === 0" class="text-center py-8 text-gray-500">
                <svg class="w-12 h-12 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p>No se encontraron pruebas</p>
              </div>
              
              <div v-else class="space-y-3">
                <div v-for="test in testsData" :key="test.name" class="bg-white rounded-lg p-4 border border-gray-200">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                      <div class="flex-shrink-0">
                        <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                      </div>
                      <div>
                        <h6 class="text-sm font-medium text-gray-900">{{ test.name }}</h6>
                        <p class="text-xs text-gray-500">{{ test.codigo }}</p>
                      </div>
                    </div>
                    <div class="text-right">
                      <div class="text-lg font-bold text-green-600">{{ test.count }}</div>
                      <div class="text-xs text-gray-500">realizadas</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
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
import { CloseButton } from '@/shared/components/buttons'
import { Modal } from '@/shared/components/layout'
import type { PathologistMetrics, PeriodSelection } from '../../types/pathologists.types'
import { pathologistsApiService } from '../../services/pathologists.service'

interface EntityData {
  name: string
  type: string
  codigo: string
  casesCount: number
}

interface TestData {
  name: string
  category: string
  codigo: string
  count: number
}

interface Props {
  pathologist: PathologistMetrics | null
  period: PeriodSelection
}

const props = defineProps<Props>()
defineEmits<{ (e: 'close'): void }>()

// Estado del modal principal
const isOpen = computed(() => !!props.pathologist)

// Estado para entidades
const entitiesData = ref<EntityData[]>([])
const isLoadingEntities = ref(false)

// Estado para pruebas
const testsData = ref<TestData[]>([])
const isLoadingTests = ref(false)

// Computed properties

// Helper functions

function formatPeriod(): string {
  const months = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ]
  return `${months[props.period.month - 1]} ${props.period.year}`
}

// Cargar entidades cuando se abre el modal
async function loadEntities() {
  if (!props.pathologist) return
  
  isLoadingEntities.value = true
  try {
    const response = await pathologistsApiService.getPathologistEntities(
      props.pathologist.name,
      props.period.month,
      props.period.year
    )
    
    entitiesData.value = response.entidades || []
  } catch (error) {
    console.error('Error cargando entidades:', error)
    entitiesData.value = []
  } finally {
    isLoadingEntities.value = false
  }
}

// Cargar pruebas cuando se abre el modal
async function loadTests() {
  if (!props.pathologist) return
  
  isLoadingTests.value = true
  try {
    const response = await pathologistsApiService.getPathologistTests(
      props.pathologist.name,
      props.period.month,
      props.period.year
    )
    
    testsData.value = response.pruebas || []
  } catch (error) {
    console.error('Error cargando pruebas:', error)
    testsData.value = []
  } finally {
    isLoadingTests.value = false
  }
}

// Watch para cargar datos cuando cambia el patólogo
watch(() => props.pathologist, (newPathologist) => {
  if (newPathologist) {
    loadEntities()
    loadTests()
  } else {
    entitiesData.value = []
    testsData.value = []
  }
}, { immediate: true })

</script>
