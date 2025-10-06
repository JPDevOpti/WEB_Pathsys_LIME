<template>
  <!-- Create complementary technique form (Excel-aligned) -->
  <div class="space-y-6">
    <form class="space-y-6" @submit.prevent="onSubmit">
      <!-- Basic Information -->
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <h4 class="text-sm font-semibold text-gray-700 mb-4 flex items-center">
          <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          Información Básica
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormInputField v-model="form.date" label="Fecha" type="date" :required="true" :error="errors.date" />
          <FormInputField v-model="form.elaboratedBy" label="Elaboró" :required="true" :max-length="50" :error="errors.elaboratedBy" />
          <FormInputField v-model="form.caseNumber" label="N° Caso" :required="true" :max-length="20" :error="errors.caseNumber" />
          <FormInputField v-model="form.patientDocument" label="Documento del paciente" :required="true" :max-length="20" :error="errors.patientDocument" />
          <FormInputField v-model="form.patientName" label="Nombre del paciente" :required="true" :max-length="100" :error="errors.patientName" />
          <FormInputField v-model="form.institution" label="Institución" :required="true" :max-length="50" :error="errors.institution" />
          <FormInputField v-model.number="form.receivedSlidesCount" label="Número de placas recibe" type="number" :required="true" :error="errors.receivedSlidesCount" />
          <FormInputField v-model="form.receivedBy" label="Recibe" :max-length="50" :error="errors.receivedBy" />
        </div>
      </div>

      <!-- Case Association -->
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <h4 class="text-sm font-semibold text-gray-700 mb-4 flex items-center">
          <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          Asociación con Caso
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormInputField v-model="form.deliveryDate" label="Fecha entrega" type="date" :required="true" :error="errors.deliveryDate" />
          <FormInputField v-model="form.deliveredBy" label="Entrega" :required="true" :max-length="50" :error="errors.deliveredBy" />
        </div>
      </div>

      <!-- Additional Information -->
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <h4 class="text-sm font-semibold text-gray-700 mb-4 flex items-center">
          <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4"/>
          </svg>
          Información Adicional
        </h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormTextarea v-model="form.lowComplexityIHQ" label="IHQ baja complejidad" placeholder="ALK-1, TOXOPLASMA, CMV, TDT, SINAPTOFISINA, ..." :rows="2" :error="errors.lowComplexityIHQ" />
          <FormInputField v-model.number="form.lowComplexitySlidesCount" label="# Placas (baja complejidad)" type="number" :error="errors.lowComplexitySlidesCount" />
          <FormTextarea v-model="form.highComplexityIHQ" label="IHQ alta complejidad" placeholder="SOX-11, C4D, SV40, HER2, RE, RP, CICLINA D1, ..." :rows="2" :error="errors.highComplexityIHQ" />
          <FormInputField v-model.number="form.highComplexitySlidesCount" label="# Placas (alta complejidad)" type="number" :error="errors.highComplexitySlidesCount" />
          <FormTextarea v-model="form.specialIHQ" label="IHQ especiales" placeholder="ATRX, IDH1, MUC1, PD1, PD-L1, ..." :rows="2" :error="errors.specialIHQ" />
          <FormInputField v-model.number="form.specialIHQSlidesCount" label="# Placas (especiales)" type="number" :error="errors.specialIHQSlidesCount" />
          <FormTextarea v-model="form.histochemical" label="Histoquímicas" placeholder="PAS, ROJO CONGO, ZN, ..." :rows="2" :error="errors.histochemical" />
          <FormInputField v-model.number="form.histochemicalSlidesCount" label="# Placas (histoquímicas)" type="number" :error="errors.histochemicalSlidesCount" />
          <FormSelect v-model="form.receiptStatus" label="Recibo" :options="receiptStatusOptions" :required="true" :error="errors.receiptStatus" />
          <FormTextarea v-model="form.notes" label="Observaciones" placeholder="Observaciones adicionales (opcional)" :rows="2" :error="errors.notes" />
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-end pt-4 border-t border-gray-200">
        <ClearButton text="Limpiar formulario" @click="onReset" :disabled="isSubmitting" />
        <SaveButton text="Crear Técnica" :loading="isSubmitting" :disabled="!isFormValid" @click="onSubmit" />
      </div>
    </form>

    <!-- Success Message -->
    <div v-if="showSuccessModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div class="flex items-center mb-4">
          <svg class="w-6 h-6 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
          <h3 class="text-lg font-semibold text-gray-900">Técnica Creada Exitosamente</h3>
        </div>
        <p class="text-gray-600 mb-6">{{ successMessage }}</p>
        <div class="flex justify-end gap-3">
          <button @click="closeSuccessModal" class="px-4 py-2 text-gray-600 hover:text-gray-800">Cerrar</button>
          <button @click="handleSuccessConfirm" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Aceptar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Imports
