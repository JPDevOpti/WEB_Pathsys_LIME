<template>
  <transition enter-active-class="transition ease-out duration-300" enter-from-class="opacity-0 transform scale-95" enter-to-class="opacity-100 transform scale-100" leave-active-class="transition ease-in duration-200" leave-from-class="opacity-100 transform scale-100" leave-to-class="opacity-0 transform scale-95">
    <div v-if="caseItem" class="fixed inset-0 z-50 flex items-start justify-center p-4 pt-20" @click.self="emit('close')">
      <!-- Debug info -->
      <div class="absolute top-0 left-0 bg-red-500 text-white p-2 text-xs z-50">
        Modal visible - caseItem: {{ caseItem?.codigo }}
      </div>
      <div ref="modalContent" class="relative bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto overflow-x-hidden">
        <div class="sticky top-0 z-10 bg-white border-b border-gray-200 px-6 py-4 rounded-t-2xl flex items-center justify-between">
          <h3 class="text-xl font-semibold text-gray-900">Detalles del Caso</h3>
          <button @click="emit('close')" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div class="p-6 space-y-6">
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
        </div>
        <div class="sticky bottom-0 bg-white border-t border-gray-200 px-6 py-4 rounded-b-2xl flex flex-col sm:flex-row sm:justify-between gap-3">
          <div class="flex gap-2">
            <!-- Botón de previsualización temporalmente deshabilitado -->
          </div>
          <div class="flex gap-2 justify-end">
            <ActionButton variant="secondary" :text="'Cerrar'" @action="emit('close')" />
            <ActionButton :text="'Editar Caso'" @action="emit('edit', caseItem)" />
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import type { CasoUrgente } from '../types/dashboard.types'
import { ActionButton } from '@/shared/components/buttons'

const props = defineProps<{ caseItem: CasoUrgente | null }>()
const emit = defineEmits<{ 
  (e: 'close'): void; 
  (e: 'edit', caso: CasoUrgente): void; 
  (e: 'preview', caso: CasoUrgente): void; 
}>()

// Watcher para centrar el scroll cuando se abre el modal
watch(() => props.caseItem, (newValue) => {
  if (newValue) {
    centerScrollInModal()
  }
}, { immediate: true })

const modalContent = ref<HTMLElement>()

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

// Watch para centrar el scroll cuando se abre el modal
watch(() => props.caseItem, (newCase) => {
  if (newCase) {
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
