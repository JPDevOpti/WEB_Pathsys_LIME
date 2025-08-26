<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <!-- Personal Information Section -->
    <div>
      <h4 class="text-lg font-medium text-gray-900 mb-4">Información Personal</h4>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- First Name -->
        <div>
          <label for="firstName" class="block text-sm font-medium text-gray-700 mb-1">
            Nombre *
          </label>
          <input
            id="firstName"
            v-model="formData.firstName"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            :class="{ 'border-red-300 focus:ring-red-500 focus:border-red-500': getFieldError('firstName') }"
            @blur="validateField('firstName')"
          />
          <p v-if="getFieldError('firstName')" class="mt-1 text-sm text-red-600">
            {{ getFieldError('firstName') }}
          </p>
        </div>

        <!-- Last Name -->
        <div>
          <label for="lastName" class="block text-sm font-medium text-gray-700 mb-1">
            Apellido *
          </label>
          <input
            id="lastName"
            v-model="formData.lastName"
            type="text"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            :class="{ 'border-red-300 focus:ring-red-500 focus:border-red-500': getFieldError('lastName') }"
            @blur="validateField('lastName')"
          />
          <p v-if="getFieldError('lastName')" class="mt-1 text-sm text-red-600">
            {{ getFieldError('lastName') }}
          </p>
        </div>

        <!-- Email -->
        <div class="md:col-span-2">
          <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
            Correo Electrónico *
          </label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            :class="{ 'border-red-300 focus:ring-red-500 focus:border-red-500': getFieldError('email') }"
            @blur="validateField('email')"
          />
          <p v-if="getFieldError('email')" class="mt-1 text-sm text-red-600">
            {{ getFieldError('email') }}
          </p>
        </div>

        <!-- Phone -->
        <div>
          <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">
            Teléfono
          </label>
          <input
            id="phone"
            v-model="formData.phone"
            type="tel"
            placeholder="+57 300 123 4567"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            :class="{ 'border-red-300 focus:ring-red-500 focus:border-red-500': getFieldError('phone') }"
            @blur="validateField('phone')"
          />
          <p v-if="getFieldError('phone')" class="mt-1 text-sm text-red-600">
            {{ getFieldError('phone') }}
          </p>
        </div>

        <!-- Document Type -->
        <div>
          <label for="documentType" class="block text-sm font-medium text-gray-700 mb-1">
            Tipo de Documento *
          </label>
          <select
            id="documentType"
            v-model="formData.documentType"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          >
            <option value="CC">Cédula de Ciudadanía</option>
            <option value="CE">Cédula de Extranjería</option>
            <option value="PP">Pasaporte</option>
          </select>
        </div>

        <!-- Document Number -->
        <div class="md:col-span-2">
          <label for="document" class="block text-sm font-medium text-gray-700 mb-1">
            Número de Documento *
          </label>
          <input
            id="document"
            v-model="formData.document"
            type="text"
            required
            placeholder="12345678"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            :class="{ 'border-red-300 focus:ring-red-500 focus:border-red-500': getFieldError('document') }"
            @blur="validateField('document')"
          />
          <p v-if="getFieldError('document')" class="mt-1 text-sm text-red-600">
            {{ getFieldError('document') }}
          </p>
        </div>
      </div>
    </div>

    <!-- Form Actions -->
    <div class="flex flex-col sm:flex-row gap-3 pt-6 border-t border-gray-200">
      <button
        type="submit"
        :disabled="isLoading || !hasChanges || hasErrors"
        class="flex-1 sm:flex-none sm:order-2 inline-flex items-center justify-center px-6 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        <span v-if="!isLoading">Guardar Cambios</span>
        <span v-else class="flex items-center gap-2">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Guardando...
        </span>
      </button>
      
      <button
        type="button"
        @click="$emit('cancel')"
        :disabled="isLoading"
        class="flex-1 sm:flex-none sm:order-1 inline-flex items-center justify-center px-6 py-2 bg-white text-gray-700 text-sm font-medium rounded-lg border border-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        Cancelar
      </button>
    </div>

    <!-- Unsaved Changes Warning -->
    <div v-if="hasChanges && !isLoading" class="flex items-center gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg">
      <ExclamationTriangleIcon class="w-5 h-5 text-amber-600 flex-shrink-0" />
      <p class="text-sm text-amber-800">
        Tienes cambios sin guardar. Asegúrate de guardar antes de cerrar.
      </p>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import type { UserProfile, ProfileFormData, ValidationError } from '../../types/userProfile.types'
import { MockProfileService } from '../../services/mockProfileService'

interface Props {
  user: UserProfile
  isLoading?: boolean
  errors?: ValidationError[]
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  errors: () => []
})

const emit = defineEmits<{
  submit: [data: ProfileFormData]
  cancel: []
  change: [hasChanges: boolean]
}>()

// Form data
const formData = reactive<ProfileFormData>({
  firstName: props.user.firstName,
  lastName: props.user.lastName,
  email: props.user.email,
  phone: props.user.phone || '',
  document: props.user.document,
  documentType: props.user.documentType
})

// Original data for comparison
const originalData = reactive<ProfileFormData>({
  firstName: props.user.firstName,
  lastName: props.user.lastName,
  email: props.user.email,
  phone: props.user.phone || '',
  document: props.user.document,
  documentType: props.user.documentType
})

// Local validation errors
const localErrors = ref<ValidationError[]>([])

// Computed properties
const hasChanges = computed(() => {
  return Object.keys(formData).some(key => {
    const formKey = key as keyof ProfileFormData
    return formData[formKey] !== originalData[formKey]
  })
})

const hasErrors = computed(() => {
  return localErrors.value.length > 0 || props.errors.length > 0
})

// Watch for changes and emit
watch(hasChanges, (newValue) => {
  emit('change', newValue)
}, { immediate: true })

// Methods
const getFieldError = (field: string): string | undefined => {
  const localError = localErrors.value.find(error => error.field === field)
  const propError = props.errors.find(error => error.field === field)
  return localError?.message || propError?.message
}

const validateField = (field: keyof ProfileFormData) => {
  // Remove existing error for this field
  localErrors.value = localErrors.value.filter(error => error.field !== field)
  
  const value = formData[field]
  let errorMessage = ''

  switch (field) {
    case 'firstName':
    case 'lastName':
      if (!value.trim()) {
        errorMessage = `${field === 'firstName' ? 'El nombre' : 'El apellido'} es requerido`
      }
      break
    
    case 'email':
      if (!value.trim()) {
        errorMessage = 'El email es requerido'
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        errorMessage = 'El email no tiene un formato válido'
      }
      break
    
    case 'phone':
      if (value && !/^\+?[\d\s-()]{10,}$/.test(value)) {
        errorMessage = 'El teléfono no tiene un formato válido'
      }
      break
    
    case 'document':
      if (!value.trim()) {
        errorMessage = 'El documento es requerido'
      } else if (!/^\d{8,12}$/.test(value)) {
        errorMessage = 'El documento debe tener entre 8 y 12 dígitos'
      }
      break
  }

  if (errorMessage) {
    localErrors.value.push({ field, message: errorMessage })
  }
}

const validateForm = (): boolean => {
  localErrors.value = []
  
  // Validate all fields
  Object.keys(formData).forEach(field => {
    validateField(field as keyof ProfileFormData)
  })
  
  return localErrors.value.length === 0
}

const handleSubmit = () => {
  if (validateForm() && hasChanges.value) {
    emit('submit', { ...formData })
  }
}
</script>