<template>
  <div v-if="localModel.residenteCode" class="space-y-6">
    <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4">
      <div class="col-span-full">
        <h4 class="text-base font-semibold text-gray-800">Editar Residente</h4>
        <p class="text-sm text-gray-500 mt-1">Modifica los datos del residente médico</p>
      </div>

      <!-- Código y Nombre -->
      <FormInputField 
        class="col-span-full md:col-span-6" 
        label="Código del residente" 
        placeholder="Ejemplo: 12345678" 
        v-model="localModel.residenteCode"
        :error="formErrors.residenteCode || codeValidationError"
        :disabled="true"
        autocomplete="off"
      />
      <FormInputField 
        class="col-span-full md:col-span-6" 
        label="Nombre completo" 
        placeholder="Ejemplo: María Elena Rodríguez" 
        v-model="localModel.residenteName"
        :error="formErrors.residenteName"
        autocomplete="name" 
      />

      <!-- Iniciales y Email -->
      <FormInputField 
        class="col-span-full md:col-span-6" 
        label="Iniciales del residente" 
        placeholder="Ejemplo: MER" 
        v-model="localModel.InicialesResidente"
        :error="formErrors.InicialesResidente"
        autocomplete="off"
        maxlength="10"
      />
      <FormInputField 
        class="col-span-full md:col-span-6" 
        label="Email" 
        type="email" 
        placeholder="maria.rodriguez@udea.edu.co" 
        v-model="localModel.ResidenteEmail"
        :error="formErrors.ResidenteEmail || emailValidationError"
        @blur="validateEmail"
        autocomplete="email" 
      />

      <!-- Registro médico -->
      <FormInputField 
        class="col-span-full md:col-span-6" 
        label="Registro médico" 
        placeholder="Ejemplo: RM-2024-001" 
        v-model="localModel.registro_medico"
        :error="formErrors.registro_medico || licenseValidationError"
        @blur="validateMedicalLicense"
      />

      <!-- Contraseña y Confirmación -->
      <FormInputField 
        class="col-span-full md:col-span-6" 
        label="Nueva contraseña (opcional)" 
        type="password" 
        placeholder="••••••••" 
        :model-value="localModel.password || ''"
        @update:model-value="val => (localModel.password = val)"
        :error="formErrors.password"
        autocomplete="new-password"
      />
      <FormInputField 
        class="col-span-full md:col-span-6" 
        label="Confirmar contraseña" 
        type="password" 
        placeholder="••••••••" 
        :model-value="localModel.passwordConfirm || ''"
        @update:model-value="val => (localModel.passwordConfirm = val)"
        :error="formErrors.passwordConfirm"
        autocomplete="new-password"
      />

      <!-- Observaciones -->
      <FormTextarea 
        class="col-span-full" 
        label="Observaciones" 
        placeholder="Notas adicionales sobre el residente (opcional)" 
        v-model="localModel.observaciones" 
        :rows="3"
        :error="formErrors.observaciones"
      />

      <!-- Estado activo -->
      <div class="col-span-full md:col-span-6 flex items-center pt-3">
        <FormCheckbox label="Activo" v-model="localModel.isActive" />
      </div>

      <!-- Botones de acción -->
      <div class="col-span-full flex flex-col sm:flex-row gap-2 sm:gap-3 sm:justify-end pt-4 border-t border-gray-200">
        <ClearButton type="button" @click="onReset" :disabled="isLoading || !hasChanges" variant="secondary" :text="'Reiniciar'" :icon="'reset'">
          <template #icon>
            <RefreshIcon class="w-4 h-4 mr-2" />
          </template>
        </ClearButton>
        <SaveButton text="Actualizar Residente" type="submit" :disabled="!canSubmit || isLoading || !hasChanges" :loading="isLoading" />
      </div>

      <!-- Notificación -->
      <div v-if="notification.visible" ref="notificationContainer" class="col-span-full">
        <Notification
          :visible="true"
          :type="notification.type"
          :title="notification.title"
          :message="notification.message"
          :inline="true"
          :auto-close="false"
          @close="() => {}"
        >
          <template v-if="notification.type === 'success' && updatedResident" #content>
            <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div class="space-y-4">
                <!-- Información principal del residente -->
                <div class="mb-4 pb-3 border-b border-gray-100">
                  <h3 class="text-xl font-bold text-gray-900 mb-2">{{ updatedResident.residenteName }}</h3>
                  <p class="text-gray-600">
                    <span class="font-medium">Código:</span> 
                    <span class="font-mono font-bold text-gray-800 ml-1">{{ updatedResident.residenteCode }}</span>
                  </p>
                </div>
                
                <!-- Detalles del residente en vertical -->
                <div class="space-y-4 text-sm">
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Iniciales:</span>
                    <p class="text-gray-800 font-semibold">{{ updatedResident.InicialesResidente }}</p>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Email:</span>
                    <p class="text-gray-800 font-semibold">{{ updatedResident.ResidenteEmail }}</p>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Registro médico:</span>
                    <p class="text-gray-800 font-semibold">{{ updatedResident.registro_medico }}</p>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Estado:</span>
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      :class="updatedResident.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                      {{ updatedResident.isActive ? 'Activo' : 'Inactivo' }}
                    </span>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Fecha de actualización:</span>
                    <p class="text-gray-800 font-semibold">{{ formatDate(updatedResident.fecha_actualizacion) }}</p>
                  </div>
                </div>
                
                <!-- Observaciones -->
                <div v-if="updatedResident.observaciones">
                  <span class="text-gray-500 font-medium block mb-2">Observaciones:</span>
                  <p class="text-gray-800 bg-gray-50 p-3 rounded-lg">{{ updatedResident.observaciones }}</p>
                </div>
              </div>
            </div>
          </template>
        </Notification>
      </div>

      <!-- Alerta de Validación -->
      <ValidationAlert
        :visible="validationState.showValidationError && validationState.hasAttemptedSubmit"
        :errors="validationErrors"
      />
    </form>
  </div>
  <div v-else class="text-center py-8">
    <p class="text-gray-500">No se pudieron cargar los datos del residente para edición.</p>
    <p class="text-sm text-gray-400 mt-2">Faltan datos críticos: ID o código del residente.</p>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, watch, nextTick, ref } from 'vue'
