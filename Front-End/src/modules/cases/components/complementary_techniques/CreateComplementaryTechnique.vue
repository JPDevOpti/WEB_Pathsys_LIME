<template>
  <!-- Create complementary technique form -->
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
          <FormInputField
            v-model="form.nombre"
            label="Nombre de la técnica"
            placeholder="Ej: Inmunohistoquímica CD20"
            :required="true"
            :max-length="100"
            :error="errors.nombre"
          />
          
          <FormSelect
            v-model="form.tipo"
            label="Tipo de técnica"
            :required="true"
            :options="tipoOptions"
            :error="errors.tipo"
          />
        </div>

        <div class="mt-4">
          <FormTextarea
            v-model="form.descripcion"
            label="Descripción"
            placeholder="Descripción detallada de la técnica complementaria"
            :required="true"
            :max-length="500"
            :rows="3"
            :error="errors.descripcion"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <FormSelect
            v-model="form.categoria"
            label="Categoría"
            :required="true"
            :options="categoriaOptions"
            :error="errors.categoria"
          />
          
          <FormSelect
            v-model="form.estado"
            label="Estado inicial"
            :required="true"
            :options="estadoOptions"
            :error="errors.estado"
          />
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
          <FormInputField
            v-model="form.casoAsociado"
            label="Código de caso asociado"
            placeholder="Ej: 2025-00001"
            :required="true"
            :max-length="10"
            :error="errors.casoAsociado"
            @update:model-value="validateCaseCode"
          />
          
          <FormInputField
            v-model="form.fechaEntrega"
            label="Fecha de entrega esperada"
            type="date"
            :required="true"
            :error="errors.fechaEntrega"
          />
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
          <FormInputField
            v-model="form.observaciones"
            label="Observaciones"
            placeholder="Observaciones adicionales (opcional)"
            :max-length="300"
            :error="errors.observaciones"
          />
          
          <FormSelect
            v-model="form.prioridad"
            label="Prioridad"
            :options="prioridadOptions"
            :error="errors.prioridad"
          />
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-end pt-4 border-t border-gray-200">
        <ClearButton 
          text="Limpiar formulario" 
          @click="onReset" 
          :disabled="isSubmitting"
        />
        <SaveButton 
          text="Crear Técnica" 
          :loading="isSubmitting"
          :disabled="!isFormValid"
          @click="onSubmit"
        />
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
import { ref, computed, reactive } from 'vue'
import { TestIcon } from '@/assets/icons'
import { FormInputField, FormTextarea, FormSelect } from '@/shared/components/forms'
import { SaveButton, ClearButton } from '@/shared/components/buttons'

// Form data
const form = reactive({
  nombre: '',
  descripcion: '',
  tipo: '',
  categoria: '',
  estado: 'En proceso',
  casoAsociado: '',
  fechaEntrega: '',
  observaciones: '',
  prioridad: 'Normal'
})

// Form state
const isSubmitting = ref(false)
const showSuccessModal = ref(false)
const successMessage = ref('')

// Validation errors
const errors = reactive({
  nombre: '',
  descripcion: '',
  tipo: '',
  categoria: '',
  estado: '',
  casoAsociado: '',
  fechaEntrega: '',
  observaciones: '',
  prioridad: ''
})

// Options for select fields
const tipoOptions = [
  { value: 'inmunohistoquimica', label: 'Inmunohistoquímica' },
  { value: 'molecular', label: 'Técnica Molecular' },
  { value: 'citogenetica', label: 'Citogenética' },
  { value: 'bioquimica', label: 'Bioquímica' },
  { value: 'microbiologia', label: 'Microbiología' },
  { value: 'otra', label: 'Otra' }
]

const categoriaOptions = [
  { value: 'Oncología', label: 'Oncología' },
  { value: 'Linfoma', label: 'Linfoma' },
  { value: 'Hematología', label: 'Hematología' },
  { value: 'Inflamación', label: 'Inflamación' },
  { value: 'Infecciosa', label: 'Infecciosa' },
  { value: 'Metabólica', label: 'Metabólica' },
  { value: 'Otra', label: 'Otra' }
]

const estadoOptions = [
  { value: 'En proceso', label: 'En proceso' },
  { value: 'Por entregar', label: 'Por entregar' },
  { value: 'Completado', label: 'Completado' }
]

const prioridadOptions = [
  { value: 'Baja', label: 'Baja' },
  { value: 'Normal', label: 'Normal' },
  { value: 'Alta', label: 'Alta' },
  { value: 'Urgente', label: 'Urgente' }
]

// Computed properties
const isFormValid = computed(() => {
  return form.nombre.trim() &&
         form.descripcion.trim() &&
         form.tipo &&
         form.categoria &&
         form.casoAsociado.trim() &&
         form.fechaEntrega &&
         !Object.values(errors).some(error => error !== '')
})

// Methods
const validateCaseCode = (value: string) => {
  const caseCodePattern = /^\d{4}-\d{5}$/
  if (value && !caseCodePattern.test(value)) {
    errors.casoAsociado = 'El código debe tener el formato YYYY-NNNNN (Ej: 2025-00001)'
  } else {
    errors.casoAsociado = ''
  }
}

const validateForm = () => {
  // Clear previous errors
  Object.keys(errors).forEach(key => {
    errors[key as keyof typeof errors] = ''
  })

  // Validate required fields
  if (!form.nombre.trim()) {
    errors.nombre = 'El nombre es requerido'
  }
  if (!form.descripcion.trim()) {
    errors.descripcion = 'La descripción es requerida'
  }
  if (!form.tipo) {
    errors.tipo = 'El tipo es requerido'
  }
  if (!form.categoria) {
    errors.categoria = 'La categoría es requerida'
  }
  if (!form.casoAsociado.trim()) {
    errors.casoAsociado = 'El código de caso es requerido'
  }
  if (!form.fechaEntrega) {
    errors.fechaEntrega = 'La fecha de entrega es requerida'
  }

  // Validate case code format
  validateCaseCode(form.casoAsociado)

  // Validate date
  if (form.fechaEntrega) {
    const deliveryDate = new Date(form.fechaEntrega)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    if (deliveryDate < today) {
      errors.fechaEntrega = 'La fecha de entrega no puede ser anterior a hoy'
    }
  }

  return Object.values(errors).every(error => error === '')
}

const onSubmit = async () => {
  if (!validateForm()) {
    return
  }

  isSubmitting.value = true
  
  try {
    // TODO: Replace with actual API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Simulate successful creation
    const newTechniqueCode = `C2025-${String(Date.now()).slice(-5)}`
    
    successMessage.value = `La técnica complementaria "${form.nombre}" ha sido creada exitosamente con el código ${newTechniqueCode}.`
    showSuccessModal.value = true
    
  } catch (error) {
    console.error('Error creating technique:', error)
    // TODO: Show error message
  } finally {
    isSubmitting.value = false
  }
}

const onReset = () => {
  Object.keys(form).forEach(key => {
    if (key === 'estado') {
      form[key as keyof typeof form] = 'En proceso'
    } else if (key === 'prioridad') {
      form[key as keyof typeof form] = 'Normal'
    } else {
      form[key as keyof typeof form] = ''
    }
  })
  
  Object.keys(errors).forEach(key => {
    errors[key as keyof typeof errors] = ''
  })
}

const closeSuccessModal = () => {
  showSuccessModal.value = false
}

const handleSuccessConfirm = () => {
  closeSuccessModal()
  onReset()
}
</script>

<style scoped>
/* Estilos específicos si es necesario */
</style>
