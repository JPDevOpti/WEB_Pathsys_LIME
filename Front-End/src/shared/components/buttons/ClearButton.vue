<template>
  <button
    type="button"
    :disabled="disabled"
    :class="buttonClasses"
    @click="$emit('click')"
  >
    <!-- Icon: permite slot personalizado y fallback a íconos integrados -->
    <slot name="icon">
      <svg
        v-if="icon === 'reset'"
        class="w-4 h-4 mr-2"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <!-- Heroicons outline: arrow-path -->
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16.023 9.348h4.992v-4.992m-1.183 3.81A8.25 8.25 0 003.9 6.75m4.077-1.936H3.007v4.992m1.183-3.81a8.25 8.25 0 0115.932 1.06m-1.183 9.813a8.25 8.25 0 01-15.932-1.06" />
      </svg>
      <svg
        v-else-if="icon === 'cancel'"
        class="w-4 h-4 mr-2"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <!-- Simple X icon -->
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
      <svg
        v-else
        class="w-4 h-4 mr-2"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <!-- Default trash icon -->
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
      </svg>
    </slot>

    {{ text }}
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  text?: string
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  icon?: 'default' | 'reset' | 'cancel'
}

const props = withDefaults(defineProps<Props>(), {
  text: 'Limpiar',
  size: 'md',
  disabled: false,
  icon: 'default'
})

defineEmits<{
  'click': []
}>()

const buttonClasses = computed(() => {
  const baseClasses = 'inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200'
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  }
  
  return `${baseClasses} ${sizeClasses[props.size]}`
})
</script>
