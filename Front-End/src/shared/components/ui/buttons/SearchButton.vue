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
      class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    
    <!-- Search Icon -->
    <SearchIcon
      v-else
      class="w-4 h-4 mr-2"
    />
    
    {{ loading ? loadingText : text }}
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SearchIcon from '@/assets/icons/SearchIcon.vue'

interface Props {
  text?: string
  loadingText?: string
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger'
}

const props = withDefaults(defineProps<Props>(), {
  text: 'Buscar',
  loadingText: 'Buscando...',
  size: 'md',
  disabled: false,
  loading: false,
  variant: 'primary'
})

defineEmits<{
  'click': []
}>()

const buttonClasses = computed(() => {
  const baseClasses = 'inline-flex items-center border text-sm font-medium rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200'
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm h-11',
    lg: 'px-6 py-3 text-base'
  }
  
  const variantClasses = {
    primary: 'border-transparent text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50 focus:ring-blue-500',
    success: 'border-transparent text-white bg-green-600 hover:bg-green-700 focus:ring-green-500',
    warning: 'border-transparent text-white bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500',
    danger: 'border-transparent text-white bg-red-600 hover:bg-red-700 focus:ring-red-500'
  }
  
  return `${baseClasses} ${sizeClasses[props.size]} ${variantClasses[props.variant]}`
})
</script>
