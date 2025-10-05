<template>
  <button
    type="button"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click="$emit('click', $event)"
    :title="title"
  >
    <!-- Loading spinner -->
    <svg
      v-if="loading"
      class="animate-spin h-4 w-4 mr-2"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    
    <!-- Close Icon -->
    <svg
      v-else
      class="w-4 h-4 mr-2"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
    </svg>
    
    {{ loading ? loadingText : text }}
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  text?: string
  loadingText?: string
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  variant?: 'danger' | 'danger-outline' | 'ghost'
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  text: 'Cerrar',
  loadingText: 'Cerrando...',
  size: 'md',
  disabled: false,
  loading: false,
  variant: 'danger-outline',
  title: 'Cerrar'
})

defineEmits<{
  'click': [e: MouseEvent]
}>()

const buttonClasses = computed(() => {
  const baseClasses = 'inline-flex items-center font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200'
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-6 py-2 text-sm',
    lg: 'px-8 py-3 text-base'
  }
  
  const variantClasses = {
    danger: 'bg-red-600 text-white border border-transparent hover:bg-red-700 focus:ring-red-500 shadow-sm',
    'danger-outline': 'bg-white text-red-600 border border-red-600 hover:bg-red-50 focus:ring-red-500 shadow-sm',
    ghost: 'bg-transparent text-red-600 hover:bg-red-50 focus:ring-red-500'
  }
  
  return `${baseClasses} ${sizeClasses[props.size]} ${variantClasses[props.variant]}`
})
</script>