import { FormInputField, FormCheckbox, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton } from '@/shared/components/buttons'
import { Notification, ValidationAlert } from '@/shared/components/feedback'
import { useResidentEdition } from '../../composables/useResidentEdition'
import type { ResidentEditFormModel, ResidentUpdateResponse } from '../../types/resident.types'
import { RefreshIcon } from '@/assets/icons'

type Usuario = {
  id: string;
  residenteName?: string;
  nombre?: string;
  tipo: string;
  residenteCode?: string;
  codigo?: string;
  documento?: string;
  ResidenteEmail?: string;
  email?: string;
  InicialesResidente?: string;
  registro_medico?: string;
  observaciones?: string;
  activo?: boolean;
  isActive?: boolean;
}

// Props y emits
const props = defineProps<{
  usuario: Usuario;
}>()

const emit = defineEmits<{
  (e: 'usuario-actualizado', data: any): void;
}>()

// Referencias
const notificationContainer = ref<HTMLElement | null>(null)

// Estado del residente actualizado
const updatedResident = ref<ResidentUpdateResponse | null>(null)

// Estado de notificación
const notification = reactive({
  visible: false,
  type: 'success' as 'success' | 'error' | 'warning' | 'info',
  title: '',
  message: ''
})

// Estado de validación
const validationState = reactive({
  showValidationError: false,
  hasAttemptedSubmit: false
})

