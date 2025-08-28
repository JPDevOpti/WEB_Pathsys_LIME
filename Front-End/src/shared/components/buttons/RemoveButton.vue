<template>
  <button
    type="button"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click="$emit('click')"
    :title="title"
  >
    <!-- Loading spinner -->
    <svg
      v-if="loading"
      class="animate-spin h-4 w-4"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    
    <!-- Remove/Delete Icon -->
    <svg
      v-else
      class="w-4 h-4"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  disabled?: boolean
  loading?: boolean
  size?: 'xs' | 'sm' | 'md' | 'lg'
  variant?: 'danger' | 'danger-ghost' | 'warning'
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  loading: false,
  size: 'md',
  variant: 'danger',
  title: 'Eliminar'
})

defineEmits<{
  'click': []
}>()

const buttonClasses = computed(() => {
  const baseClasses = 'inline-flex items-center justify-center rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200'
  
  const sizeClasses = {
    xs: 'p-1',
    sm: 'p-1.5',
    md: 'p-2',
    lg: 'p-3'
  }
  
  const variantClasses = {
    danger: 'text-red-600 hover:text-red-800 hover:bg-red-50 focus:ring-red-500',
    'danger-ghost': 'text-red-500 hover:text-red-700 hover:bg-red-50 focus:ring-red-500',
    warning: 'text-yellow-600 hover:text-yellow-800 hover:bg-yellow-50 focus:ring-yellow-500'
  }
  
  return `${baseClasses} ${sizeClasses[props.size]} ${variantClasses[props.variant]}`
})
</script>
