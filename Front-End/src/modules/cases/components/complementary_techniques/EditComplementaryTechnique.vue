<template>
  <!-- Edit complementary technique form -->
  <div class="space-y-6">
    <form class="space-y-6" @submit.prevent="onSubmit">
      <!-- Search section -->
      <div v-if="!techniqueCodeProp" class="bg-gray-50 rounded-lg border border-gray-200">
        <div class="px-4 pt-4 pb-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
            <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            Buscar técnica complementaria para editar
          </h3>
      
          <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-end">
            <div class="flex-1">
              <FormInputField
                v-model="searchTechniqueCode"
                type="text"
                placeholder="Ejemplo: C2025-00001"
                maxlength="12"
                autocomplete="off"
                :disabled="isSearching"
                @update:model-value="handleTechniqueCodeChange"
                @keydown.enter.prevent="searchTechnique"
              />
              <div v-if="searchTechniqueCode && !isValidTechniqueCodeFormat(searchTechniqueCode)" class="mt-1 text-xs text-red-600">
                El código debe tener el formato CYYYY-NNNNN (Ejemplo: C2025-00001)
              </div>
            </div>
            <div class="flex gap-2 sm:gap-3">
              <SearchButton text="Buscar" loading-text="Buscando..." :loading="isSearching" @click="searchTechnique" size="md" variant="primary" />
              <ClearButton v-if="techniqueFound" text="Limpiar" @click="onReset" />
            </div>
          </div>

          <!-- Search error banner -->
          <div v-if="searchError" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              <p class="text-sm text-red-600">{{ searchError }}</p>
            </div>
          </div>

          <!-- Found technique banner -->
          <div v-if="techniqueFound && foundTechniqueInfo" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <svg class="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
                <div>
                  <p class="text-sm font-medium text-green-800">Técnica encontrada</p>
                  <p class="text-xs text-green-600">{{ foundTechniqueInfo.nombre }} - {{ foundTechniqueInfo.estado }}</p>
                </div>
              </div>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="getStatusClass(foundTechniqueInfo.estado)">
                {{ foundTechniqueInfo.estado }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Edit form (always shown) -->
      <div class="space-y-6">


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
              v-model="form.codigo"
              label="Código"
              placeholder="Ej: C2025-00001"
            />
            
            <FormInputField
              v-model="form.nombre"
              label="Nombre de la técnica"
              placeholder="Ej: Inmunohistoquímica CD20"
              :required="true"
              :max-length="100"
              :error="errors.nombre"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <FormSelect
              v-model="form.tipo"
              label="Tipo de técnica"
              :required="true"
              :options="tipoOptions"
              :error="errors.tipo"
            />
            
            <FormSelect
              v-model="form.categoria"
              label="Categoría"
              :required="true"
              :options="categoriaOptions"
              :error="errors.categoria"
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
        </div>

        <!-- Status and Dates -->
        <div class="bg-white rounded-lg border border-gray-200 p-4">
          <h4 class="text-sm font-semibold text-gray-700 mb-4 flex items-center">
            <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            Estado y Fechas
          </h4>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <FormSelect
              v-model="form.estado"
              label="Estado actual"
              :required="true"
              :options="estadoOptions"
              :error="errors.estado"
            />
            
            <FormInputField
              v-model="form.fechaCreacion"
              label="Fecha de creación"
              type="date"
            />
            
            <FormInputField
              v-model="form.fechaEntrega"
              label="Fecha de entrega"
              type="date"
              :required="true"
              :error="errors.fechaEntrega"
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
          
          <FormInputField
            v-model="form.casoAsociado"
            label="Código de caso asociado"
            placeholder="Ej: 2025-00001"
            :required="true"
            :max-length="10"
            :error="errors.casoAsociado"
            @update:model-value="validateCaseCode"
          />
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
            text="Cancelar" 
            @click="onReset" 
            :disabled="isSubmitting"
          />
          <SaveButton 
            text="Actualizar Técnica" 
            :loading="isSubmitting"
            :disabled="!isFormValid"
            @click="onSubmit"
          />
        </div>
      </div>
    </form>

    <!-- Success Message -->
    <div v-if="showSuccessModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div class="flex items-center mb-4">
          <svg class="w-6 h-6 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
          </svg>
          <h3 class="text-lg font-semibold text-gray-900">Técnica Actualizada Exitosamente</h3>
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
import { ref, computed, reactive, onMounted } from 'vue'
import { FormInputField, FormTextarea, FormSelect } from '@/shared/components/forms'
import { SaveButton, ClearButton, SearchButton } from '@/shared/components/buttons'

// Props
interface Props {
  techniqueCodeProp?: string
}

const props = withDefaults(defineProps<Props>(), {
  techniqueCodeProp: ''
})

// Search state
const searchTechniqueCode = ref('')
const isSearching = ref(false)
const searchError = ref('')
const techniqueFound = ref(false)
const foundTechniqueInfo = ref<any>(null)

// Form data
const form = reactive({
  codigo: '',
  nombre: '',
  descripcion: '',
  tipo: '',
  categoria: '',
  estado: '',
  fechaCreacion: '',
  fechaEntrega: '',
  casoAsociado: '',
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
  fechaEntrega: '',
  casoAsociado: '',
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
         form.estado &&
         form.casoAsociado.trim() &&
         form.fechaEntrega &&
         !Object.values(errors).some(error => error !== '')
})

// Methods
const isValidTechniqueCodeFormat = (code: string) => {
  const pattern = /^C\d{4}-\d{5}$/
  return pattern.test(code)
}

const handleTechniqueCodeChange = (value: string) => {
  let formattedValue = value.toUpperCase()
  
  // Auto-format: add C prefix if not present and starts with 4 digits
  if (formattedValue.length >= 4 && !formattedValue.startsWith('C')) {
    formattedValue = 'C' + formattedValue
  }
  
  searchTechniqueCode.value = formattedValue
  if (searchError.value) {
    searchError.value = ''
  }
}

const validateCaseCode = (value: string) => {
  const caseCodePattern = /^\d{4}-\d{5}$/
  if (value && !caseCodePattern.test(value)) {
    errors.casoAsociado = 'El código debe tener el formato YYYY-NNNNN (Ej: 2025-00001)'
  } else {
    errors.casoAsociado = ''
  }
}

const getStatusClass = (estado: string) => {
  switch (estado) {
    case 'En proceso':
      return 'bg-blue-100 text-blue-800'
    case 'Por entregar':
      return 'bg-yellow-100 text-yellow-800'
    case 'Completado':
      return 'bg-green-100 text-green-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const searchTechnique = async () => {
  if (!searchTechniqueCode.value.trim()) {
    searchError.value = 'Ingrese un código de técnica complementaria'
    return
  }

  if (!isValidTechniqueCodeFormat(searchTechniqueCode.value)) {
    searchError.value = 'El código debe tener el formato CYYYY-NNNNN (Ejemplo: C2025-00001)'
    return
  }

  isSearching.value = true
  searchError.value = ''

  try {
    // TODO: Replace with actual API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Mock data - simulate finding technique
    const mockTechnique = {
      id: '1',
      codigo: searchTechniqueCode.value,
      nombre: 'Inmunohistoquímica CD20',
      descripcion: 'Técnica para detección de antígeno CD20 en tejidos linfoides',
      tipo: 'inmunohistoquimica',
      categoria: 'Linfoma',
      estado: 'En proceso',
      fechaCreacion: '2024-01-15',
      fechaEntrega: '2024-01-18',
      casoAsociado: '2025-00001',
      observaciones: 'Técnica rutinaria para diagnóstico de linfoma',
      prioridad: 'Normal'
    }
    
    foundTechniqueInfo.value = mockTechnique
    techniqueFound.value = true
    
    // Populate form with found technique data
    Object.assign(form, mockTechnique)
    
  } catch (error) {
    searchError.value = 'No se encontró la técnica complementaria con ese código'
    foundTechniqueInfo.value = null
    techniqueFound.value = false
  } finally {
    isSearching.value = false
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
  if (!form.estado) {
    errors.estado = 'El estado es requerido'
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
    
    // Simulate successful update
    successMessage.value = `La técnica complementaria "${form.nombre}" ha sido actualizada exitosamente.`
    showSuccessModal.value = true
    
  } catch (error) {
    console.error('Error updating technique:', error)
    // TODO: Show error message
  } finally {
    isSubmitting.value = false
  }
}

const onReset = () => {
  if (props.techniqueCodeProp) {
    // Reset form data but keep code prop
    Object.assign(form, {
      codigo: props.techniqueCodeProp,
      nombre: '',
      descripcion: '',
      tipo: '',
      categoria: '',
      estado: '',
      fechaCreacion: '',
      fechaEntrega: '',
      casoAsociado: '',
      observaciones: '',
      prioridad: 'Normal'
    })
  } else {
    // Reset everything including search
    searchTechniqueCode.value = ''
    techniqueFound.value = false
    foundTechniqueInfo.value = null
    searchError.value = ''
    
    Object.keys(form).forEach(key => {
      if (key === 'prioridad') {
        form[key as keyof typeof form] = 'Normal'
      } else {
        form[key as keyof typeof form] = ''
      }
    })
  }
  
  Object.keys(errors).forEach(key => {
    errors[key as keyof typeof errors] = ''
  })
}

const closeSuccessModal = () => {
  showSuccessModal.value = false
}

const handleSuccessConfirm = () => {
  closeSuccessModal()
  if (!props.techniqueCodeProp) {
    onReset()
  }
}

// Load technique if code prop is provided
onMounted(() => {
  if (props.techniqueCodeProp) {
    searchTechniqueCode.value = props.techniqueCodeProp
    form.codigo = props.techniqueCodeProp
    techniqueFound.value = true
    // TODO: Load technique data from API
  }
})
</script>

<style scoped>
/* Estilos específicos si es necesario */
</style>