import { ref, computed, reactive } from 'vue'
import { FormInputField, FormTextarea, FormSelect } from '@/shared/components/ui/forms'
import { SaveButton, ClearButton } from '@/shared/components/ui/buttons'
import type { ComplementaryTechnique } from '../types/special-cases.types'

// Emits created event so parent can append to list
const emit = defineEmits<{ (e: 'created', payload: ComplementaryTechnique): void }>()

// Form data (English keys; values displayed to user in Spanish)
const form = reactive({
  date: '',
  elaboratedBy: '',
  caseNumber: '',
  patientDocument: '',
  patientName: '',
  institution: '',
  receivedSlidesCount: 0,
  receivedBy: '',
  deliveryDate: '',
  deliveredBy: '',
  lowComplexityIHQ: '',
  lowComplexitySlidesCount: 0,
  highComplexityIHQ: '',
  highComplexitySlidesCount: 0,
  specialIHQ: '',
  specialIHQSlidesCount: 0,
  histochemical: '',
  histochemicalSlidesCount: 0,
  receiptStatus: 'FACTURAR',
  notes: ''
})

// Form state
const isSubmitting = ref(false)
const showSuccessModal = ref(false)
const successMessage = ref('')

// Validation errors (English keys)
const errors = reactive<Record<string, string>>({
  date: '',
  elaboratedBy: '',
  caseNumber: '',
  patientDocument: '',
  patientName: '',
  institution: '',
  receivedSlidesCount: '',
  receivedBy: '',
  deliveryDate: '',
  deliveredBy: '',
  lowComplexityIHQ: '',
  lowComplexitySlidesCount: '',
  highComplexityIHQ: '',
  highComplexitySlidesCount: '',
  specialIHQ: '',
  specialIHQSlidesCount: '',
  histochemical: '',
  histochemicalSlidesCount: '',
  receiptStatus: '',
  notes: ''
})

// Options for select fields
const receiptStatusOptions = [
  { value: 'FACTURAR', label: 'FACTURAR' },
  { value: 'PENDIENTE', label: 'PENDIENTE' },
  { value: 'ANULADO', label: 'ANULADO' }
]

// Computed properties
const isFormValid = computed(() => {
  const required = [
    form.date,
    form.elaboratedBy,
    form.caseNumber,
    form.patientDocument,
    form.patientName,
    form.institution,
    String(form.receivedSlidesCount),
    form.deliveryDate,
    form.deliveredBy,
    form.receiptStatus
  ]
  return required.every(v => String(v).trim() !== '') && !Object.values(errors).some(error => error !== '')
})

