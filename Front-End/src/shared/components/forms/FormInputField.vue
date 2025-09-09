<template>
  <div :class="dense ? 'space-y-1' : 'space-y-1'">
    <label v-if="label" :class="['block font-medium text-gray-700', dense ? 'text-xs' : 'text-sm']">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    
    <div class="relative">
      <input
        :type="type"
        :value="modelValue"
        @input="handleInput"
        @blur="handleBlur"
        :placeholder="placeholder"
        :maxlength="maxLength"
        :disabled="disabled"
        :class="inputClasses"
        :style="errors.length > 0 ? 'border-color: #ef4444 !important;' : ''"
        :ref="inputRef"
        :autocomplete="autocomplete"
        :inputmode="inputmode"
      />
      
      <!-- Contador de caracteres -->
      <span
        v-if="showCounter"
        class="absolute inset-y-0 right-0 flex items-center justify-center pr-4 text-xs font-mono text-gray-500 pointer-events-none"
        :style="counterStyle"
      >
        {{ String(modelValue).length }}/{{ maxLength }}
      </span>
      
      <!-- Icono de loading -->
      <div v-if="isValidating" class="absolute inset-y-0 right-12 flex items-center pr-2">
        <svg class="animate-spin h-4 w-4 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
    </div>
    
    <!-- Mensajes de error -->
    <div v-if="errors.length > 0" class="space-y-1">
      <p v-for="error in errors" :key="error" class="text-sm text-red-600">
        {{ error }}
      </p>
    </div>
    
    <!-- Mensajes de advertencia -->
    <div v-if="warnings.length > 0" class="space-y-1">
      <p v-for="warning in warnings" :key="warning" class="text-sm text-yellow-600">
        {{ warning }}
      </p>
    </div>
    
    <!-- Texto de ayuda -->
    <p v-if="helpText" class="text-xs text-gray-500">
      {{ helpText }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: string | number
  label?: string
  type?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  maxLength?: number
  showCounter?: boolean
  counterStyle?: string
  errors?: string[]
  warnings?: string[]
  helpText?: string
  autocomplete?: string
  inputmode?: 'text' | 'numeric' | 'email' | 'tel' | 'url' | 'search' | 'none' | 'decimal'
  isValidating?: boolean
  inputRef?: string
  dense?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  required: false,
  disabled: false,
  showCounter: false,
  counterStyle: 'min-width: 38px;',
  errors: () => [],
  warnings: () => [],
  autocomplete: 'off',
  inputmode: 'text',
  isValidating: false,
  dense: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  'input': [value: string]
  'blur': [value: string]
}>()

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  const value = target.value
  emit('update:modelValue', value)
  emit('input', value)
}

const handleBlur = (event: Event) => {
  const target = event.target as HTMLInputElement
  const value = target.value
  emit('blur', value)
}

const inputClasses = computed(() => {
  const baseClasses = props.dense
    ? "w-full px-2 py-1.5 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-colors text-sm"
    : "w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-colors"
  
  if (props.errors.length > 0) {
    return `${baseClasses} !border-red-500 !focus:border-red-500 !focus:ring-red-200`
  }
  
  if (props.warnings.length > 0) {
    return `${baseClasses} border-yellow-500`
  }
  
  if (props.modelValue && props.errors.length === 0) {
    return `${baseClasses} border-green-500`
  }
  
  return `${baseClasses} border-gray-300`
})
</script>
