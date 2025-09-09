<template>
  <ComponentCard 
    title="Asignación de patólogo a un caso"
    description="Busque un caso y asigne un patólogo responsable para el análisis."
  >
    <template #icon>
      <DoctorIcon class="w-5 h-5 mr-2 text-blue-600" />
    </template>

    <div class="space-y-6">
      <!-- Sección 1: Búsqueda de Caso -->
      <div class="bg-gray-50 rounded-lg p-3 sm:p-4 lg:p-6 border border-gray-200">
        <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
          <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          Buscar Caso
        </h3>
        
        <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-end">
          <div class="flex-1">
            <FormInputField
              id="codigo-caso"
              v-model="codigoCaso"
              type="text"
              placeholder="Ejemplo: 2025-00001"
              maxlength="10"
              autocomplete="off"
              :disabled="isLoadingSearch"
              @update:model-value="handleCodigoChange"
              @keydown.enter.prevent="buscarCaso"
              @input="handleNumericInput"
              class="flex-1"
            />
            
            <!-- Validación de formato del código -->
            <div v-if="codigoCaso && !isValidCodigoFormat(codigoCaso)" class="mt-1 text-xs text-red-600">
              El código debe tener el formato YYYY-NNNNN (Ejemplo: 2025-00001)
            </div>
          </div>
          
          <div class="flex gap-2 sm:gap-3">
            <SearchButton
              v-if="!casoEncontrado"
              text="Buscar"
              loading-text="Buscando..."
              :loading="isLoadingSearch"
              @click="buscarCaso"
              size="md"
              variant="primary"
            />
            
            <ClearButton
              v-if="casoEncontrado"
              text="Limpiar"
              @click="limpiarFormulario"
            />
          </div>
        </div>

        <!-- Mensaje de error de búsqueda -->
        <div v-if="searchError" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-center">
            <svg class="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <p class="text-sm text-red-600">{{ searchError }}</p>
          </div>
        </div>

        <!-- Información del caso encontrado -->
        <div v-if="casoEncontrado && casoInfo" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div class="flex items-center mb-3">
            <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <h4 class="text-sm font-semibold text-green-800">Caso Encontrado</h4>
          </div>
          
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-sm">
            <div>
              <span class="font-medium text-green-700">Código:</span>
              <p class="text-green-800 font-mono">{{ (casoInfo as any).caso_code }}</p>
            </div>
            <div>
              <span class="font-medium text-green-700">Estado:</span>
              <p class="text-green-800">{{ casoInfo.estado }}</p>
            </div>
            <div>
              <span class="font-medium text-green-700">Paciente:</span>
              <p class="text-green-800 break-words">{{ casoInfo.paciente.nombre }}</p>
            </div>
            <div>
              <span class="font-medium text-green-700">Cédula:</span>
              <p class="text-green-800 font-mono">{{ casoInfo.paciente.paciente_code }}</p>
            </div>
            <div>
              <span class="font-medium text-green-700">Entidad:</span>
              <p class="text-green-800 break-words">{{ casoInfo.paciente.entidad_info?.nombre || 'N/A' }}</p>
            </div>
            <div>
              <span class="font-medium text-green-700">Patólogo Actual:</span>
              <p class="text-green-800 break-words">{{ casoInfo.patologo_asignado?.nombre || 'Sin asignar' }}</p>
            </div>
          </div>
          
          <!-- Lista de muestras -->
          <div v-if="casoInfo.muestras?.length > 0" class="mt-3">
            <span class="font-medium text-green-700 text-sm">Muestras:</span>
            <div class="flex flex-wrap gap-2 mt-1">
              <span
                v-for="muestra in casoInfo.muestras"
                :key="muestra.region_cuerpo"
                class="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-md"
              >
                {{ muestra.region_cuerpo }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Sección 2: Formulario de Asignación -->
      <div v-if="casoEncontrado" class="space-y-6">
        <!-- Selección de Patólogo -->
        <div class="bg-white border border-gray-200 rounded-lg p-3 sm:p-4 lg:p-6">
          <div class="max-w-md">
            <PathologistList
              v-model="formData.patologoId"
              label="Patólogo Asignado"
              placeholder="Buscar y seleccionar patólogo..."
              :required="true"
              :errors="validationErrors.patologoId"
              help-text="Seleccione el patólogo asignado a este caso"
            />
          </div>
        </div>

        <!-- Botones de Acción -->
        <div class="flex flex-col sm:flex-row justify-end gap-3 pt-4 border-t border-gray-200">
          <ClearButton
            @click="limpiarFormulario"
          />
          
          <SaveButton
            :text="getButtonText"
            loading-text="Asignando..."
            :loading="isLoadingAssignment"
            @click="handleAsignarClick"
            :disabled="!isFormValid"
          />
        </div>

        <!-- Alerta de Validación -->
        <ValidationAlert
          :visible="showValidationError"
          :errors="validationErrorsList"
        />
      </div>

      <!-- Notificación de Éxito/Error -->
      <div ref="notificationContainer">
        <Notification
          :visible="notification.visible"
          :type="notification.type"
          :title="notification.title"
          :message="notification.message"
          :inline="true"
          :auto-close="false"
          @close="closeNotification"
        />
      </div>
    </div>
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed, ref, reactive, watch } from 'vue'
import { usePathologistAPI } from '../composables/usePathologistAPI'
import { useNotifications } from '../composables/useNotifications'
import casesApiService from '../services/casesApi.service'
import type { 
  PathologistFormData, 
  CaseModel
} from '../types'

