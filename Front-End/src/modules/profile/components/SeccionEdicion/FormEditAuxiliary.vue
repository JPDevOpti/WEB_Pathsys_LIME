<template>
  <div v-if="localModel.auxiliarCode" class="space-y-6">
    <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4">
      <div class="col-span-full">
        <h4 class="text-base font-semibold text-gray-800">Editar Auxiliar administrativo</h4>
        <p class="text-sm text-gray-500 mt-1">Modifica los datos del auxiliar</p>
      </div>

      <FormInputField class="md:col-span-6" label="Código del auxiliar" :disabled="true" v-model="localModel.auxiliarCode" />
      <FormInputField class="md:col-span-6" label="Nombre completo" v-model="localModel.auxiliarName" :error="formErrors.auxiliarName" />

      <FormInputField class="md:col-span-6" label="Email" type="email" v-model="localModel.AuxiliarEmail" :error="formErrors.AuxiliarEmail" autocomplete="email" />

      <FormInputField class="md:col-span-6" label="Nueva contraseña (opcional)" type="password" placeholder="••••••••" :model-value="localModel.password || ''" @update:model-value="val => (localModel.password = val)" :error="formErrors.password" autocomplete="new-password" />
      <FormInputField class="md:col-span-6" label="Confirmar contraseña" type="password" placeholder="••••••••" :model-value="localModel.passwordConfirm || ''" @update:model-value="val => (localModel.passwordConfirm = val)" :error="formErrors.passwordConfirm" autocomplete="new-password" />

      <FormTextarea class="col-span-full" label="Observaciones" v-model="localModel.observaciones" :rows="3" :error="formErrors.observaciones" />

      <div class="md:col-span-6 flex items-center pt-3">
        <FormCheckbox label="Activo" v-model="localModel.isActive" />
      </div>

      <div class="col-span-full flex flex-col sm:flex-row gap-2 sm:gap-3 sm:justify-end pt-4 border-t border-gray-200">
        <ClearButton type="button" @click="onReset" :disabled="isLoading || !hasChanges" variant="secondary" :text="'Reiniciar'" :icon="'reset'">
          <template #icon>
            <RefreshIcon class="w-4 h-4 mr-2" />
          </template>
        </ClearButton>
        <SaveButton text="Actualizar Auxiliar" type="submit" :disabled="!canSubmitButton || isLoading || !hasChanges" :loading="isLoading" />
      </div>

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
          <template v-if="notification.type === 'success' && updatedAuxiliary" #content>
            <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div class="space-y-4">
                <div class="mb-4 pb-3 border-b border-gray-100">
                  <h3 class="text-xl font-bold text-gray-900 mb-2">{{ updatedAuxiliary.auxiliarName }}</h3>
                  <p class="text-gray-600">
                    <span class="font-medium">Código:</span>
                    <span class="font-mono font-bold text-gray-800 ml-1">{{ updatedAuxiliary.auxiliarCode }}</span>
                  </p>
                </div>
                <div class="space-y-3 text-sm">
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Email:</span>
                    <p class="text-gray-800 font-semibold">{{ updatedAuxiliary.AuxiliarEmail }}</p>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Estado:</span>
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full" :class="updatedAuxiliary.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                      {{ updatedAuxiliary.isActive ? 'Activo' : 'Inactivo' }}
                    </span>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Fecha de actualización:</span>
                    <p class="text-gray-800 font-semibold">{{ formatDate(updatedAuxiliary.fecha_actualizacion) }}</p>
                  </div>
                </div>
                <div v-if="updatedAuxiliary.observaciones">
                  <span class="text-gray-500 font-medium block mb-2">Observaciones:</span>
                  <p class="text-gray-800 bg-gray-50 p-3 rounded-lg">{{ updatedAuxiliary.observaciones }}</p>
                </div>
              </div>
            </div>
          </template>
        </Notification>
      </div>

      <ValidationAlert :visible="validationState.showValidationError && validationState.hasAttemptedSubmit" :errors="validationErrors" />
    </form>
  </div>
  <div v-else class="text-center py-8">
    <p class="text-gray-500">No se pudieron cargar los datos del auxiliar para edición.</p>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, watch, ref, nextTick } from 'vue'
import { FormInputField, FormCheckbox, FormTextarea } from '@/shared/components/ui/forms'
import { SaveButton, ClearButton } from '@/shared/components/ui/buttons'
import { Notification, ValidationAlert } from '@/shared/components/ui/feedback'
import { useAuxiliaryEdition } from '../../composables/useAuxiliaryEdition'
import type { AuxiliaryEditFormModel } from '../../types/auxiliary.types'
import { RefreshIcon } from '@/assets/icons'

type UsuarioAux = {
  id: string
  tipo: string
  nombre?: string
  codigo?: string
  email?: string
  activo?: boolean
  auxiliarName?: string
  auxiliarCode?: string
  AuxiliarEmail?: string
  name?: string
  code?: string
  auxiliar_email?: string
  auxiliar_emailAddress?: string
  auxiliarEmail?: string
  auxiliar_code?: string
  auxiliar_name?: string
  observations?: string
  observaciones?: string
  is_active?: boolean
  isActive?: boolean
}

const props = defineProps<{ usuario: UsuarioAux }>()
const emit = defineEmits<{ (e: 'usuario-actualizado', payload: any): void }>()

