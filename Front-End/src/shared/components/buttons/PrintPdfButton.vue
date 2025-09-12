<template>
  <button
    type="button"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click.prevent="goToPreview"
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
import { computed } from 'vue'
import { PrintIcon } from '@/assets/icons'
import { useRouter } from 'vue-router'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface Props {
  text?: string
  loadingText?: string
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  variant?: 'primary' | 'secondary' | 'ghost'
  caseCode?: string
}

const props = withDefaults(defineProps<Props>(), {
  text: 'Imprimir PDF',
  loadingText: 'Preparando...'
})

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

const router = useRouter()
function goToPreview() {
  if (!props.caseCode) return
  const url = `${API_BASE_URL}/api/v1/casos/caso-code/${encodeURIComponent(props.caseCode)}/pdf`
  const features = 'noopener,noreferrer,width=1000,height=800'
  window.open(url, '_blank', features)
}
</script>
