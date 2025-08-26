<template>
  <div v-if="localModel.patologoCode" class="space-y-6">
    <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4">
      <div class="col-span-full">
        <h4 class="text-base font-semibold text-gray-800">Editar Patólogo</h4>
        <p class="text-sm text-gray-500 mt-1">Modifica los datos del patólogo</p>
      </div>

      <!-- Código y Nombre -->
      <FormInputField class="md:col-span-6" label="Código del patólogo" :disabled="true" v-model="localModel.patologoCode" />
      <FormInputField class="md:col-span-6" label="Nombre completo" v-model="localModel.patologoName" />

      <!-- Iniciales y Email -->
      <FormInputField class="md:col-span-6" label="Iniciales" v-model="localModel.InicialesPatologo" maxlength="10" />
      <FormInputField class="md:col-span-6" label="Email" type="email" v-model="localModel.PatologoEmail" />

      <!-- Registro médico y Contraseña (lado a lado) -->
      <FormInputField class="md:col-span-6" label="Registro médico" v-model="localModel.registro_medico" />
      <FormInputField class="md:col-span-6" label="Nueva contraseña (opcional)"  placeholder="••••••••" type="password" :model-value="localModel.password || ''" @update:model-value="val => (localModel.password = val)" />

      <!-- Observaciones -->
      <FormTextarea class="col-span-full" label="Observaciones" v-model="localModel.observaciones" :rows="3" />

      <!-- Estado -->
      <div class="md:col-span-6 flex items-center pt-3">
        <FormCheckbox label="Activo" v-model="localModel.isActive" />
      </div>

      <!-- Botones -->
      <div class="col-span-full flex flex-col sm:flex-row gap-2 sm:gap-3 sm:justify-end pt-4 border-t border-gray-200">
        <ClearButton type="button" @click="onReset" :disabled="isLoading || !hasChanges" variant="secondary" :text="'Reiniciar'" :icon="'reset'">
          <template #icon>
            <RefreshIcon class="w-4 h-4 mr-2" />
          </template>
        </ClearButton>
        <SaveButton text="Actualizar Patólogo" type="submit" :disabled="!canSubmitButton || isLoading || !hasChanges" :loading="isLoading" />
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
          <template v-if="notification.type === 'success' && updatedPathologist" #content>
            <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div class="space-y-4">
                <div class="mb-4 pb-3 border-b border-gray-100">
                  <h3 class="text-xl font-bold text-gray-900 mb-2">{{ updatedPathologist.patologoName }}</h3>
                  <p class="text-gray-600">
                    <span class="font-medium">Código:</span>
                    <span class="font-mono font-bold text-gray-800 ml-1">{{ updatedPathologist.patologoCode }}</span>
                  </p>
                </div>
                <div class="space-y-3 text-sm">
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Iniciales:</span>
                    <p class="text-gray-800 font-semibold">{{ updatedPathologist.InicialesPatologo || '—' }}</p>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Email:</span>
                    <p class="text-gray-800 font-semibold">{{ updatedPathologist.PatologoEmail }}</p>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Registro médico:</span>
                    <p class="text-gray-800 font-semibold">{{ updatedPathologist.registro_medico }}</p>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Estado:</span>
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full" :class="updatedPathologist.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                      {{ updatedPathologist.isActive ? 'Activo' : 'Inactivo' }}
                    </span>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Fecha de actualización:</span>
                    <p class="text-gray-800 font-semibold">{{ formatDate(updatedPathologist.fecha_actualizacion) }}</p>
                  </div>
                </div>
                <div v-if="updatedPathologist.observaciones">
                  <span class="text-gray-500 font-medium block mb-2">Observaciones:</span>
                  <p class="text-gray-800 bg-gray-50 p-3 rounded-lg">{{ updatedPathologist.observaciones }}</p>
                </div>
              </div>
            </div>
          </template>
        </Notification>
      </div>

      <!-- Alerta de Validación -->
      <ValidationAlert :visible="validationState.showValidationError && validationState.hasAttemptedSubmit" :errors="validationErrors" />
    </form>
  </div>
  <div v-else class="text-center py-8">
    <p class="text-gray-500">No se pudieron cargar los datos del patólogo para edición.</p>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, watch, nextTick, ref } from 'vue'