// Componentes UI
import { ComponentCard } from '@/shared/components'
import { FormInputField } from '@/shared/components/forms'
import { PathologistList } from '@/shared/components/List'
import { SearchButton, SaveButton, ClearButton } from '@/shared/components/buttons'
import { ValidationAlert, Notification } from '@/shared/components/feedback'
import { DoctorIcon } from '@/assets/icons'

// ============================================================================
// ESTADO DEL COMPONENTE
// ============================================================================

// Estado de búsqueda
const codigoCaso = ref('')
const isLoadingSearch = ref(false)
const casoEncontrado = ref(false)
const searchError = ref('')

// Información del caso
const casoInfo = ref<CaseModel | null>(null)

// Estado del formulario
const formData = reactive<PathologistFormData>({
  patologoId: '',
  fechaAsignacion: ''
})

// Estado de validación
const hasAttemptedSubmit = ref(false)
const showValidationError = ref(false)
const isLoadingAssignment = ref(false)

// Referencias
const notificationContainer = ref<HTMLElement | null>(null)

// ============================================================================
// COMPOSABLES
// ============================================================================

const { assignPathologist } = usePathologistAPI()
const { notification, showNotification, closeNotification } = useNotifications()

// ============================================================================
// COMPUTED PROPERTIES
// ============================================================================

/**
 * Verifica si el formulario es válido para proceder con la asignación
 */
const isFormValid = computed(() => {
  return casoEncontrado.value && formData.patologoId.trim() !== ''
})

/**
 * Errores de validación específicos por campo
 */
const validationErrors = computed(() => {
  const errors: Record<string, string[]> = {
    patologoId: []
  }
  
  if (hasAttemptedSubmit.value && !formData.patologoId) {
    errors.patologoId.push('Debe seleccionar un patólogo')
  }
  
  return errors
})

/**
 * Lista de errores de validación para mostrar en la alerta
 */
const validationErrorsList = computed(() => {
  const errors: string[] = []
  
  if (!casoEncontrado.value) {
    errors.push('Debe buscar y encontrar un caso primero')
  }
  if (!formData.patologoId) {
    errors.push('Debe seleccionar un patólogo')
  }
  
  return errors
})

/**
 * Texto del botón de asignación según el estado del caso
 */
const getButtonText = computed(() => {
  return casoInfo.value?.patologo_asignado ? 'Reasignar Patólogo' : 'Asignar Patólogo'
})

// ============================================================================
// FUNCIONES DE VALIDACIÓN
// ============================================================================

/**
 * Valida el formato del código de caso (YYYY-NNNNN)
 * @param codigo - Código a validar
 * @returns true si el formato es válido
 */
