<template>
  <button
    type="button"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click.prevent="generatePdf"
  >
    <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
    </svg>
    <PrintIcon v-else class="w-4 h-4 mr-2 text-gray-600" />
    {{ loading ? loadingText : text }}
  </button>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { PrintIcon } from '@/assets/icons'
import { useToasts } from '@/shared/composables/useToasts'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface Props {
  text?: string
  loadingText?: string
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  variant?: 'primary' | 'secondary' | 'ghost'
  caseCode?: string
  caseData?: any
}

const props = withDefaults(defineProps<Props>(), {
  text: 'Imprimir PDF',
  loadingText: 'Generando PDF...'
})

const emit = defineEmits<{
  (e: 'pdf-generated', pdfBlob: Blob): void
  (e: 'error', error: string): void
}>()

const { success, error: showError } = useToasts()
const internalLoading = ref(false)

const loading = computed(() => props.loading || internalLoading.value)

const buttonClasses = computed(() => {
  const base = 'inline-flex items-center px-4 py-2 border text-sm font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'
  const size = { sm: 'px-3 py-1.5 text-xs', md: 'px-4 py-2 text-sm', lg: 'px-6 py-3 text-base' }[props.size || 'md']
  const variant = {
    primary: 'border-transparent text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'border-gray-300 text-gray-600 bg-white hover:bg-gray-50 focus:ring-gray-500',
    ghost: 'border-transparent text-gray-600 bg-transparent hover:bg-gray-50 focus:ring-gray-500'
  }[props.variant || 'secondary']
  return `${base} ${size} ${variant}`
})

async function generatePdf() {
  if (!props.caseCode) {
    showError('generic', 'Error', 'Código de caso no proporcionado')
    emit('error', 'Código de caso no proporcionado')
    return
  }

  internalLoading.value = true

  try {
    const url = `${API_BASE_URL}/api/v1/cases/${encodeURIComponent(props.caseCode)}/pdf`
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`)
    }

    const pdfBlob = await response.blob()
    
    if (pdfBlob.type !== 'application/pdf') {
      throw new Error('El servidor no devolvió un archivo PDF válido')
    }

    const pdfUrl = URL.createObjectURL(pdfBlob)
    const features = 'noopener,noreferrer,width=1000,height=800'
    window.open(pdfUrl, '_blank', features)

    success('generic', 'PDF Generado', `PDF del caso ${props.caseCode} generado exitosamente`)
    emit('pdf-generated', pdfBlob)

    setTimeout(() => URL.revokeObjectURL(pdfUrl), 1000)

  } catch (error: any) {
    console.error('Error generando PDF:', error)
    const errorMessage = error.message || 'Error desconocido al generar el PDF'
    showError('generic', 'Error al generar PDF', errorMessage)
    emit('error', errorMessage)
  } finally {
    internalLoading.value = false
  }
}
</script>
