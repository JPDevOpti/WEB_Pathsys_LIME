<template>
  <Modal
    v-model="isOpen"
    title="Detalles del Caso"
    size="lg"
    @close="$emit('close')"
  >
    <div class="space-y-6">
      <!-- Encabezado con icono, código, paciente y badges -->
      <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
        <div class="px-6 py-5 border-b border-gray-200 flex items-start gap-4">
          <div class="flex-shrink-0">
            <div class="w-12 h-12 bg-green-50 rounded-xl flex items-center justify-center">
              <CaseIcon class="w-6 h-6 text-green-600" />
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
              <div class="min-w-0">
                <h3 class="text-lg font-bold text-gray-900 truncate">Caso</h3>
                <div class="flex items-center flex-wrap gap-2 mt-1">
                  <span class="text-base font-semibold text-gray-900 font-mono break-all">{{ caseCode || 'Sin código' }}</span>
                  <span v-if="patientName" class="text-sm text-gray-600">• Paciente: <span class="font-medium text-gray-900">{{ patientName }}</span></span>
                </div>
              </div>
              <div class="flex flex-wrap gap-2">
                <span v-if="caseState" class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-100">Estado: {{ caseState }}</span>
                <span v-if="casePriority" :class="['inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border', priorityBadgeClasses]">Prioridad: {{ casePriority }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Tarjetas de información del paciente -->
        <div class="p-6 grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                <ProfileIcon class="w-5 h-5 text-gray-700" />
              </div>
              <div class="min-w-0">
                <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Documento</p>
                <p class="text-lg font-bold text-gray-900 font-mono break-all">{{ patientDocument || '—' }}</p>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                <CalendarIcon class="w-5 h-5 text-gray-700" />
              </div>
              <div class="min-w-0">
                <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Edad</p>
                <p class="text-lg font-bold text-gray-900">{{ patientAge ? `${patientAge} años` : '—' }}</p>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                <GerdenIcon class="w-5 h-5 text-gray-700" />
              </div>
              <div class="min-w-0">
                <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Sexo</p>
                <p class="text-lg font-bold text-gray-900 capitalize">{{ patientGender || '—' }}</p>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                <AtentionTypeIcon class="w-5 h-5 text-gray-700" />
              </div>
              <div class="min-w-0">
                <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Tipo de atención</p>
                <p class="text-lg font-bold text-gray-900 capitalize">{{ patientCareType || '—' }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Entidad y Patólogo -->
        <div class="px-6 pb-6 grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div class="bg-gray-50 rounded-lg p-5 border border-gray-200">
            <div class="flex items-start gap-3">
              <div class="w-12 h-12 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                <EntityIcon class="w-6 h-6 text-gray-700" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-1">Entidad</p>
                <p class="text-lg font-semibold text-gray-900 break-words">{{ entityName || 'No especificada' }}</p>
                <p v-if="entityCode" class="text-sm text-gray-600 font-mono mt-1 break-all">Código: {{ entityCode }}</p>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 rounded-lg p-5 border border-gray-200">
            <div class="flex items-start gap-3">
              <div class="w-12 h-12 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                <DoctorIcon class="w-6 h-6 text-gray-700" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-1">Patólogo Asignado</p>
                <p class="text-lg font-semibold text-gray-900 break-words">{{ caseItem?.pathologist || 'Sin asignar' }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Fechas -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="bg-white rounded-lg p-4 border border-gray-200">
          <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Fecha de creación</p>
          <p class="text-base font-semibold text-gray-900 mt-1">{{ caseItem?.receivedAt ? formatDate(caseItem.receivedAt) : 'N/A' }}</p>
        </div>
        <div class="bg-white rounded-lg p-4 border border-gray-200">
          <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Fecha de firma</p>
          <p class="text-base font-semibold text-gray-900 mt-1">{{ (caseItem?.signedAt || caseItem?.deliveredAt) ? formatDate((caseItem?.signedAt || caseItem?.deliveredAt) as string) : 'Pendiente' }}</p>
        </div>
      </div>

      <!-- Submuestras y pruebas -->
      <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-200 flex items-center gap-2">
          <SampleIcon class="w-5 h-5 text-blue-600" />
          <h4 class="text-sm font-semibold text-gray-800">Muestras y Pruebas</h4>
          <span v-if="caseItem?.subsamples?.length" class="ml-auto inline-flex items-center px-3 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
            {{ caseItem?.subsamples?.length }} submuestra{{ caseItem?.subsamples?.length !== 1 ? 's' : '' }}
          </span>
        </div>
        <div class="p-5">
          <div v-if="caseItem?.subsamples && caseItem.subsamples.length" class="space-y-3">
            <div v-for="(muestra, mIdx) in caseItem.subsamples" :key="mIdx" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
              <div class="flex items-center justify-between mb-2">
                <p class="text-sm text-gray-600">Región del cuerpo</p>
                <p class="text-sm font-medium text-gray-900">{{ muestra.bodyRegion || 'No especificada' }}</p>
              </div>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="(prueba, pIdx) in muestra.tests"
                  :key="pIdx"
                  class="relative inline-flex items-center justify-center bg-white text-gray-700 font-mono text-xs pl-2 pr-6 py-1 rounded border text-nowrap shadow-sm"
                  :title="prueba.name && prueba.name !== prueba.id ? prueba.name : ''"
                >
                  {{ prueba.id }} - {{ prueba.name || prueba.id }}
                  <span
                    v-if="prueba.quantity > 1"
                    class="absolute -top-1 -right-1 inline-flex items-center justify-center w-4 h-4 rounded-full bg-blue-100 text-blue-600 text-[10px] font-bold"
                  >
                    {{ prueba.quantity }}
                  </span>
                </span>
              </div>
            </div>
          </div>
          <div v-else class="text-sm text-gray-500">Sin muestras registradas</div>
        </div>
      </div>

      <!-- Resultado del informe -->
      <div v-if="caseItem?.result && caseItem?.status !== 'En proceso'" class="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-200">
          <h5 class="text-sm font-semibold text-gray-800">Resultado del Informe</h5>
        </div>
        <div class="p-5 space-y-3">
          <div v-if="caseItem.result.method && caseItem.result.method.length > 0" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
            <div class="mb-2">
              <p class="text-sm text-gray-600">Método</p>
            </div>
            <div class="flex flex-wrap gap-1">
              <span
                v-for="(metodo, index) in caseItem.result.method"
                :key="index"
                class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-800"
              >
                {{ metodo }}
              </span>
            </div>
          </div>

          <div v-if="caseItem.result.macro_result" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
            <div class="mb-2">
              <p class="text-sm text-gray-600">Resultado Macroscópico</p>
            </div>
            <p class="text-sm text-gray-800 break-words">{{ caseItem.result.macro_result }}</p>
          </div>

          <div v-if="caseItem.result.micro_result" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
            <div class="mb-2">
              <p class="text-sm text-gray-600">Resultado Microscópico</p>
            </div>
            <p class="text-sm text-gray-800 break-words">{{ caseItem.result.micro_result }}</p>
          </div>

          <div v-if="caseItem.result.diagnosis" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
            <div class="mb-2">
              <p class="text-sm text-gray-600">Diagnóstico</p>
            </div>
            <p class="text-sm text-gray-800 break-words">{{ caseItem.result.diagnosis }}</p>
          </div>

          <div v-if="caseItem.result.observations" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
            <div class="mb-2">
              <p class="text-sm text-gray-600">Observaciones</p>
            </div>
            <p class="text-sm text-gray-800 break-words">{{ caseItem.result.observations }}</p>
          </div>
        </div>
      </div>

      <!-- Diagnósticos clasificados -->
      <div v-if="caseItem?.result && caseItem?.status !== 'En proceso' && (caseItem.result.cie10_diagnosis || caseItem.result.cieo_diagnosis)" class="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-200">
          <h5 class="text-sm font-semibold text-gray-800">Diagnósticos Clasificados</h5>
        </div>
        <div class="p-5 space-y-3">
          <div v-if="caseItem.result.cie10_diagnosis" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
            <div class="flex items-center gap-2 mb-2">
              <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">CIE-10</span>
              <span class="text-sm font-mono text-gray-600">{{ caseItem.result.cie10_diagnosis.code }}</span>
            </div>
            <p class="text-sm text-gray-800">{{ caseItem.result.cie10_diagnosis.name }}</p>
          </div>

          <div v-if="caseItem.result.cieo_diagnosis" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
            <div class="flex items-center gap-2 mb-2">
              <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">CIE-O</span>
              <span class="text-sm font-mono text-gray-600">{{ caseItem.result.cieo_diagnosis.code }}</span>
            </div>
            <p class="text-sm text-gray-800">{{ caseItem.result.cieo_diagnosis.name }}</p>
          </div>
        </div>
      </div>

      <!-- Pruebas complementarias -->
      <div v-if="caseItem?.complementary_tests && caseItem.complementary_tests.length > 0" class="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-200">
          <h5 class="text-sm font-semibold text-gray-800">Pruebas Complementarias</h5>
        </div>
        <div class="p-5 space-y-3">
          <div v-for="(test, index) in caseItem.complementary_tests" :key="index">
            <div v-if="test.code && test.name && test.quantity" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">{{ test.code }}</span>
                  <span class="text-sm font-medium text-gray-900">{{ test.name }}</span>
                </div>
                <span v-if="test.quantity > 1" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">Cantidad: {{ test.quantity }}</span>
              </div>
            </div>
            <div v-else-if="test.reason" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
              <div class="mb-2">
                <p class="text-sm text-gray-600">Motivo de la solicitud</p>
              </div>
              <p class="text-sm text-gray-800 break-words leading-relaxed">{{ test.reason }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Notas adicionales -->
      <div v-if="props.caseItem?.status === 'Completado' && props.caseItem?.additional_notes && props.caseItem.additional_notes.length > 0" class="bg-white rounded-2xl border border-gray-200 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-200 flex items-center gap-2">
          <DocsIcon class="w-4 h-4 text-gray-600" />
          <h5 class="text-sm font-semibold text-gray-800">Notas Adicionales</h5>
          <span v-if="props.caseItem?.additional_notes && props.caseItem.additional_notes.length > 0" class="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {{ props.caseItem.additional_notes.length }} {{ props.caseItem.additional_notes.length === 1 ? 'nota' : 'notas' }}
          </span>
        </div>
        <div class="p-5">
          <div v-if="props.caseItem?.additional_notes && props.caseItem.additional_notes.length > 0" class="space-y-3">
            <div v-for="(nota, index) in props.caseItem.additional_notes" :key="index" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="text-xs text-gray-600 font-medium">{{ formatDate(nota.date, true) }}</span>
                </div>
                <span class="text-xs text-gray-400">#{{ index + 1 }}</span>
              </div>
              <p class="text-sm text-gray-800 break-words leading-relaxed">{{ nota.note }}</p>
            </div>
          </div>
          <div v-else class="text-center py-4">
            <DocsIcon class="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p class="text-sm text-gray-500">No hay notas adicionales para este caso</p>
            <p class="text-xs text-gray-400 mt-1">Puedes agregar notas usando el botón "Notas adicionales"</p>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end gap-2">
        <PrintPdfButton
          text="Imprimir PDF"
          :caseCode="props.caseItem?.caseCode || props.caseItem?.id"
          :caseData="props.caseItem"
          @pdf-generated="handlePdfGenerated"
          @error="handlePdfError"
        />
        <button
          v-if="props.caseItem?.status === 'Por entregar' || props.caseItem?.status === 'Completado'"
          @click="showNotesDialog = true"
          class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <DocsIcon class="w-4 h-4 mr-2" />
          Notas Adicionales
        </button>
        <CloseButton
          @click="$emit('close')"
          variant="danger-outline"
          size="md"
          text="Cerrar"
        />
      </div>
    </template>
  </Modal>

  <NotesDialog
    v-model="showNotesDialog"
    title="Notas adicionales"
    subtitle="Agregar información complementaria al caso"
    textarea-label="Nueva nota"
    textarea-placeholder="Escriba aquí la nueva nota adicional para este caso..."
    help-text="Esta información será agregada al caso como nota adicional con fecha y hora actual"
    confirm-text="Agregar nota"
    cancel-text="Cancelar"
    @confirm="handleNotesConfirm"
    @cancel="handleNotesCancel"
  />
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Case } from '../types/case.types'
import { DocsIcon } from '@/assets/icons'
import { NotesDialog } from '@/shared/components/feedback'
import { CloseButton, PrintPdfButton } from '@/shared/components/buttons'
import { Modal } from '@/shared/components/layout'
import { casesApiService } from '@/modules/cases/services/casesApi.service'
import { useNotifications } from '@/modules/cases/composables/useNotifications'
import CaseIcon from '@/assets/icons/CaseIcon.vue'
import EntityIcon from '@/assets/icons/EntityIcon.vue'
import SampleIcon from '@/assets/icons/SampleIcon.vue'
import CalendarIcon from '@/assets/icons/CalendarIcon.vue'
import ProfileIcon from '@/assets/icons/ProfileIcon.vue'
import GerdenIcon from '@/assets/icons/GerdenIcon.vue'
import AtentionTypeIcon from '@/assets/icons/AtentionTypeIcon.vue'
import DoctorIcon from '@/assets/icons/DoctorIcon.vue'

const props = defineProps<{ caseItem: Case | null }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'edit', c: Case): void; (e: 'preview', c: Case): void; (e: 'notes', c: Case): void }>()

const showNotesDialog = ref(false)
const isOpen = computed(() => !!props.caseItem)
const { showSuccess, showError } = useNotifications()

// Normalizadores para mostrar datos con estilo similar a la notificación de caso creado
const activePatient = computed<any>(() => (props.caseItem as any)?.patient || (props.caseItem as any)?.patient_info || {})
const caseCode = computed(() => props.caseItem?.caseCode || (props.caseItem as any)?.case_code || props.caseItem?.id || '')
const caseState = computed(() => props.caseItem?.status || '')
const casePriority = computed(() => translateCasePriority((props.caseItem as any)?.priority))

const patientName = computed(() => activePatient.value.fullName || activePatient.value.name || 'No registrado')
const patientDocument = computed(() => activePatient.value.id || activePatient.value.patient_code || '')
const patientAge = computed(() => activePatient.value.age || '')
const patientGender = computed(() => normalizeGender(activePatient.value.sex || activePatient.value.gender))
const patientCareType = computed(() => normalizeCareType(activePatient.value.attentionType || activePatient.value.care_type))

const entityName = computed(() => activePatient.value.entity || (props.caseItem as any)?.entity || '')
const entityCode = computed(() => activePatient.value.entityCode || activePatient.value.entity_code || '')

const priorityBadgeClasses = computed(() => {
  const base = 'border-1'
  const key = (casePriority.value || '').toString().trim().toLowerCase()
  if (key === 'normal') return `${base} bg-green-50 text-green-700 border-green-100`
  if (['prioritario','priority','urgente','urgent'].includes(key)) return `${base} bg-red-50 text-red-700 border-red-100`
  return `${base} bg-gray-50 text-gray-700 border-gray-200`
})

const formatDate = (dateString: string, includeTime: boolean = false) => {
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

function normalizeGender(value?: string | null) {
  if (!value) return ''
  const text = value.toString().trim().toLowerCase()
  if (text.startsWith('masc') || text === 'm') return 'masculino'
  if (text.startsWith('fem') || text === 'f') return 'femenino'
  return value
}

function normalizeCareType(value?: string | null) {
  if (!value) return ''
  const text = value.toString().trim().toLowerCase()
  if (text.startsWith('ambu')) return 'ambulatorio'
  if (text.startsWith('hosp')) return 'hospitalizado'
  return value
}

function translateCasePriority(value?: string | null) {
  if (!value) return ''
  const map: Record<string, string> = { normal: 'Normal', priority: 'Prioritario', prioritario: 'Prioritario', urgente: 'Urgente' }
  const key = value.toString().trim().toLowerCase()
  return map[key] || value
}

const handleNotesConfirm = async (notes: string) => {
  try {
    const caseCode = props.caseItem?.caseCode || (props.caseItem as any)?.caso_code
    if (!caseCode) {
      showError('Error', 'No se pudo identificar el caso')
      return
    }

    const nuevaNota = {
      date: new Date().toISOString(),
      note: notes
    }
    
    const todasLasNotas = [
      ...(props.caseItem?.additional_notes || []),
      nuevaNota
    ]

    const updateData = {
      additional_notes: todasLasNotas
    }
    
    await casesApiService.updateCase(caseCode, updateData)
    showSuccess('Nota agregada', 'La nota adicional se ha guardado exitosamente')
    showNotesDialog.value = false
    
    const casoActualizado = {
      ...props.caseItem,
      additional_notes: todasLasNotas
    }
    
    emit('notes', casoActualizado as any)
  } catch (error: any) {
    showError('Error', error.message || 'No se pudo guardar la nota adicional')
  }
}

const handleNotesCancel = () => {
  showNotesDialog.value = false
}

const handlePdfGenerated = (pdfBlob: Blob) => {
  console.log('PDF generado exitosamente:', pdfBlob.size, 'bytes')
}

const handlePdfError = (error: string) => {
  console.error('Error al generar PDF:', error)
}

</script>