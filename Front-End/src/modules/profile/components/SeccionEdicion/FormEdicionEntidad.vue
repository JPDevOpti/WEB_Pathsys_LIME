<template>
  <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4">
    <div class="col-span-full">
      <h4 class="text-base font-semibold text-gray-800">Editar Entidad</h4>
      <p class="text-sm text-gray-600 mt-1">Modifica los datos de la entidad</p>
    </div>

    <!-- Código y Nombre (código SIEMPRE a la izquierda) -->
    <FormInputField class="col-span-full md:col-span-6" label="Código de entidad" v-model="localModel.EntidadCode" :error="formErrors.EntidadCode" @blur="validateCode" :disabled="true" />
    <FormInputField class="col-span-full md:col-span-6" label="Nombre de entidad" v-model="localModel.EntidadName" :error="formErrors.EntidadName" />

    <!-- Observaciones -->
    <FormTextarea class="col-span-full" label="Observaciones" v-model="localModel.observaciones" rows="3" :error="formErrors.observaciones" />

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
      <SaveButton text="Actualizar Entidad" type="submit" :disabled="!canSubmit || isLoading || !hasChanges" :loading="isLoading" />
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
        <template v-if="notification.type === 'success' && updatedEntity" #content>
          <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
            <div class="space-y-4">
              <!-- Información principal de la entidad -->
              <div class="mb-4 pb-3 border-b border-gray-100">
                <h3 class="text-xl font-bold text-gray-900 mb-2">{{ updatedEntity.EntidadName }}</h3>
                <p class="text-gray-600">
                  <span class="font-medium">Código:</span>
                  <span class="font-mono font-bold text-gray-800 ml-1">{{ updatedEntity.EntidadCode }}</span>
                </p>
              </div>

              <!-- Detalles en vertical -->
              <div class="space-y-4 text-sm">
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Estado:</span>
                  <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                    :class="updatedEntity.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                    {{ updatedEntity.isActive ? 'Activo' : 'Inactivo' }}
                  </span>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Última actualización:</span>
                  <p class="text-gray-800 font-semibold">{{ formatDate(updatedEntity.fecha_actualizacion) }}</p>
                </div>
              </div>

              <!-- Observaciones -->
              <div v-if="updatedEntity.observaciones">
                <span class="text-gray-500 font-medium block mb-2">Observaciones:</span>
                <p class="text-gray-800 bg-gray-50 p-3 rounded-lg">{{ updatedEntity.observaciones }}</p>
              </div>
            </div>
          </div>
        </template>
      </Notification>
    </div>

    <!-- Alerta de Validación -->
    <ValidationAlert :visible="validationState.showValidationError && validationState.hasAttemptedSubmit" :errors="validationErrors" />
  </form>
 </template>

<script setup lang="ts">
import { reactive, computed, watch, ref, nextTick } from 'vue'
import { FormInputField, FormCheckbox, FormTextarea } from '@/shared/components/ui/forms'
import { SaveButton, ClearButton } from '@/shared/components/ui/buttons'
import { Notification, ValidationAlert } from '@/shared/components/ui/feedback'
import { useEntityEdition } from '../../composables/useEntityEdition'
import type { EntityEditFormModel, EntityUpdateResponse } from '../../types/entity.types'
import { RefreshIcon } from '@/shared/icons'

const props = defineProps<{ usuario: any; usuarioActualizado: boolean; mensajeExito: string }>()
const emit = defineEmits<{ (e: 'usuario-actualizado', payload: any): void; (e: 'cancelar'): void }>()

const {
  state,
  isLoadingEntity,
  codeValidationError,
  originalEntityData,
  canSubmit,
  validateForm,
  checkCodeAvailability,
  updateEntity,
  setInitialData,
  resetToOriginal,
  clearState,
  clearMessages,
  hasChangesFactory
} = useEntityEdition()

const isLoading = computed(() => state.isLoading)

// Notificación
const notificationContainer = ref<HTMLElement | null>(null)
const notification = reactive({
  visible: false,
  type: 'success' as 'success' | 'error' | 'warning' | 'info',
  title: '',
  message: ''
})
const updatedEntity = ref<EntityUpdateResponse | null>(null)
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

const localModel = reactive<EntityEditFormModel>({
  id: '',
  EntidadName: '',
  EntidadCode: '',
  observaciones: '',
  isActive: true
})

const formErrors = reactive({
  EntidadName: '',
  EntidadCode: '',
  observaciones: ''
})

const validationState = reactive({ showValidationError: false, hasAttemptedSubmit: false })

const validationErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  const errors: string[] = []
  if (!localModel.EntidadName || formErrors.EntidadName) errors.push('Nombre válido requerido')
  if (!localModel.EntidadCode || formErrors.EntidadCode) errors.push('Código válido requerido')
  if (formErrors.observaciones) errors.push('Observaciones válidas requeridas')
  return errors
})

const hasChanges = computed(() => hasChangesFactory(localModel))

const validateCode = async () => {
  formErrors.EntidadCode = ''
  if (!localModel.EntidadCode?.trim()) { formErrors.EntidadCode = 'El código es requerido'; return }
  if (localModel.EntidadCode.length < 2) { formErrors.EntidadCode = 'Mínimo 2 caracteres'; return }
  if (localModel.EntidadCode.length > 20) { formErrors.EntidadCode = 'Máximo 20 caracteres'; return }
  if (!/^[A-Z0-9_-]+$/i.test(localModel.EntidadCode)) { formErrors.EntidadCode = 'Solo letras, números, guiones y guiones bajos'; return }
  const originalCode = originalEntityData.value?.EntidadCode
  await checkCodeAvailability(localModel.EntidadCode, originalCode)
  if (codeValidationError.value) formErrors.EntidadCode = codeValidationError.value
}

const clearFormErrors = () => { Object.keys(formErrors).forEach(k => { (formErrors as any)[k] = '' }) }

const submit = async () => {
  validationState.hasAttemptedSubmit = true
  clearFormErrors()
  const validation = validateForm(localModel)
  if (!validation.isValid) { Object.assign(formErrors, validation.errors); validationState.showValidationError = true; return }
  validationState.showValidationError = false
  try {
    const result = await updateEntity(localModel)
    if (result.success && result.data) {
      updatedEntity.value = result.data
      showNotification('success', '¡Entidad Actualizada Exitosamente!', '')
      await scrollToNotification()
      emit('usuario-actualizado', { ...result.data, nombre: result.data.EntidadName, codigo: result.data.EntidadCode, tipo: 'entidad' })
    } else {
      showNotification('error', 'Error al Actualizar Entidad', 'No se pudo actualizar la entidad')
    }
  } catch (error: any) {
    showNotification('error', 'Error al Actualizar Entidad', error.message || 'Error inesperado')
  }
}

const onReset = () => {
  const original = resetToOriginal()
  if (original) { Object.assign(localModel, original); clearFormErrors(); validationState.hasAttemptedSubmit = false; validationState.showValidationError = false }
}



watch(() => props.usuario, (u) => {
  if (u) {
    const mapped: EntityEditFormModel = {
      id: u.id || u.codigo || u.EntidadCode,
      EntidadName: u.EntidadName || u.nombre || '',
      EntidadCode: u.EntidadCode || u.codigo || '',
      observaciones: u.observaciones || '',
      isActive: u.isActive ?? u.activo ?? true
    }
    Object.assign(localModel, mapped)
    setInitialData(mapped)
  } else {
    clearState()
  }
}, { immediate: true, deep: true })
</script>


