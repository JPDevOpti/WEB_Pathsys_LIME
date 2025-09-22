<template>
  <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4">
    <div class="col-span-full">
      <h4 class="text-base font-semibold text-gray-800">Entity Form</h4>
    </div>

    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Entity Name" 
      placeholder="Example: North Clinic" 
      v-model="localModel.entityName"
      :error="formErrors.entityName"
    />
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Entity Code" 
      placeholder="Example: CLINIC001" 
      v-model="localModel.entityCode"
      :error="formErrors.entityCode"
      @blur="validateCode"
    />

    <FormTextarea 
      class="col-span-full" 
      label="Observations" 
      placeholder="Relevant notes or observations (optional)" 
      v-model="localModel.notes" 
      :rows="3"
      :error="formErrors.notes"
    />

    <div class="col-span-full md:col-span-6 flex items-center pt-3">
      <FormCheckbox label="Active" v-model="localModel.isActive" />
    </div>

    <div class="col-span-full flex flex-col sm:flex-row gap-2 sm:gap-3 sm:justify-end pt-4 border-t border-gray-200">
      <ClearButton type="button" @click="onClear" :disabled="isLoading" />
      <SaveButton 
        text="Save Entity" 
        type="submit" 
        :disabled="!canSubmit || isLoading"
        :loading="isLoading"
      />
    </div>

    <div ref="notificationContainer" class="col-span-full">
      <Notification
        :visible="notification.visible"
        :type="notification.type"
        :title="notification.title"
        :message="notification.message"
        :inline="true"
        :auto-close="false"
        @close="closeNotification"
      >
        <template v-if="notification.type === 'success' && createdEntity" #content>
          <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
            <div class="space-y-4">
              <div class="mb-4 pb-3 border-b border-gray-100">
                <h3 class="text-xl font-bold text-gray-900 mb-2">{{ createdEntity.name }}</h3>
                <p class="text-gray-600">
                  <span class="font-medium">Code:</span> 
                  <span class="font-mono font-bold text-gray-800 ml-1">{{ createdEntity.entity_code }}</span>
                </p>
              </div>
              
              <div class="space-y-4 text-sm">
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Status:</span>
                  <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                    :class="createdEntity.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                    {{ createdEntity.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Creation Date:</span>
                  <p class="text-gray-800 font-semibold">{{ formatDate(createdEntity.created_at) }}</p>
                </div>
              </div>
              
              <div v-if="createdEntity.notes">
                <span class="text-gray-500 font-medium block mb-2">Observations:</span>
                <p class="text-gray-800 bg-gray-50 p-3 rounded-lg">{{ createdEntity.notes }}</p>
              </div>
            </div>
          </div>
        </template>
      </Notification>
    </div>

    <ValidationAlert
      :visible="validationState.showValidationError && validationState.hasAttemptedSubmit"
      :errors="validationErrors"
    />
  </form>
</template>

<script setup lang="ts">
import { reactive, computed, watch, nextTick, ref } from 'vue'
import { FormInputField, FormCheckbox, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton } from '@/shared/components/buttons'
import { Notification, ValidationAlert } from '@/shared/components/feedback'
import { useEntityCreation } from '../../composables/useEntityCreation'
import type { EntityFormModel, EntityCreateResponse } from '../../types/entity.types'

// Props and emits
const modelValue = defineModel<EntityFormModel>({ required: true })
const emit = defineEmits<{ 
  (e: 'usuario-creado', payload: EntityFormModel): void 
}>()

// Refs and reactive state
const notificationContainer = ref<HTMLElement | null>(null)
const createdEntity = ref<EntityCreateResponse | null>(null)
const isLoading = ref(false)

const notification = reactive({
  visible: false,
  type: 'success' as 'success' | 'error' | 'warning' | 'info',
  title: '',
  message: ''
})

const validationState = reactive({
  showValidationError: false,
  hasAttemptedSubmit: false
})

// Composable for backend operations
const {
  state,
  codeValidationError,
  validateForm,
  checkCodeAvailability,
  createEntity,
  clearState,
  clearMessages
} = useEntityCreation()

// Local form model
const localModel = reactive<EntityFormModel>({ 
  ...modelValue.value
})

// Form validation errors
const formErrors = reactive({
  entityName: '',
  entityCode: '',
  notes: ''
})

// Computed properties
const validationErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  const validation = validateForm(localModel)
  return validation.isValid ? [] : Object.values(validation.errors)
})

const canSubmit = computed(() => true)

