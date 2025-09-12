<template>
  <Modal
    v-model="isOpen"
    title="Detalles del Caso"
    size="lg"
    @close="emit('close')"
  >
          <div class="grid grid-cols-2 gap-4 bg-gray-50 rounded-xl p-4">
            <div>
              <p class="text-sm text-gray-500">Código del Caso</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem.codigo }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Estado</p>
              <p class="text-base font-medium text-red-700">{{ caseItem.estado }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Nombre del Paciente</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem.paciente.nombre }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Cédula</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem.paciente.cedula }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Entidad</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem.paciente.entidad || 'No especificada' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Patólogo Asignado</p>
              <p class="text-base font-medium text-gray-900">{{ caseItem.patologo || 'Sin asignar' }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Fecha de Creación</p>
              <p class="text-base font-medium text-gray-900">{{ formatDate(caseItem.fecha_creacion) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Días en Sistema</p>
              <p class="text-base font-medium text-gray-900" :class="daysClass(caseItem)">
                {{ caseItem.dias_en_sistema }} días
              </p>
            </div>
          </div>

          <div class="bg-gray-50 rounded-xl p-4 space-y-3">
            <h5 class="text-sm font-medium text-gray-700">Pruebas Solicitadas</h5>
            <div v-if="caseItem.pruebas && caseItem.pruebas.length" class="space-y-3">
              <div v-for="(prueba, pIdx) in caseItem.pruebas" :key="pIdx" class="border border-gray-200 rounded-lg p-3 bg-white">
                <span class="text-sm font-medium text-gray-900">{{ extractTestCode(prueba) }} - {{ getTestName(prueba) }}</span>
              </div>
            </div>
            <div v-else class="text-sm text-gray-500">Sin pruebas registradas</div>
          </div>

          <div class="bg-gray-50 rounded-xl p-4 space-y-2">
            <h5 class="text-sm font-medium text-gray-700">Información de Urgencia</h5>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <p class="text-sm text-gray-500">Prioridad</p>
                <p class="text-sm font-medium text-gray-900" :class="priorityClass(caseItem)">
                  {{ getPriorityLabel(caseItem) }}
                </p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Tiempo Restante</p>
                <p class="text-sm font-medium text-gray-900" :class="timeRemainingClass(caseItem)">
                  {{ getTimeRemaining(caseItem) }}
                </p>
              </div>
            </div>
          </div>
    
    <template #footer>
      <div class="flex justify-end gap-2">
        <PrintPdfButton text="Imprimir PDF" :caseCode="caseItem?.codigo" />
        <CloseButton
          @click="emit('close')"
          variant="danger-outline"
          size="md"
          text="Cerrar"
        />
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue'
import type { CasoUrgente } from '../types/dashboard.types'
import { CloseButton, PrintPdfButton } from '@/shared/components/buttons'
import { Modal } from '@/shared/components/layout'

const props = defineProps<{ caseItem: CasoUrgente | null }>()
const emit = defineEmits<{ 
  (e: 'close'): void; 
  (e: 'edit', caso: CasoUrgente): void; 
  (e: 'preview', caso: CasoUrgente): void; 
}>()

const modalContent = ref<HTMLElement>()

// Estado del modal principal
const isOpen = computed(() => !!props.caseItem)

// Función para centrar el scroll en la ventana modal
function centerScrollInModal() {
  if (modalContent.value) {
    nextTick(() => {
      modalContent.value?.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center',
        inline: 'center'
      })
    })
  }
}

// Watcher para centrar el scroll cuando se abre el modal
watch(() => props.caseItem, (newValue) => {
  if (newValue) {
    centerScrollInModal()
  }
}, { immediate: true })

function formatDate(dateString: string) {
  if (!dateString) return 'N/A'
  const d = new Date(dateString)
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function daysClass(caso: CasoUrgente): string {
  const days = caso.dias_en_sistema
  if (days > 6 && caso.estado !== 'Completado') return 'text-red-700'
  return 'text-blue-700'
}

function priorityClass(caso: CasoUrgente): string {
  const days = caso.dias_en_sistema
  if (days > 6 && caso.estado !== 'Completado') return 'text-red-700 font-semibold'
  if (days > 4 && caso.estado !== 'Completado') return 'text-orange-700 font-medium'
  return 'text-green-700'
}

function getPriorityLabel(caso: CasoUrgente): string {
  const days = caso.dias_en_sistema
  if (days > 6 && caso.estado !== 'Completado') return 'CRÍTICA'
  if (days > 4 && caso.estado !== 'Completado') return 'ALTA'
  return 'NORMAL'
}

function timeRemainingClass(caso: CasoUrgente): string {
  const days = caso.dias_en_sistema
  if (days > 6 && caso.estado !== 'Completado') return 'text-red-700 font-semibold'
  if (days > 4 && caso.estado !== 'Completado') return 'text-orange-700 font-medium'
  return 'text-green-700'
}

function getTimeRemaining(caso: CasoUrgente): string {
  const days = caso.dias_en_sistema
  if (days > 6 && caso.estado !== 'Completado') {
    return `${days - 6} días de retraso`
  }
  if (days > 4 && caso.estado !== 'Completado') {
    return `${6 - days} días restantes`
  }
  return 'Dentro del tiempo límite'
}

function extractTestCode(testString: string): string {
  const match = testString.match(/^\d{6}/)
  return match ? match[0] : testString.split(' - ')[0]
}

function getTestName(testString: string): string {
  const parts = testString.split(' - ')
  return parts.length > 1 ? parts.slice(1).join(' - ') : testString
}
</script>
