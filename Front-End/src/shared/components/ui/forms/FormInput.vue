<template>
  <div class="relative group">
    <label
      v-if="label"
      :for="id"
      class="mb-1.5 block text-sm font-semibold text-gray-700"
    >
      {{ label }}<span v-if="required" class="text-error-500">*</span>
    </label>
    <div class="relative">
      <!-- Icono izquierdo -->
      <span 
        v-if="leftIcon"
        class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-brand-500 transition-colors duration-300"
      >
        <component :is="leftIcon" />
      </span>
      
      <!-- Input principal -->
      <input
        :id="id"
        :type="type"
        :value="modelValue"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        :class="[
          'h-12 w-full rounded-lg border bg-white py-2.5 text-base text-gray-800 shadow-theme-xs placeholder:text-gray-400 focus:border-brand-500 focus:ring-2 focus:ring-brand-200/40 transition-all duration-300 outline-none',
          leftIcon ? 'pl-10' : 'pl-3',
          rightIcon ? 'pr-10' : 'pr-3',
          error ? 'border-error-500 focus:border-error-500 focus:ring-error-200/40' : 'border-gray-300',
          success ? 'border-success-500 focus:border-success-500 focus:ring-success-200/40' : '',
          disabled ? 'opacity-50 cursor-not-allowed' : ''
        ]"
      />
      
      <!-- Icono derecho -->
      <span 
        v-if="rightIcon"
        class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-brand-500 transition-colors duration-300"
      >
        <component :is="rightIcon" />
      </span>
    </div>
    
    <!-- Mensaje de error -->
    <p v-if="error" class="mt-1 text-sm text-error-500">
      {{ error }}
    </p>
    
    <!-- Mensaje de ayuda -->
    <p v-else-if="helpText" class="mt-1 text-sm text-gray-500">
      {{ helpText }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: string
  id?: string
  type?: string
  label?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  error?: string
  success?: boolean
  helpText?: string
  leftIcon?: any
  rightIcon?: any
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  required: false,
  disabled: false,
  success: false
})

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script> 