const isValidCodigoFormat = (codigo: string | undefined | null): boolean => {
  if (!codigo || typeof codigo !== 'string' || codigo.trim() === '') return false
  const regex = /^\d{4}-\d{5}$/
  return regex.test(codigo.trim())
}

// ============================================================================
// FUNCIONES DE MANIPULACIÓN DE DATOS
// ============================================================================

/**
 * Maneja el cambio en el campo de código de caso con formateo automático
 * @param value - Nuevo valor del campo
 */
const handleCodigoChange = (value: string) => {
  // Limpiar caracteres no válidos (solo números y guión)
  value = value.replace(/[^\d-]/g, '')
  
  // Limitar a 10 caracteres máximo
  value = value.slice(0, 10)
  
  // Formatear automáticamente: agregar guión después de 4 dígitos
  if (value.length >= 4 && !value.includes('-')) {
    value = value.slice(0, 4) + '-' + value.slice(4)
  }
  
  // Evitar múltiples guiones
  const parts = value.split('-')
  if (parts.length > 2) {
    value = parts[0] + '-' + parts.slice(1).join('')
  }
  
  // Asegurar que el guión esté en la posición correcta
  if (value.includes('-') && value.indexOf('-') !== 4) {
    const digits = value.replace(/-/g, '')
    if (digits.length >= 4) {
      value = digits.slice(0, 4) + '-' + digits.slice(4, 9)
    } else {
      value = digits
    }
  }
  
  codigoCaso.value = value
}

/**
 * Maneja la entrada de solo números en el campo de código de caso
 */
const handleNumericInput = (value: string) => {
  handleCodigoChange(value)
}

// ============================================================================
// FUNCIONES DE BÚSQUEDA
// ============================================================================

/**
 * Busca un caso por su código en el sistema
 */
const buscarCaso = async () => {
  // Validaciones previas
  if (!codigoCaso.value.trim()) {
    searchError.value = 'Por favor, ingrese un código de caso'
    return
  }

  if (!isValidCodigoFormat(codigoCaso.value)) {
    searchError.value = 'El código debe tener el formato YYYY-NNNNN (Ejemplo: 2025-00001)'
    return
  }

  // Inicializar estado de búsqueda
  isLoadingSearch.value = true
  searchError.value = ''
  casoEncontrado.value = false

  try {

    
    // Realizar búsqueda en el backend
    const casoResponse = await casesApiService.getCaseByCode(codigoCaso.value.trim())
    
    // Caso encontrado exitosamente
    casoEncontrado.value = true
    casoInfo.value = casoResponse
    
    
    
  } catch (error: any) {
    casoEncontrado.value = false
    casoInfo.value = null
    
    // Configurar mensaje de error específico
    searchError.value = getErrorMessage(error)
  } finally {
    isLoadingSearch.value = false
  }
}

/**
 * Obtiene el mensaje de error apropiado según el tipo de error
 * @param error - Error capturado
 * @returns Mensaje de error formateado
 */
const getErrorMessage = (error: any): string => {
  if (error.message.includes('404') || error.message.includes('no encontrado')) {
    return `No existe un caso con el código "${codigoCaso.value}"`
  } else if (error.message.includes('400')) {
    return 'Formato de código de caso inválido'
  } else if (error.message.includes('500')) {
    return 'Error interno del servidor. Inténtelo más tarde.'
  } else {
    return 'Error al buscar el caso. Inténtelo nuevamente.'
  }
}

// ============================================================================
// FUNCIONES DE ASIGNACIÓN
// ============================================================================

/**
 * Asigna un patólogo al caso encontrado
 */
const asignarPatologo = async () => {
  if (!isFormValid.value || !casoInfo.value) return

  isLoadingAssignment.value = true

  try {
    // Usar el código correcto del caso (backend devuelve caso_code)
    const codigoCaso = (casoInfo.value as any).caso_code
    
    if (!codigoCaso) {
      throw new Error(`Código del caso no disponible. Estructura: ${JSON.stringify(casoInfo.value)}`)
    }
    
    // Realizar asignación usando el composable
    const result = await assignPathologist(codigoCaso, {
      patologoId: formData.patologoId,
      fechaAsignacion: new Date().toISOString().split('T')[0]
    })
    
    if (result.success) {
      await handleAsignacionExitosa(result)
    } else {
      throw new Error(result.message || 'Error al asignar patólogo')
    }
    
  } catch (error: any) {
    await handleErrorAsignacion(error)
  } finally {
    isLoadingAssignment.value = false
  }
}

