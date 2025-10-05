<template>
  <ComponentCard
    v-if="isPatologo"
    title="Firma Digital"
    description="Sube tu imagen de firma para usarla en reportes médicos y documentos oficiales"
  >
    <div
      class="border border-dashed border-gray-300 rounded-xl bg-gray-50 p-6 md:p-8 hover:border-blue-500 transition-colors"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop.prevent="(e) => { onDrop(e); const files = e.dataTransfer?.files; if (files && files.length > 0) handleFileWithErrorHandling(files[0]) }"
      :class="{ 'border-blue-500 bg-blue-50/50': isDragOver }"
    >
      <div v-if="previewUrl" class="flex flex-col items-center gap-4">
        <div class="relative">
          <div class="bg-white border-2 border-gray-200 rounded-lg p-4 shadow-md min-h-[120px] min-w-[200px] flex items-center justify-center overflow-hidden">
            <img 
              :src="previewUrl" 
              alt="Vista previa de la firma" 
              class="max-h-32 max-w-full object-contain transition-transform duration-200" 
              @error="handleImageError"
              @load="handleImageLoad"
            />
          </div>
          <div class="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full flex items-center justify-center shadow-sm">
            <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>
        
        <div class="text-center">
          <p class="text-sm font-medium text-gray-900 mb-2">Firma Digital Guardada</p>
          <p class="text-xs text-gray-500 mb-3">Tu firma está lista para usar en reportes médicos</p>

        </div>
        
        <div class="flex justify-center">
          <button 
            type="button" 
            class="px-4 py-2 text-sm rounded-lg border border-red-600 text-red-600 bg-white hover:bg-red-50 transition-colors disabled:opacity-50" 
            @click="removeWithErrorHandling"
            :disabled="isUploading"
          >
            Eliminar Firma
          </button>
        </div>
      </div>

      <div v-else class="text-center">
        <div class="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-blue-100 text-blue-600">
          <svg class="w-10 h-10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
          </svg>
        </div>
        <h4 class="mb-2 font-semibold text-gray-800">Subir Firma Digital</h4>
        <p class="mb-4 text-sm text-gray-600">Arrastra y suelta tu imagen de firma aquí o haz clic para seleccionar</p>
        <label class="inline-flex items-center justify-center px-6 py-3 text-sm font-medium text-white bg-blue-600 rounded-lg cursor-pointer hover:bg-blue-700 transition-colors shadow-sm">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          Seleccionar archivo
          <input ref="fileInput" type="file" class="hidden" accept="image/png,image/jpeg,image/svg+xml" @change="(e) => { onFileChange(e); const files = (e.target as HTMLInputElement).files; if (files && files.length > 0) handleFileWithErrorHandling(files[0]) }" />
        </label>
        <p class="mt-3 text-xs text-gray-500">Formatos aceptados: PNG, JPG, SVG. Tamaño máximo: 1MB</p>
      </div>
    </div>
  </ComponentCard>
  <!-- Si por algún motivo se intenta montar sin rol patólogo, no renderizamos nada -->
  <template v-else></template>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import ComponentCard from '@/shared/components/layout/ComponentCard.vue'
import { useSignatureManager } from '../../composables/useSignatureManager'

interface Props {
  currentUrl?: string
  userRole?: string // rol del usuario autenticado
  pathologistCode?: string // código del patólogo para las operaciones de API
}

const props = withDefaults(defineProps<Props>(), {
  currentUrl: '',
  userRole: '',
  pathologistCode: ''
})

const emit = defineEmits<{
  change: [payload: { file: File | null; previewUrl: string | null }]
}>()

const {
  isDragOver,
  isUploading,
  selectedFile,
  previewUrl,
  isPatologo,
  onDragOver,
  onDragLeave,
  onDrop,
  onFileChange,
  handleFile,
  remove,
  setCurrentUrl,
  handleImageError,
  handleImageLoad
} = useSignatureManager(props.userRole, props.pathologistCode)

// Initialize with current URL if exists
if (props.currentUrl && isPatologo.value) {
  setCurrentUrl(props.currentUrl)
}

watch(
  () => props.currentUrl,
  (val) => {
    // Si hay una URL válida y no hay archivo seleccionado, mostrar la firma existente
    if (val && !selectedFile.value && isPatologo.value) {
      setCurrentUrl(val)
    }
    // Si no hay URL y no hay archivo seleccionado, limpiar la vista previa
    else if ((!val || !isPatologo.value) && !selectedFile.value) {
      setCurrentUrl(null)
    }
  },
  { immediate: true }
)

const handleFileWithErrorHandling = async (file: File) => {
  try {
    await handleFile(file)
    emitChange()
  } catch (error) {
    console.error('Error al subir firma:', error)
    alert('Error al subir la firma. Inténtalo de nuevo.')
  }
}

const removeWithErrorHandling = async () => {
  try {
    await remove()
    emitChange()
  } catch (error) {
    console.error('Error al eliminar firma:', error)
    alert('Error al eliminar la firma. Inténtalo de nuevo.')
  }
}

const emitChange = () => {
  if (isPatologo.value) {
    emit('change', { file: selectedFile.value, previewUrl: previewUrl.value })
  }
}
</script>


