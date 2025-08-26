<template>
  <button
    type="button"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click="$emit('click')"
  >
    <!-- Loading spinner -->
    <svg
      v-if="loading"
      class="animate-spin -ml-1 mr-2 h-4 w-4"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    
    <!-- Add Icon -->
    <svg
      v-else
      class="w-4 h-4 mr-1"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
    </svg>
    
    {{ loading ? loadingText : text }}
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  text?: string
  loadingText?: string
  size?: 'xs' | 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'link'
}

const props = withDefaults(defineProps<Props>(), {
  text: 'Agregar',
  loadingText: 'Agregando...',
  size: 'sm',
  disabled: false,
  loading: false,
  variant: 'link'
})

defineEmits<{
  'click': []
}>()

const buttonClasses = computed(() => {
  const baseClasses = 'inline-flex items-center font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200'
  
  const sizeClasses = {
    xs: 'px-2 py-1 text-xs',
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  }
  
  const variantClasses = {
    primary: 'border border-transparent text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500 rounded-lg shadow-sm',
    secondary: 'border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 focus:ring-blue-500 rounded-lg shadow-sm',
    success: 'border border-transparent text-white bg-green-600 hover:bg-green-700 focus:ring-green-500 rounded-lg shadow-sm',
    warning: 'border border-transparent text-white bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500 rounded-lg shadow-sm',
    danger: 'border border-transparent text-white bg-red-600 hover:bg-red-700 focus:ring-red-500 rounded-lg shadow-sm',
    link: 'text-blue-600 hover:text-blue-800 focus:ring-blue-500 rounded'
  }
  
  return `${baseClasses} ${sizeClasses[props.size]} ${variantClasses[props.variant]}`
})
</script>
