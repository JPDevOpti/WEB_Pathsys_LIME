<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'flex items-center justify-center w-full px-4 py-3 text-base font-extrabold text-white transition-all duration-300 rounded-xl shadow-lg focus:ring-4 disabled:opacity-70 disabled:cursor-not-allowed gap-2',
      variant === 'primary' ? 'bg-gradient-to-tr from-brand-500 to-brand-700 hover:scale-105 hover:shadow-2xl focus:ring-brand-200/40' : '',
      variant === 'secondary' ? 'bg-gradient-to-tr from-gray-500 to-gray-700 hover:scale-105 hover:shadow-2xl focus:ring-gray-200/40' : '',
      variant === 'danger' ? 'bg-gradient-to-tr from-error-500 to-error-700 hover:scale-105 hover:shadow-2xl focus:ring-error-200/40' : '',
      size === 'sm' ? 'px-3 py-2 text-sm' : '',
      size === 'lg' ? 'px-6 py-4 text-lg' : ''
    ]"
  >
    <!-- Icono de carga -->
    <svg v-if="loading" class="w-5 h-5 animate-spin" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    
    <!-- Icono personalizado -->
    <component v-else-if="icon" :is="icon" class="w-5 h-5" />
    
    <!-- Texto del botón -->
    <span>{{ loading ? loadingText : text }}</span>
  </button>
</template>

<script setup lang="ts">
interface Props {
  text: string
  loadingText?: string
  type?: 'button' | 'submit' | 'reset'
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
  icon?: any
}

const props = withDefaults(defineProps<Props>(), {
  type: 'button',
  variant: 'primary',
  size: 'md',
  loading: false,
  disabled: false,
  loadingText: 'Cargando...'
})
</script> 