import { FormInputField, FormCheckbox, FormTextarea } from '@/shared/components/ui/forms'
import { SaveButton, ClearButton } from '@/shared/components/ui/buttons'
import { Notification, ValidationAlert } from '@/shared/components/ui/feedback'
import { usePathologistEdition } from '../../composables/usePathologistEdition'
import type { PathologistEditFormModel } from '../../types/pathologist.types'
import { RefreshIcon } from '@/shared/icons'

const props = defineProps<{ usuario: any }>()

// Referencias
const notificationContainer = ref<HTMLElement | null>(null)

// Notificación y estado
const updatedPathologist = ref<any | null>(null)
const notification = reactive({
  visible: false,
  type: 'success' as 'success' | 'error' | 'warning' | 'info',
  title: '',
  message: ''
})
const validationState = reactive({ showValidationError: false, hasAttemptedSubmit: false })

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

// Formateo de fechas
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

const {
  isLoading,
  canSubmit,
  validateForm,
  update,
  setInitialData,
  resetToOriginal,
  createHasChanges
} = usePathologistEdition()

// Botón de submit: como en Residentes, permitir solo contraseña válida
const canSubmitButton = computed(() => {
  const passwordOnlyValid = !!localModel.password && localModel.password.trim().length >= 6
  const baseValid = canSubmit.value &&
    localModel.patologoName?.trim().length >= 2 &&
    localModel.InicialesPatologo?.trim().length >= 2 &&
    localModel.patologoCode?.trim().length >= 6 &&
    localModel.PatologoEmail?.trim().length > 0 &&
    localModel.registro_medico?.trim().length >= 5
  return baseValid || passwordOnlyValid
})

const localModel = reactive<PathologistEditFormModel>({
  id: '', patologoName: '', InicialesPatologo: '', patologoCode: '', PatologoEmail: '',
  registro_medico: '', observaciones: '', isActive: true
})

const hasChanges = computed(() => createHasChanges(localModel))

const validationErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return [] as string[]
  const errs: string[] = []
  if (!localModel.patologoName?.trim()) errs.push('Nombre completo válido requerido')
  if (!localModel.InicialesPatologo?.trim() || localModel.InicialesPatologo.trim().length < 2) errs.push('Iniciales válidas requeridas')
  if (!localModel.PatologoEmail?.trim()) errs.push('Email válido requerido')
  if (!localModel.registro_medico?.trim()) errs.push('Registro médico válido requerido')
  return errs
})

watch(() => props.usuario, (u) => {
  if (!u) return
  const mapped: PathologistEditFormModel = {
    id: u.id,
    patologoName: u.patologoName || u.nombre || '',
    InicialesPatologo: u.InicialesPatologo || '',
    patologoCode: u.patologoCode || u.codigo || '',
    PatologoEmail: u.PatologoEmail || u.email || '',
    registro_medico: u.registro_medico || '',
    observaciones: u.observaciones || '',
    isActive: u.isActive ?? u.activo ?? true
  }
  Object.assign(localModel, mapped)
  setInitialData(mapped)
}, { immediate: true, deep: true })

const onReset = () => {
  const original = resetToOriginal()
  if (original) Object.assign(localModel, original)
}

const submit = async () => {
  validationState.hasAttemptedSubmit = true
  const validation = validateForm(localModel)
  if (!validation.isValid) { validationState.showValidationError = true; return }
  validationState.showValidationError = false

  const result = await update(localModel)
  if ((result as any).success && (result as any).data) {
    updatedPathologist.value = (result as any).data
    showNotification('success', '¡Patólogo Actualizado Exitosamente!', '')
    await scrollToNotification()
  } else {
    showNotification('error', 'Error al Actualizar Patólogo', (result as any).error || 'No se pudo actualizar el patólogo')
    await scrollToNotification()
  }
}
</script>