// Composable para manejo de backend
const {
  isLoading,
  codeValidationError,
  emailValidationError,
  licenseValidationError,
  canSubmit: canSubmitFromComposable,
  validateForm,
  checkEmailAvailability,
  checkLicenseAvailability,
  updateResident,
  setInitialData,
  resetToOriginal,
  clearMessages,
  createHasChanges
} = useResidentEdition()

// Modelo local del formulario
const localModel = reactive<ResidentEditFormModel>({
  id: '',
  residenteName: '',
  InicialesResidente: '',
  residenteCode: '',
  ResidenteEmail: '',
  registro_medico: '',
  observaciones: '',
  isActive: true,
  password: '',
  passwordConfirm: ''
})

// Errores del formulario
const formErrors = reactive({
  residenteName: '',
  InicialesResidente: '',
  residenteCode: '',
  ResidenteEmail: '',
  registro_medico: '',
  observaciones: '',
  password: '',
  passwordConfirm: ''
})

// Computed para detectar cambios
const hasChanges = computed(() => createHasChanges(localModel))

// Computed para verificar si se puede enviar
const canSubmit = computed(() => {
  const passwordOnlyValid = !!localModel.password && localModel.password.trim().length >= 6
  const baseValid = canSubmitFromComposable.value && 
    localModel.residenteName?.trim().length >= 2 &&
    localModel.InicialesResidente?.trim().length >= 2 &&
    localModel.residenteCode?.trim().length >= 3 &&
    localModel.ResidenteEmail?.trim().length > 0 &&
    localModel.registro_medico?.trim().length >= 3

  // Permitir envío si solo cambia contraseña válida
  return baseValid || passwordOnlyValid
})

// Lista de errores de validación
const validationErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  
  const errors: string[] = []
  
  if (!localModel.residenteName || formErrors.residenteName) {
    errors.push('Nombre completo válido requerido')
  }
  if (!localModel.InicialesResidente || formErrors.InicialesResidente) {
    errors.push('Iniciales válidas requeridas')
  }
  if (!localModel.residenteCode || formErrors.residenteCode) {
    errors.push('Código de residente válido requerido')
  }
  if (!localModel.ResidenteEmail || formErrors.ResidenteEmail) {
    errors.push('Email válido requerido')
  }
  if (!localModel.registro_medico || formErrors.registro_medico) {
    errors.push('Registro médico válido requerido')
  }
  if (formErrors.observaciones) {
    errors.push('Observaciones válidas requeridas')
  }
  
  return errors
})

// Normalizador robusto de campos (residente -> resident, etc.)
const normalizeResident = (raw: any): ResidentEditFormModel | null => {
  if (!raw) return null
  const name = raw.residenteName || raw.residentName || raw.nombre || raw.name || ''
  const code = raw.residenteCode || raw.residentCode || raw.codigo || raw.code || raw.documento || ''
  const initials = raw.InicialesResidente || raw.inicialesResidente || raw.initials || ''
  const email = raw.ResidenteEmail || raw.residentEmail || raw.email || ''
  const registro = raw.registro_medico || raw.medicalLicense || raw.medical_license || ''
  const obs = raw.observaciones || raw.observations || raw.notes || ''
  const active = raw.isActive !== undefined ? raw.isActive : (raw.is_active !== undefined ? raw.is_active : (raw.activo !== undefined ? raw.activo : true))
  return {
    id: raw.id || raw._id || code,
    residenteName: String(name),
    InicialesResidente: String(initials),
    residenteCode: String(code),
    ResidenteEmail: String(email),
    registro_medico: String(registro),
    observaciones: String(obs),
    isActive: !!active
  }
}

// Función para cargar datos iniciales
const loadInitialData = () => {
  const mappedData = normalizeResident(props.usuario)
  if (!mappedData) return
  Object.assign(localModel, mappedData)
  setInitialData(mappedData)
}