// Validation functions
const validateCode = async () => {
  formErrors.entityCode = ''
  
  if (!localModel.entityCode?.trim()) {
    formErrors.entityCode = 'Code is required'
    return
  }
  
  if (localModel.entityCode.length > 20) {
    formErrors.entityCode = 'Maximum 20 characters'
    return
  }
  
  if (!/^[A-Z0-9_-]+$/i.test(localModel.entityCode)) {
    formErrors.entityCode = 'Only letters, numbers, hyphens and underscores'
    return
  }
  
  await checkCodeAvailability(localModel.entityCode)
  if (codeValidationError.value) {
    formErrors.entityCode = codeValidationError.value
  }
}

// Helper functions
const clearFormErrors = () => {
  Object.keys(formErrors).forEach(key => {
    formErrors[key as keyof typeof formErrors] = ''
  })
}

const showNotification = (type: typeof notification.type, title: string, message: string) => {
  notification.type = type
  notification.title = title
  notification.message = message
  notification.visible = true
}

const clearNotification = () => {
  notification.visible = false
  notification.title = ''
  notification.message = ''
  createdEntity.value = null
}

const closeNotification = () => onClear()

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
    return 'Date not available'
  }
}

const scrollToNotification = async () => {
  await nextTick()
  if (notificationContainer.value) {
    notificationContainer.value.scrollIntoView({
      behavior: 'smooth',
      block: 'center'
    })
  }
}

// Form submission
const submit = async () => {
  validationState.hasAttemptedSubmit = true
  clearFormErrors()
  clearNotification()
  
  const validation = validateForm(localModel)
  if (!validation.isValid) {
    validationState.showValidationError = true
    return
  }
  
  validationState.showValidationError = false
  isLoading.value = true
  
  try {
    const result = await createEntity(localModel)
    
    if (result.success && result.data) {
      await handleEntityCreated(result.data)
    } else {
      const errorMessage = state.error || 'Unknown error creating entity'
      throw new Error(errorMessage)
    }
  } catch (error: any) {
    await handleEntityCreationError(error)
  } finally {
    isLoading.value = false
  }
}

// Success handler
const handleEntityCreated = async (createdEntityData: EntityCreateResponse) => {
  createdEntity.value = createdEntityData
  showNotification('success', 'Entity Registered Successfully!', '')
  emit('usuario-creado', { ...localModel })
  await scrollToNotification()
}

// Error handler with HTTP status code mapping
const handleEntityCreationError = async (error: any) => {
  console.error('Error saving entity:', error)
  
  let errorMessage = 'Could not save entity. Please try again.'
  let errorTitle = 'Error Saving Entity'
  
  if (error.message) {
    errorMessage = error.message
    if (error.message.includes('code')) {
      errorTitle = 'Duplicate Data'
    } else if (error.message.includes('valid') || error.message.includes('required')) {
      errorTitle = 'Invalid Data'
    } else if (error.message.includes('server')) {
      errorTitle = 'Server Error'
    }
  } else if (error.response?.data?.detail) {
    errorMessage = error.response.data.detail
  } else if (error.response?.status) {
    const errorMap: Record<number, { title: string; message: string }> = {
      409: { title: 'Duplicate Data', message: 'An entity with the provided data already exists' },
      422: { title: 'Invalid Data', message: 'The provided data is not valid' },
      400: { title: 'Incorrect Data', message: 'Incorrect or incomplete data' },
      500: { title: 'Server Error', message: 'Internal server error. Please try later' }
    }
    const errorInfo = errorMap[error.response.status] || { 
      title: `Server Error (${error.response.status})`, 
      message: 'An unexpected error occurred' 
    }
    errorTitle = errorInfo.title
    errorMessage = errorInfo.message
  }
  
  showNotification('error', errorTitle, errorMessage)
  await scrollToNotification()
}

// Form reset functions
const clearForm = () => {
  validationState.hasAttemptedSubmit = false
  validationState.showValidationError = false
  clearFormErrors()
  clearState()
  
  Object.assign(localModel, { 
    entityName: '', 
    entityCode: '', 
    notes: '', 
    isActive: true 
  })
}

const onClear = () => {
  clearForm()
  clearNotification()
}

// Watchers
watch(() => modelValue.value, (newValue) => {
  Object.assign(localModel, newValue)
}, { deep: true })

watch(() => localModel, () => {
  if (validationState.hasAttemptedSubmit && !notification.visible) {
    clearMessages()
    clearFormErrors()
  }
}, { deep: true })

watch(() => notification.visible, (newValue) => {
  if (newValue) scrollToNotification()
})
</script>


