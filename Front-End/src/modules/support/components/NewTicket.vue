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

      <!-- Archivos adjuntos -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Archivos adjuntos
        </label>
        <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
          <div class="space-y-1 text-center">
            <button
              @click="($refs.fileInput as HTMLInputElement)?.click()"
              type="button"
              class="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-800"
            >
              <PaperclipIcon class="w-4 h-4 mr-2" />
              Seleccionar archivos
            </button>
            <input
              ref="fileInput"
              type="file"
              multiple
              accept="image/*,.pdf,.doc,.docx,.txt"
              @change="handleFileUpload"
              class="hidden"
            />
            <p class="text-xs text-gray-500">
              PNG, JPG, PDF, DOC hasta 10MB
            </p>
          </div>
        </div>
      </div>

      <!-- Lista de archivos adjuntos -->
      <div v-if="formData.attachments.length > 0" class="space-y-2">
        <h4 class="text-sm font-medium text-gray-700">Archivos seleccionados:</h4>
        <div class="space-y-1">
          <div
            v-for="attachment in formData.attachments"
            :key="attachment.id"
            class="flex items-center justify-between p-2 bg-gray-50 rounded border"
          >
            <div class="flex items-center">
              <PaperclipIcon class="w-4 h-4 text-gray-400 mr-2" />
              <span class="text-sm text-gray-700">{{ attachment.fileName }}</span>
              <span class="text-xs text-gray-500 ml-2">
                ({{ (attachment.fileSize / 1024).toFixed(1) }} KB)
              </span>
            </div>
            <button
              @click="removeAttachment(attachment.id)"
              class="text-red-600 hover:text-red-800"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
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
import type { NewTicketForm, TicketAttachment } from '../types/support.types'

// Emits
const emit = defineEmits<{
  ticketCreated: [ticket: any]
}>()

// Estado del formulario
const formData = reactive<NewTicketForm>({
  title: '',
  category: '',
  description: '',
  attachments: []
})

// Opciones de categoría para el FormSelect
const categoryOptions = [
  { value: 'bug', label: 'Error / Bug' },
  { value: 'feature', label: 'Nueva característica' },
  { value: 'question', label: 'Pregunta' },
  { value: 'technical', label: 'Problema técnico' },
  { value: 'NN', label: 'Sin especificación' }
]

// Referencia para el input de archivos
const fileInput = ref<HTMLInputElement>()

// Computed para validación del formulario
const isFormValid = computed(() => {
  return formData.title.trim() !== '' && 
         formData.category !== '' && 
         formData.description.trim() !== ''
})

// Función para manejar la carga de archivos
const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  
  if (files) {
    Array.from(files).forEach(file => {
      // Validar tamaño (máximo 10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert(`El archivo ${file.name} es demasiado grande. Máximo 10MB.`)
        return
      }

      const attachment: TicketAttachment = {
        id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
        fileName: file.name,
        fileType: file.type,
        fileSize: file.size
      }

      // Si es una imagen, crear preview
      if (file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          attachment.previewUrl = e.target?.result as string
        }
        reader.readAsDataURL(file)
      }

      formData.attachments.push(attachment)
    })
    
    // Limpiar el input
    target.value = ''
  }
}

// Función para remover un archivo adjunto
const removeAttachment = (attachmentId: string) => {
  const index = formData.attachments.findIndex(att => att.id === attachmentId)
  if (index > -1) {
    formData.attachments.splice(index, 1)
  }
}

// Función para limpiar el formulario
const clearForm = () => {
  formData.title = ''
  formData.category = ''
  formData.description = ''
  formData.attachments = []
}

// Función para enviar el ticket
const submitTicket = () => {
  if (!isFormValid.value) {
    return
  }

  // Crear el ticket (simulado)
  const newTicket = {
    id: Date.now().toString(),
    title: formData.title,
    category: formData.category,
    description: formData.description,
    status: 'open' as const,
    createdAt: new Date().toISOString(),
    attachments: [...formData.attachments],
    comments: []
  }

  // Emitir evento
  emit('ticketCreated', newTicket)

  // Limpiar formulario
  clearForm()

  // Mostrar mensaje de éxito
  alert('¡Ticket creado exitosamente!')
}
</script>
