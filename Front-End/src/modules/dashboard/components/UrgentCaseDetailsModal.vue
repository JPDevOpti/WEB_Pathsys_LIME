<template>
  <!-- Modal con detalles del caso urgente -->
  <Modal v-model="isOpen" title="Detalles del Caso" size="lg" @close="emit('close')">
    <div v-if="caseItem" class="space-y-5">
      <!-- Encabezado con icono, código, paciente y badges -->
      <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
        <div class="px-6 py-5 border-b border-gray-200">
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0">
              <div class="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center">
                <CaseIcon class="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-3">
                <div class="min-w-0">
                  <h3 class="text-xl font-bold text-gray-900 mb-1">Caso Urgente</h3>
                  <div class="flex items-center flex-wrap gap-2">
                    <div class="flex items-center gap-1.5">
                      <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Código</span>
                      <span class="text-lg font-bold text-gray-900 font-mono">{{ caseItem.codigo }}</span>
                    </div>
                    <div class="flex items-center gap-1.5">
                      <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Paciente</span>
                      <span class="text-lg font-semibold text-gray-900 truncate">{{ caseItem.paciente.nombre }}</span>
                    </div>
                  </div>
                </div>
                <div class="flex flex-wrap gap-2">
                  <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold" :class="getCaseStatusClass(caseItem.estado)">
                    {{ caseItem.estado }}
                  </span>
                  <span :class="['inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border', priorityBadgeClasses]">
                    {{ caseItem.prioridad }}
                  </span>
                  <span :class="['inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold', daysBadgeClasses]">
                    {{ caseItem.dias_en_sistema }} días
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tarjetas de información del paciente, entidad y patólogo -->
        <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-3">
          <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
            <div class="flex items-center space-x-2">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                  <ProfileIcon class="w-4 h-4 text-gray-700" />
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Documento</p>
                <p class="text-sm font-bold text-gray-900 font-mono">{{ caseItem.paciente.cedula || '—' }}</p>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
            <div class="flex items-center space-x-2">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                  <EntityIcon class="w-4 h-4 text-gray-700" />
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Entidad</p>
                <p class="text-sm font-bold text-gray-900 break-words">{{ caseItem.paciente.entidad || 'No especificada' }}</p>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
            <div class="flex items-center space-x-2">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                  <DoctorIcon class="w-4 h-4 text-gray-700" />
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Patólogo</p>
                <p class="text-sm font-bold text-gray-900">{{ caseItem.patologo || 'Sin asignar' }}</p>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
            <div class="flex items-center space-x-2">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                  <CalendarIcon class="w-4 h-4 text-gray-700" />
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Fecha de creación</p>
                <p class="text-sm font-bold text-gray-900">{{ formatDate(caseItem.fecha_creacion) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Muestras/Pruebas solicitadas -->
      <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center gap-3">
          <div class="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center">
            <SampleIcon class="w-4 h-4 text-blue-600" />
          </div>
          <h4 class="text-lg font-semibold text-gray-900">Pruebas Solicitadas</h4>
          <span v-if="caseItem.pruebas?.length" class="ml-auto inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700">
            {{ caseItem.pruebas.length }} {{ caseItem.pruebas.length === 1 ? 'prueba' : 'pruebas' }}
          </span>
        </div>
        <div class="p-6">
          <div v-if="caseItem.pruebas && caseItem.pruebas.length" class="flex flex-wrap gap-2">
            <span
              v-for="(prueba, pIdx) in caseItem.pruebas"
              :key="pIdx"
              class="inline-flex items-center justify-center bg-white text-gray-700 font-mono text-xs px-3 py-2 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
              :title="getTestName(prueba) !== extractTestCode(prueba) ? getTestName(prueba) : ''"
            >
              {{ extractTestCode(prueba) }} - {{ getTestName(prueba) }}
            </span>
          </div>
          <div v-else class="text-center py-8">
            <div class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-3">
              <SampleIcon class="w-6 h-6 text-gray-400" />
            </div>
            <p class="text-sm text-gray-500">Sin pruebas registradas</p>
          </div>
        </div>
      </div>

      <!-- Información de urgencia -->
      <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
        <div class="px-6 py-4 border-b border-gray-200 flex items-center gap-3">
          <div class="w-8 h-8 bg-red-50 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M4.93 4.93l14.14 14.14M12 2a10 10 0 100 20 10 10 0 000-20z"/></svg>
          </div>
          <h5 class="text-lg font-semibold text-gray-900">Información de Urgencia</h5>
        </div>
        <div class="p-6 grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
            <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Prioridad</p>
            <p class="mt-1 inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border" :class="priorityBadgeClasses">{{ getPriorityLabel(caseItem) }}</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
            <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Tiempo transcurrido</p>
            <p class="mt-1 inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold" :class="daysBadgeClasses">{{ getTimeRemaining(caseItem) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer: acciones -->
    <template #footer>
      <div v-if="caseItem" class="flex justify-end gap-2">
        <PrintPdfButton
          text="Imprimir PDF"
          :caseCode="caseItem.codigo"
          :caseData="caseItem"
        />
        <CloseButton @click="emit('close')" variant="danger-outline" size="md" text="Cerrar" />
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CasoUrgente } from '../types/dashboard.types'
import { CloseButton, PrintPdfButton } from '@/shared/components/ui/buttons'
import { Modal } from '@/shared/components/layout'
import CaseIcon from '@/assets/icons/CaseIcon.vue'
import ProfileIcon from '@/assets/icons/ProfileIcon.vue'
import EntityIcon from '@/assets/icons/EntityIcon.vue'
import DoctorIcon from '@/assets/icons/DoctorIcon.vue'
import CalendarIcon from '@/assets/icons/CalendarIcon.vue'
import SampleIcon from '@/assets/icons/SampleIcon.vue'

// Selected urgent case to display
const props = defineProps<{ caseItem: CasoUrgente | null }>()
// Emit close to parent
const emit = defineEmits<{ (e: 'close'): void }>()

// Open modal when a case is provided
const isOpen = computed(() => !!props.caseItem)

// Format ISO date to dd/mm/yyyy (es-ES)
const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

// Urgency criteria: >=5 business days and not completed
const isUrgent = (caso: CasoUrgente) => caso.dias_en_sistema >= 5 && caso.estado !== 'Completado'

const urgencyClass = (caso: CasoUrgente) => isUrgent(caso) ? 'text-red-700 font-semibold' : 'text-green-700'

const getPriorityLabel = (caso: CasoUrgente) => isUrgent(caso) ? 'URGENTE' : 'NORMAL'

const getTimeRemaining = (caso: CasoUrgente) => isUrgent(caso) ? `${caso.dias_en_sistema} días en sistema` : 'Dentro del tiempo límite'

// Extract test code from "123456 - Test name" or leading 6 digits
const extractTestCode = (testString: string) => testString.match(/^\d{6}/)?.[0] || testString.split(' - ')[0]

// Derive test name from "code - name" pattern
const getTestName = (testString: string) => {
  const parts = testString.split(' - ')
  return parts.length > 1 ? parts.slice(1).join(' - ') : testString
}

// Estilos de badges coherentes con CaseDetailsModal
const getCaseStatusClass = (status: string) => {
  const statusClasses: Record<string, string> = {
    'En proceso': 'bg-blue-100 text-blue-800',
    'Por firmar': 'bg-yellow-100 text-yellow-800',
    'Por entregar': 'bg-red-100 text-red-800',
    'Completado': 'bg-green-100 text-green-800',
    'Entregado': 'bg-gray-100 text-gray-800',
    'Cancelado': 'bg-red-100 text-red-800'
  }
  return statusClasses[status] || 'bg-gray-100 text-gray-800'
}

const priorityBadgeClasses = computed(() => {
  const key = (props.caseItem?.prioridad || '').toString().trim().toLowerCase()
  if (['prioritario','urgente'].includes(key)) return 'bg-red-50 text-red-700 border-red-100'
  return 'bg-green-50 text-green-700 border-green-100'
})

const daysBadgeClasses = computed(() => {
  const c = props.caseItem
  if (!c) return 'bg-gray-50 text-gray-700'
  return (c.dias_en_sistema >= 5 && c.estado !== 'Completado')
    ? 'bg-red-50 text-red-700'
    : 'bg-blue-50 text-blue-700'
})
</script>

<style scoped>
/* Mantener estilos mínimos; el componente Modal maneja el overlay */
</style>