// Watcher para cargar datos cuando cambia el usuario
watch(() => props.usuario, () => {
  if (props.usuario) {
    loadInitialData()
  }
}, { immediate: true, deep: true })

// Watcher para limpiar errores cuando el usuario está escribiendo
watch(() => localModel, () => {
  if (validationState.hasAttemptedSubmit && !notification.visible) {
    clearMessages()
    clearFormErrors()
  }
}, { deep: true })

// Funciones de validación
const validateEmail = async () => {
  formErrors.ResidenteEmail = ''
  
  if (!localModel.ResidenteEmail?.trim()) {
    formErrors.ResidenteEmail = 'El email es requerido'
    return
  }
  
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(localModel.ResidenteEmail)) {
    formErrors.ResidenteEmail = 'Formato de email inválido'
    return
  }
  
  await checkEmailAvailability(localModel.ResidenteEmail)
  if (emailValidationError.value) {
    formErrors.ResidenteEmail = emailValidationError.value
  }
}

const validateMedicalLicense = async () => {
  formErrors.registro_medico = ''
  
  if (!localModel.registro_medico?.trim()) {
    formErrors.registro_medico = 'El registro médico es requerido'
    return
  }
  
  if (localModel.registro_medico.length < 3) {
    formErrors.registro_medico = 'Mínimo 3 caracteres'
    return
  }
  
  if (localModel.registro_medico.length > 50) {
    formErrors.registro_medico = 'Máximo 50 caracteres'
    return
  }
  
  await checkLicenseAvailability(localModel.registro_medico)
  if (licenseValidationError.value) {
    formErrors.registro_medico = licenseValidationError.value
  }
}

// Limpiar errores del formulario
const clearFormErrors = () => {
  Object.keys(formErrors).forEach(key => {
    formErrors[key as keyof typeof formErrors] = ''
  })
}

// Funciones de notificación
const showNotification = (type: typeof notification.type, title: string, message: string) => {
  notification.type = type
  notification.title = title
  notification.message = message
  notification.visible = true
}

const scrollToNotification = async () => {
  await nextTick()
  if (notificationContainer.value) {
    notificationContainer.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

// Función para formatear fecha
const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return 'Fecha no disponible'
  }
}

// Envío del formulario
const submit = async () => {
  validationState.hasAttemptedSubmit = true
  clearFormErrors()
  
  // Validar contraseñas
  if (localModel.password && localModel.password.trim().length > 0) {
    if (localModel.password.trim().length < 6) {
      formErrors.password = 'La contraseña debe tener al menos 6 caracteres'
      validationState.showValidationError = true
      return
    }
    if (localModel.password !== localModel.passwordConfirm) {
      formErrors.passwordConfirm = 'Las contraseñas no coinciden'
      validationState.showValidationError = true
      return
    }
  }
  
  const validation = validateForm(localModel)
  if (!validation.isValid) {
    Object.assign(formErrors, validation.errors)
    validationState.showValidationError = true
    return
  }
  
  validationState.showValidationError = false
  
  try {
    const result = await updateResident(localModel)
    if ((result as any).success && (result as any).data) {
      const data = (result as any).data
      updatedResident.value = data
      showNotification('success', '¡Residente Actualizado Exitosamente!', '')
      await scrollToNotification()
      emit('usuario-actualizado', { ...data, nombre: data.residenteName, codigo: data.residenteCode, tipo: 'residente' })
    } else {
      showNotification('error', 'Error al Actualizar Residente', 'No se pudo actualizar el residente')
    }
  } catch (error: any) {
    showNotification('error', 'Error al Actualizar Residente', error.message || 'Error inesperado')
  }
}

const onReset = () => {
  const original = resetToOriginal()
  if (original) {
    Object.assign(localModel, original)
    localModel.password = ''
    localModel.passwordConfirm = ''
    clearFormErrors()
    validationState.hasAttemptedSubmit = false
    validationState.showValidationError = false
  }
}


</script>