/**
 * Maneja la asignación exitosa del patólogo
 * @param result - Resultado de la asignación
 */
const handleAsignacionExitosa = async (result: any) => {
  
  
  // Actualizar información del caso con el patólogo asignado
  if (result.assignment?.pathologist && casoInfo.value) {
    casoInfo.value.patologo_asignado = {
      codigo: result.assignment.pathologist.id,
      nombre: result.assignment.pathologist.nombre
    }
  }
  
  // Obtener el código correcto del caso (backend devuelve caso_code)
  const codigoCaso = (casoInfo.value as any).caso_code
  
  // Mostrar notificación de éxito
  const accion = casoInfo.value?.patologo_asignado ? 'reasignado' : 'asignado'
  showNotification(
    'success',
    `¡Patólogo ${accion} exitosamente!`,
    `El patólogo ha sido ${accion} al caso ${codigoCaso} correctamente.`,
    0
  )

  // Emitir evento de éxito
  emit('patologo-asignado', {
    codigoCaso: codigoCaso,
    patologo: formData.patologoId
  })

  // Limpiar formulario
  limpiarFormulario()
}

/**
 * Maneja errores durante la asignación del patólogo
 * @param error - Error capturado
 */
const handleErrorAsignacion = async (error: any) => {
  
  // Si el error indica que ya tiene patólogo asignado, tratarlo como reasignación exitosa
  if (isReasignacionError(error.message)) {
    
    
    // Obtener el código correcto del caso (backend devuelve caso_code)
    const codigoCaso = (casoInfo.value as any).caso_code
    
    showNotification(
      'success',
      '¡Patólogo asignado exitosamente!',
      `El patólogo ha sido reasignado al caso ${codigoCaso} correctamente.`,
      0
    )

    emit('patologo-asignado', {
      codigoCaso: codigoCaso,
      patologo: formData.patologoId
    })

    limpiarFormulario()
  } else {
    // Error real
    showNotification(
      'error',
      'Error al Asignar Patólogo',
      error.message || 'No se pudo asignar el patólogo. Por favor, inténtelo nuevamente.',
      0
    )
  }
}

/**
 * Verifica si el error corresponde a una reasignación
 * @param message - Mensaje de error
 * @returns true si es un error de reasignación
 */
const isReasignacionError = (message: string): boolean => {
  const reasignacionKeywords = ['ya tiene', 'already', 'asignado', 'assigned']
  return reasignacionKeywords.some(keyword => message.includes(keyword))
}

// ============================================================================
// FUNCIONES DE UTILIDAD
// ============================================================================

/**
 * Limpia completamente el formulario y reinicia el estado
 */
const limpiarFormulario = () => {
  codigoCaso.value = ''
  casoEncontrado.value = false
  searchError.value = ''
  casoInfo.value = null
  formData.patologoId = ''
  formData.fechaAsignacion = ''
  showValidationError.value = false
  hasAttemptedSubmit.value = false
}

/**
 * Maneja el click del botón de asignar con validación
 */
const handleAsignarClick = () => {
  hasAttemptedSubmit.value = true
  
  if (!isFormValid.value) {
    showValidationError.value = true
    return
  }

  showValidationError.value = false
  asignarPatologo()
}

// ============================================================================
// WATCHERS
// ============================================================================

// Ocultar error de validación cuando el formulario se vuelve válido
watch([() => formData.patologoId, casoEncontrado], () => {
  if (showValidationError.value && isFormValid.value) {
    showValidationError.value = false
  }
})

// ============================================================================
// EMITS Y EXPOSICIÓN
// ============================================================================

// Definir eventos que emite el componente
const emit = defineEmits<{
  'patologo-asignado': [data: { codigoCaso: string; patologo: string }]
}>()

// Exponer funciones para uso externo
defineExpose({
  limpiarFormulario,
  buscarCaso
})
</script>
