<template>
  <!-- Modal with urgent case details and actions -->
  <Modal v-model="isOpen" title="Detalles del Caso" size="lg" @close="emit('close')" class="debug-modal">
    <div v-if="caseItem" class="space-y-4">
      <!-- Primary details grid -->
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
          <p class="text-sm text-gray-500">Documento</p>
          <p class="text-base font-medium text-gray-900">{{ caseItem.paciente.cedula || 'N/A' }}</p>
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
          <p class="text-base font-medium text-gray-900" :class="urgencyClass(caseItem)">
            {{ caseItem.dias_en_sistema }} días
          </p>
        </div>
      </div>

      <!-- Requested tests list -->
      <div class="bg-gray-50 rounded-xl p-4 space-y-3">
        <h5 class="text-sm font-medium text-gray-700">Pruebas Solicitadas</h5>
        <div v-if="caseItem.pruebas?.length" class="space-y-3">
          <div v-for="(prueba, pIdx) in caseItem.pruebas" :key="pIdx" class="border border-gray-200 rounded-lg p-3 bg-white">
            <span class="text-sm font-medium text-gray-900">{{ extractTestCode(prueba) }} - {{ getTestName(prueba) }}</span>
          </div>
        </div>
        <div v-else class="text-sm text-gray-500">Sin pruebas registradas</div>
      </div>

      <!-- Urgency info: priority and time remaining -->
      <div class="bg-gray-50 rounded-xl p-4 space-y-2">
        <h5 class="text-sm font-medium text-gray-700">Información de Urgencia</h5>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <p class="text-sm text-gray-500">Prioridad</p>
            <p class="text-sm font-medium text-gray-900" :class="urgencyClass(caseItem)">
              {{ getPriorityLabel(caseItem) }}
            </p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Tiempo Restante</p>
            <p class="text-sm font-medium text-gray-900" :class="urgencyClass(caseItem)">
              {{ getTimeRemaining(caseItem) }}
            </p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Footer actions: print and close -->
    <template #footer>
      <div v-if="caseItem" class="flex justify-end gap-2">
        <PrintPdfButton 
          text="Imprimir PDF" 
          :caseCode="caseItem.codigo"
          :caseData="caseItem"
          @pdf-generated="(pdfBlob) => console.log('PDF generado:', pdfBlob.size, 'bytes')"
          @error="(error) => console.error('Error PDF:', error)"
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
</script>

<style scoped>
.debug-modal {
  z-index: 10000 !important;
}

.debug-modal :deep(.fixed) {
  background-color: rgba(0, 0, 0, 0.8) !important;
}
</style>