const notificationContainer = ref<HTMLElement | null>(null)
const updatedAuxiliary = ref<any | null>(null)
const notification = reactive({
  visible: false,
  type: 'success' as 'success' | 'error' | 'warning' | 'info',
  title: '',
  message: ''
})

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

const { state, canSubmit, validateForm, update, setInitialData, resetToOriginal, clearMessages, createHasChanges } = useAuxiliaryEdition()
const isLoading = computed(() => state.isLoading)

const localModel = reactive<AuxiliaryEditFormModel>({
  id: '', auxiliarName: '', auxiliarCode: '', AuxiliarEmail: '', observaciones: '', isActive: true, password: '', passwordConfirm: ''
})

const formErrors = reactive({ auxiliarName: '', auxiliarCode: '', AuxiliarEmail: '', observaciones: '', password: '', passwordConfirm: '' })

const hasChanges = computed(() => createHasChanges(localModel))

const canSubmitButton = computed(() => {
  const passwordOnlyValid = !!localModel.password && localModel.password.trim().length >= 6
  const baseValid = canSubmit.value &&
    localModel.auxiliarName?.trim().length >= 2 &&
    localModel.auxiliarCode?.trim().length >= 3 &&
    !!localModel.AuxiliarEmail?.trim()
  return baseValid || passwordOnlyValid
})

const validationState = reactive({ showValidationError: false, hasAttemptedSubmit: false })

const validationErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return [] as string[]
  const errs: string[] = []
  if (!localModel.auxiliarName?.trim() || formErrors.auxiliarName) errs.push('Nombre completo válido requerido')
  if (!localModel.auxiliarCode?.trim() || formErrors.auxiliarCode) errs.push('Código de auxiliar válido requerido')
  if (!localModel.AuxiliarEmail?.trim() || formErrors.AuxiliarEmail) errs.push('Email válido requerido')
  if (formErrors.password) errs.push(formErrors.password)
  if (formErrors.passwordConfirm) errs.push(formErrors.passwordConfirm)
  if (formErrors.observaciones) errs.push('Observaciones válidas requeridas')
  return errs
})

const normalizeAuxUser = (u: UsuarioAux | undefined | null): AuxiliaryEditFormModel | null => {
  if (!u) return null
  const auxiliarName = u.auxiliarName || (u as any).auxiliar_name || u.nombre || u.name || ''
  const auxiliarCode = u.auxiliarCode || (u as any).auxiliar_code || u.codigo || u.code || ''
  const auxiliarEmail = u.AuxiliarEmail || (u as any).auxiliarEmail || (u as any).auxiliar_email || (u as any).auxiliar_emailAddress || u.email || ''
  const observaciones = u.observaciones || (u as any).observations || ''
  const isActive = (u as any).isActive !== undefined ? (u as any).isActive :
    (u as any).is_active !== undefined ? (u as any).is_active :
    (u as any).activo !== undefined ? (u as any).activo : true

  return {
    id: u.id,
    auxiliarName: (auxiliarName || '').toString(),
    auxiliarCode: (auxiliarCode || '').toString(),
    AuxiliarEmail: (auxiliarEmail || '').toString(),
    observaciones: (observaciones || '').toString(),
    isActive: !!isActive,
    password: '',
    passwordConfirm: ''
  }
}

watch(() => props.usuario, (u) => {
  const mapped = normalizeAuxUser(u)
  if (!mapped) return
  Object.assign(localModel, mapped)
  setInitialData(mapped)
}, { immediate: true, deep: true })

watch(() => localModel, () => { 
  if (validationState.hasAttemptedSubmit) clearMessages() 
}, { deep: true })

const onReset = () => {
  const original = resetToOriginal()
  if (original) {
    Object.assign(localModel, original)
    localModel.password = ''
    localModel.passwordConfirm = ''
    validationState.hasAttemptedSubmit = false
    validationState.showValidationError = false
    Object.assign(formErrors, { auxiliarName: '', auxiliarCode: '', AuxiliarEmail: '', observaciones: '', password: '', passwordConfirm: '' })
  }
}

const submit = async () => {
  validationState.hasAttemptedSubmit = true
  Object.assign(formErrors, { auxiliarName: '', auxiliarCode: '', AuxiliarEmail: '', observaciones: '', password: '', passwordConfirm: '' })

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

  const result = await update(localModel)
  if ((result as any).success && (result as any).data) {
    const data = (result as any).data
    updatedAuxiliary.value = {
      auxiliarName: data.auxiliar_name,
      auxiliarCode: data.auxiliar_code,
      AuxiliarEmail: data.auxiliar_email,
      observaciones: data.observations,
      isActive: data.is_active,
      fecha_actualizacion: data.updated_at
    }
    showNotification('success', '¡Auxiliar Actualizado Exitosamente!', '')
    await scrollToNotification()
    emit('usuario-actualizado', { 
      ...data, 
      nombre: data.auxiliar_name, 
      codigo: data.auxiliar_code, 
      tipo: 'auxiliar' 
    })
  } else {
    showNotification('error', 'Error al Actualizar Auxiliar', (result as any).error || 'No se pudo actualizar el auxiliar')
    await scrollToNotification()
  }
}

const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', {
      year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
    })
  } catch {
    return 'Fecha no disponible'
  }
}
</script>
