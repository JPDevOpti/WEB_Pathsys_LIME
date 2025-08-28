<!--
  Componente BaseButton reutilizable
  Basado en los estilos del frontend anterior
-->
<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click="handleClick"
  >
    <!-- Loading spinner -->
    <div v-if="loading" class="flex items-center">
      <div class="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full mr-2"></div>
      {{ loadingText || 'Cargando...' }}
    </div>
    
    <!-- Normal content -->
    <div v-else class="flex items-center justify-center">
      <slot name="icon-left" />
      <span v-if="$slots.default">
        <slot />
      </span>
      <slot name="icon-right" />
    </div>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'button' | 'submit' | 'reset'
  variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'ghost' | 'outline'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  disabled?: boolean
  loading?: boolean
  loadingText?: string
  fullWidth?: boolean
  customClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'button',
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  loadingText: '',
  fullWidth: false,
  customClass: ''
})

const emit = defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()

const buttonClasses = computed(() => {
  const baseClasses = [
    'inline-flex items-center justify-center font-medium rounded-lg',
    'transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2',
    'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none'
  ]
  
  // Size classes
  const sizeClasses = {
    xs: 'px-2.5 py-1.5 text-xs',
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-5 py-3 text-base',
    xl: 'px-6 py-3.5 text-base'
  }
  
  baseClasses.push(sizeClasses[props.size])
  
  // Variant classes
  const variantClasses = {
    primary: [
      'bg-blue-600 text-white shadow-sm hover:bg-blue-700',
      'focus:ring-blue-500 active:bg-blue-800'
    ],
    secondary: [
      'bg-gray-600 text-white shadow-sm hover:bg-gray-700',
      'focus:ring-gray-500 active:bg-gray-800'
    ],
    success: [
      'bg-green-600 text-white shadow-sm hover:bg-green-700',
      'focus:ring-green-500 active:bg-green-800'
    ],
    danger: [
      'bg-red-600 text-white shadow-sm hover:bg-red-700',
      'focus:ring-red-500 active:bg-red-800'
    ],
    warning: [
      'bg-yellow-600 text-white shadow-sm hover:bg-yellow-700',
      'focus:ring-yellow-500 active:bg-yellow-800'
    ],
    ghost: [
      'bg-transparent text-gray-700 hover:bg-gray-100',
      'focus:ring-gray-300 active:bg-gray-200'
    ],
    outline: [
      'bg-transparent text-blue-600 border border-blue-600',
      'hover:bg-blue-50 focus:ring-blue-500 active:bg-blue-100'
    ]
  }
  
  baseClasses.push(...variantClasses[props.variant])
  
  // Full width
  if (props.fullWidth) {
    baseClasses.push('w-full')
  }
  
  // Custom classes
  if (props.customClass) {
    baseClasses.push(props.customClass)
  }
  
  return baseClasses.join(' ')
})

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>
