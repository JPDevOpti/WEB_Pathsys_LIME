<template>
  <div class="bg-white shadow rounded-lg">
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex items-center">
        <PlusIcon class="w-5 h-5 mr-2 text-blue-600" />
        <h2 class="text-lg font-semibold text-gray-900">Nuevo Ticket</h2>
      </div>
      <p class="mt-1 text-sm text-gray-600">
        Crea un ticket de soporte para reportar problemas o solicitar ayuda
      </p>
    </div>

    <div class="p-6 space-y-4">
      <!-- Título -->
      <FormInputField
        v-model="formData.title"
        label="Título del ticket"
        placeholder="Describe brevemente el problema..."
        :required="true"
        :maxLength="100"
        :showCounter="true"
      />

      <!-- Categoría -->
      <FormSelect
        v-model="formData.category"
        label="Categoría"
        placeholder="Selecciona una categoría"
        :required="true"
        :options="categoryOptions"
      />

      <!-- Descripción -->
      <FormTextarea
        v-model="formData.description"
        label="Descripción"
        placeholder="Describe detalladamente el problema, pasos para reproducirlo, comportamiento esperado, etc..."
        :required="true"
        :rows="4"
        :maxLength="500"
        :showCounter="true"
      />

      <!-- Imagen adjunta (simplificado) -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Imagen adjunta (opcional)
        </label>
        <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
          <div class="space-y-1 text-center">
            <button
              @click="($refs.fileInput as HTMLInputElement)?.click()"
              type="button"
              class="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-800"
            >
              <PaperclipIcon class="w-4 h-4 mr-2" />
              Seleccionar imagen
            </button>
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              @change="handleImageUpload"
              class="hidden"
            />
            <p class="text-xs text-gray-500">
              PNG, JPG, GIF, WEBP hasta 5MB
            </p>
          </div>
        </div>
      </div>

      <!-- Imagen seleccionada -->
      <div v-if="formData.image || imagePreview" class="space-y-2">
        <h4 class="text-sm font-medium text-gray-700">Imagen seleccionada:</h4>
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded border">
          <div class="flex items-center">
            <img 
              v-if="imagePreview" 
              :src="imagePreview" 
              alt="Preview" 
              class="w-12 h-12 object-cover rounded mr-3"
            />
            <div>
              <span class="text-sm text-gray-700">{{ formData.image?.name || 'Imagen' }}</span>
              <span v-if="formData.image" class="text-xs text-gray-500 block">
                ({{ (formData.image.size / 1024).toFixed(1) }} KB)
              </span>
            </div>
          </div>
          <button
            @click="removeImage"
            class="text-red-600 hover:text-red-800"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Botones de acción -->
      <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        <ClearButton
          text="Limpiar"
          size="sm"
          @click="clearForm"
        />
        <SaveButton
          text="Crear Ticket"
          size="sm"
          :disabled="!isFormValid"
          @click="submitTicket"
        />
      </div>
      
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { PlusIcon, PaperclipIcon } from '@/assets/icons'
import { FormInputField, FormSelect, FormTextarea } from '@/shared/components/forms'
import { ClearButton, SaveButton } from '@/shared/components/buttons'
import { useToasts } from '@/shared/composables/useToasts'
import { ticketsService } from '@/shared/services/tickets.service'
import type { NewTicketForm, TicketCategoryEnum } from '../types/support.types'

// Emits
const emit = defineEmits<{
  ticketCreated: [ticket: any]
}>()

// Estado del formulario
const formData = reactive<NewTicketForm>({
  title: '',
  category: '' as TicketCategoryEnum,
  description: '',
  image: undefined
})

// Estado adicional para preview de imagen
const imagePreview = ref<string | null>(null)
const isSubmitting = ref(false)

// Toasts
const { success, error } = useToasts()
const showSuccess = (message: string) => { success('create', 'Ticket', message, 4000) }
const showError = (message: string) => { error('generic', 'Error', message, 5000) }

// Opciones de categoría para el FormSelect
const categoryOptions = [
  { value: 'bug', label: 'Error / Bug' },
  { value: 'feature', label: 'Nueva característica' },
  { value: 'question', label: 'Pregunta' },
  { value: 'technical', label: 'Problema técnico' }
]

// Referencia para el input de archivos
const fileInput = ref<HTMLInputElement>()

// Computed para validación del formulario
const isFormValid = computed(() => {
  return formData.title.trim() !== '' && 
         formData.category !== '' as TicketCategoryEnum && 
         formData.description.trim() !== '' &&
         !isSubmitting.value
})

// Función para manejar la carga de imagen
const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    // Validar imagen usando el servicio
    const validation = ticketsService.validateImage(file)
    if (!validation.valid) {
      showError(validation.error || 'Archivo inválido')
      target.value = ''
      return
    }

    formData.image = file
    
    // Crear preview
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
    
    // Limpiar el input
    target.value = ''
  }
}

// Función para remover imagen
const removeImage = () => {
  formData.image = undefined
  imagePreview.value = null
}

// Función para limpiar el formulario
const clearForm = () => {
  formData.title = ''
  formData.category = '' as TicketCategoryEnum
  formData.description = ''
  formData.image = undefined
  imagePreview.value = null
}

// Función para enviar el ticket
const submitTicket = async () => {
  if (!isFormValid.value || isSubmitting.value) {
    return
  }

  isSubmitting.value = true

  try {
    // Crear ticket usando el servicio API
    const newTicket = await ticketsService.createTicket(formData)

    // Emitir evento con el ticket creado
    emit('ticketCreated', newTicket)

    // Limpiar formulario
    clearForm()

    showSuccess('¡Ticket creado exitosamente!')

  } catch (error: any) {
    console.error('Error creando ticket:', error)
    const message = error?.response?.data?.detail || 'Error al crear el ticket'
    showError(message)
  } finally {
    isSubmitting.value = false
  }
}
</script>