// Validate form inputs
const validateForm = () => {
  // Clear previous errors
  Object.keys(errors).forEach(key => { errors[key] = '' })

  // Basic required checks (messages in Spanish for user)
  if (!form.date) errors.date = 'La fecha es requerida'
  if (!form.elaboratedBy.trim()) errors.elaboratedBy = 'Elaboró es requerido'
  if (!form.caseNumber.trim()) errors.caseNumber = 'El número de caso es requerido'
  if (!form.patientDocument.trim()) errors.patientDocument = 'El documento del paciente es requerido'
  if (!form.patientName.trim()) errors.patientName = 'El nombre del paciente es requerido'
  if (!form.institution.trim()) errors.institution = 'La institución es requerida'
  if (!form.receivedSlidesCount || form.receivedSlidesCount < 0) errors.receivedSlidesCount = 'Número de placas inválido'
  if (!form.deliveryDate) errors.deliveryDate = 'La fecha de entrega es requerida'
  if (!form.deliveredBy.trim()) errors.deliveredBy = 'Entrega es requerido'
  if (!form.receiptStatus) errors.receiptStatus = 'El recibo es requerido'

  // Validate date not in past for deliveryDate
  if (form.deliveryDate) {
    const delivery = new Date(form.deliveryDate)
    const today = new Date(); today.setHours(0,0,0,0)
    if (delivery < today) errors.deliveryDate = 'La fecha de entrega no puede ser anterior a hoy'
  }

  return Object.values(errors).every(error => error === '')
}

// Submit handler
const onSubmit = async () => {
  if (!validateForm()) return

  isSubmitting.value = true
  try {
    // Simulate async submit (front only per your request)
    await new Promise(resolve => setTimeout(resolve, 800))

    // Create technique object (values in Spanish per workspace rule)
    const newTechnique: ComplementaryTechnique = {
      id: `CT-${Date.now()}`,
      date: form.date,
      elaboratedBy: form.elaboratedBy,
      caseNumber: form.caseNumber,
      patientDocument: form.patientDocument,
      patientName: form.patientName,
      institution: form.institution,
      receivedSlidesCount: Number(form.receivedSlidesCount) || 0,
      receivedBy: form.receivedBy,
      deliveryDate: form.deliveryDate,
      deliveredBy: form.deliveredBy,
      lowComplexityIHQ: form.lowComplexityIHQ,
      lowComplexitySlidesCount: Number(form.lowComplexitySlidesCount) || 0,
      highComplexityIHQ: form.highComplexityIHQ,
      highComplexitySlidesCount: Number(form.highComplexitySlidesCount) || 0,
      specialIHQ: form.specialIHQ,
      specialIHQSlidesCount: Number(form.specialIHQSlidesCount) || 0,
      histochemical: form.histochemical,
      histochemicalSlidesCount: Number(form.histochemicalSlidesCount) || 0,
      receiptStatus: form.receiptStatus,
      notes: form.notes
    }

    // Emit created to parent
    emit('created', newTechnique)

    // Success message to user in Spanish
    successMessage.value = `El registro con N° Caso "${form.caseNumber}" ha sido creado exitosamente.`
    showSuccessModal.value = true
  } catch (error) {
    console.error('Error creating technique:', error)
  } finally {
    isSubmitting.value = false
  }
}

// Reset form
const onReset = () => {
  form.date = ''
  form.elaboratedBy = ''
  form.caseNumber = ''
  form.patientDocument = ''
  form.patientName = ''
  form.institution = ''
  form.receivedSlidesCount = 0
  form.receivedBy = ''
  form.deliveryDate = ''
  form.deliveredBy = ''
  form.lowComplexityIHQ = ''
  form.lowComplexitySlidesCount = 0
  form.highComplexityIHQ = ''
  form.highComplexitySlidesCount = 0
  form.specialIHQ = ''
  form.specialIHQSlidesCount = 0
  form.histochemical = ''
  form.histochemicalSlidesCount = 0
  form.receiptStatus = 'FACTURAR'
  form.notes = ''

  Object.keys(errors).forEach(key => { errors[key] = '' })
}

// Modal handlers
const closeSuccessModal = () => { showSuccessModal.value = false }
const handleSuccessConfirm = () => { closeSuccessModal(); onReset() }
</script>

<style scoped>
/* Module-specific styles if needed */
</style>


