<template>
  <Modal
    v-model="isOpen"
    title="Detalles del Caso Anterior"
    size="lg"
    @close="$emit('close')"
  >
    <div class="space-y-6">
      <!-- Información básica del caso -->
      <div class="grid grid-cols-2 gap-4 bg-gray-50 rounded-xl p-4">
        <div>
          <p class="text-sm text-gray-500">Código del Caso</p>
          <p class="text-base font-medium text-gray-900">{{ caseCode }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Estado</p>
          <p class="text-base font-medium text-gray-900">{{ status }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Nombre del Paciente</p>
          <p class="text-base font-medium text-gray-900">{{ patientName }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Documento de Identidad</p>
          <p class="text-base font-medium text-gray-900">{{ patientId }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Edad</p>
          <p class="text-base font-medium text-gray-900">{{ patientAge }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Sexo</p>
          <p class="text-base font-medium text-gray-900">{{ patientSex }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Tipo de Atención</p>
          <p class="text-base font-medium text-gray-900 capitalize">{{ attentionType }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Entidad</p>
          <p class="text-base font-medium text-gray-900">{{ entity }}</p>
        </div>
      </div>

          <!-- Observaciones Generales -->
          <div v-if="caseItem?.observations" class="bg-gray-50 rounded-xl p-4">
            <h5 class="text-sm font-medium text-gray-700 mb-3">Observaciones Generales</h5>
            <div class="border border-gray-200 rounded-lg p-3 bg-white">
              <p class="text-sm text-gray-800 break-words">{{ caseItem.observations }}</p>
            </div>
          </div>

      <!-- Información temporal y patólogo -->
      <div class="grid grid-cols-4 gap-4 bg-gray-50 rounded-xl p-4">
        <div>
          <p class="text-sm text-gray-500">Fecha de Creación</p>
          <p class="text-base font-medium text-gray-900">{{ formatDate(createdAt) }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Fecha de Firma</p>
          <p class="text-base font-medium text-gray-900">{{ signedAt }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Prioridad</p>
          <p class="text-base font-medium text-gray-900">{{ priority }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500">Patólogo Asignado</p>
          <p class="text-base font-medium text-gray-900">{{ pathologist }}</p>
        </div>
      </div>

      <!-- Muestras y pruebas -->
      <div class="bg-gray-50 rounded-xl p-4 space-y-3">
        <h5 class="text-sm font-medium text-gray-700">Muestras y Pruebas</h5>
        <div v-if="muestras && muestras.length" class="space-y-3">
          <div v-for="(muestra, mIdx) in muestras" :key="mIdx" class="border border-gray-200 rounded-lg p-3 bg-white">
            <div class="flex items-center justify-between mb-2">
              <p class="text-sm text-gray-600">Región del cuerpo</p>
              <p class="text-sm font-medium text-gray-900">{{ muestra.body_region || 'No especificada' }}</p>
            </div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="(prueba, pIdx) in muestra.tests"
                :key="pIdx"
                class="relative inline-flex items-center justify-center bg-gray-100 text-gray-700 font-mono text-xs pl-2 pr-6 py-0.5 rounded border text-nowrap"
                :title="prueba.name && prueba.name !== prueba.id ? prueba.name : ''"
              >
                {{ prueba.id }} - {{ prueba.name || prueba.id }}
              </span>
            </div>
          </div>
        </div>
        <div v-else class="text-sm text-gray-500">Sin muestras registradas</div>
      </div>

      <!-- Resultado del caso -->
      <div v-if="resultado && hasResultContent" class="bg-gray-50 rounded-xl p-4 space-y-3">
        <h5 class="text-sm font-medium text-gray-700">Resultado del Informe</h5>
        

        <!-- Resultado Macroscópico -->
        <div v-if="resultado.macro_result" class="border border-gray-200 rounded-lg p-3 bg-white">
          <div class="mb-2">
            <p class="text-sm text-gray-600">Resultado Macroscópico</p>
          </div>
          <p class="text-sm text-gray-800 break-words">{{ resultado.macro_result }}</p>
        </div>

        <!-- Resultado Microscópico -->
        <div v-if="resultado.micro_result" class="border border-gray-200 rounded-lg p-3 bg-white">
          <div class="mb-2">
            <p class="text-sm text-gray-600">Resultado Microscópico</p>
          </div>
          <p class="text-sm text-gray-800 break-words">{{ resultado.micro_result }}</p>
        </div>

        <!-- Diagnóstico -->
        <div v-if="resultado.diagnosis" class="border border-gray-200 rounded-lg p-3 bg-white">
          <div class="mb-2">
            <p class="text-sm text-gray-600">Diagnóstico</p>
          </div>
          <p class="text-sm text-gray-800 break-words">{{ resultado.diagnosis }}</p>
        </div>
      </div>

      <!-- Diagnósticos CIE-10 y CIE-O -->
      <!-- TODO: Implementar cuando estén disponibles en el nuevo backend -->
      <!--
      <div v-if="resultado && (resultado.diagnostico_cie10 || resultado.diagnostico_cieo)" class="bg-gray-50 rounded-xl p-4 space-y-3">
        <h5 class="text-sm font-medium text-gray-700">Diagnósticos Clasificados</h5>
        
        <!-- Diagnóstico CIE-10 -->
        <!--
        <div v-if="resultado.diagnostico_cie10" class="border border-gray-200 rounded-lg p-3 bg-white">
          <div class="flex items-center gap-2 mb-2">
            <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              CIE-10
            </span>
            <span class="text-sm font-mono text-gray-600">{{ resultado.diagnostico_cie10.codigo }}</span>
          </div>
          <p class="text-sm text-gray-800">{{ resultado.diagnostico_cie10.nombre }}</p>
        </div>

        <!-- Diagnóstico CIE-O -->
        <!--
        <div v-if="resultado.diagnostico_cieo" class="border border-gray-200 rounded-lg p-3 bg-white">
          <div class="flex items-center gap-2 mb-2">
            <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
              CIE-O
            </span>
            <span class="text-sm font-mono text-gray-600">{{ resultado.diagnostico_cieo.codigo }}</span>
          </div>
          <p class="text-sm text-gray-800">{{ resultado.diagnostico_cieo.nombre }}</p>
        </div>
      </div>
      -->

      <!-- Información de firma -->
      <!-- TODO: Implementar cuando estén disponibles en el nuevo backend -->
      <!--
      <div v-if="resultado && resultado.firmado" class="bg-gray-50 rounded-xl p-4">
        <h5 class="text-sm font-medium text-gray-700 mb-3">Información de Firma</h5>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-gray-500">Fecha de Firma</p>
            <p class="text-base font-medium text-gray-900">{{ resultado.fecha_firma ? formatDate(resultado.fecha_firma) : 'N/A' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Patólogo Firmante</p>
            <p class="text-base font-medium text-gray-900">{{ resultado.patologo_firma || 'N/A' }}</p>
          </div>
        </div>
      </div>
      -->
    </div>

    <template #footer>
      <div class="flex justify-end gap-2">
        <PrintPdfButton 
          text="Imprimir PDF" 
          :caseCode="caseCode"
          :caseData="caseItem"
          @pdf-generated="(pdfBlob) => console.log('PDF generado:', pdfBlob.size, 'bytes')"
          @error="(error) => console.error('Error PDF:', error)"
        />
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
import { computed } from 'vue'
import type { CaseModel } from '@/modules/cases/types/case'
import { Modal } from '@/shared/components/layout'
import { CloseButton, PrintPdfButton } from '@/shared/components/buttons'

const props = defineProps<{ caseItem: CaseModel | null }>()
defineEmits<{ (e: 'close'): void }>()

// Estado del modal
const isOpen = computed(() => {
  console.log('PreviousCaseDetailsModal - caseItem:', props.caseItem)
  return !!props.caseItem
})

// Extraer datos del caso de forma unificada
const caseCode = computed(() => {
  const code = props.caseItem?.case_code || 'N/A'
  console.log('PreviousCaseDetailsModal - caseCode:', code, 'from:', props.caseItem?.case_code)
  return code
})
const status = computed(() => {
  const stat = props.caseItem?.state || 'N/A'
  console.log('PreviousCaseDetailsModal - status:', stat)
  return stat
})
const patientName = computed(() => {
  const name = props.caseItem?.patient_info?.name || 'N/A'
  console.log('PreviousCaseDetailsModal - patientName:', name, 'patient_info:', props.caseItem?.patient_info)
  return name
})
const patientId = computed(() => {
  const id = props.caseItem?.patient_info?.patient_code || 'N/A'
  console.log('PreviousCaseDetailsModal - patientId:', id)
  return id
})
const patientAge = computed(() => {
  const age = props.caseItem?.patient_info?.age
  const result = age ? `${age} años` : 'No especificada'
  console.log('PreviousCaseDetailsModal - patientAge:', result, 'age:', age)
  return result
})
const patientSex = computed(() => {
  const sex = props.caseItem?.patient_info?.gender || 'No especificado'
  console.log('PreviousCaseDetailsModal - patientSex:', sex)
  return sex
})
const attentionType = computed(() => {
  const type = props.caseItem?.patient_info?.care_type || 'N/A'
  console.log('PreviousCaseDetailsModal - attentionType:', type)
  return type
})
const entity = computed(() => {
  const ent = props.caseItem?.patient_info?.entity_info?.name || 'No especificada'
  console.log('PreviousCaseDetailsModal - entity:', ent, 'entity_info:', props.caseItem?.patient_info?.entity_info)
  return ent
})
const createdAt = computed(() => props.caseItem?.created_at || '')
const signedAt = computed(() => {
  // TODO: Implementar cuando esté disponible en el nuevo backend
  return 'Pendiente'
})
const priority = computed(() => props.caseItem?.priority || 'Normal')
const pathologist = computed(() => props.caseItem?.assigned_pathologist?.name || 'Sin asignar')
const muestras = computed(() => props.caseItem?.samples)
const resultado = computed(() => props.caseItem?.result)

const hasResultContent = computed(() => {
  if (!resultado.value) return false
  return resultado.value.macro_result || 
         resultado.value.micro_result || 
         resultado.value.diagnosis
})

function formatDate(dateString: string, includeTime: boolean = false) {
  if (!dateString) return 'N/A'
  const d = new Date(dateString)
  
  if (includeTime) {
    return d.toLocaleString('es-ES', { 
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}
</script>
