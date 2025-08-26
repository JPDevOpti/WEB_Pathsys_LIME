<template>
  <div class="space-y-1">
    <label v-if="label" class="block text-sm font-medium text-gray-700">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    
    <div class="relative">
      <select
        :value="modelValue"
        @change="handleChange"
        :disabled="disabled"
        :class="selectClasses"
      >
        <option value="" disabled>{{ placeholder }}</option>
        <option 
          v-for="option in options" 
          :key="option.value" 
          :value="option.value"
        >
          {{ option.label }}
        </option>
      </select>
      
      <!-- Custom dropdown arrow -->
      <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
        <svg 
          :class="[
            'h-5 w-5 transition-colors',
            disabled ? 'text-gray-300' : 'text-gray-400'
          ]"
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
    
    <!-- Mensaje de error -->
    <div v-if="error" class="mt-1">
      <p class="text-sm text-red-600">{{ error }}</p>
    </div>
    
    <!-- Texto de ayuda -->
    <p v-if="helpText" class="text-xs text-gray-500">
      {{ helpText }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Option {
  value: string | number
  label: string
}

interface Props {
  modelValue: string | number
  label?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  options: Option[]
  error?: string
  helpText?: string
  hasAttemptedSubmit?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  required: false,
  disabled: false,
  placeholder: 'Seleccione una opción',
  hasAttemptedSubmit: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  emit('update:modelValue', target.value)
}

const selectClasses = computed(() => {
  const baseClasses = "w-full px-3 py-2 pr-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-colors bg-white appearance-none cursor-pointer"
  
  if (props.disabled) {
    return `${baseClasses} border-gray-300 bg-gray-50 text-gray-500 cursor-not-allowed`
  }
  
  if (props.error) {
    return `${baseClasses} border-red-500 focus:ring-red-400 focus:border-red-400`
  }
  
  if (props.modelValue && !props.error) {
    return `${baseClasses} border-green-500`
  }
  
  return `${baseClasses} border-gray-300 hover:border-gray-400`
})
</script>

<style scoped>
/* Custom select styles */
select {
  background-image: none;
}

select:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Custom option styles */
select option {
  padding: 8px 12px;
  background-color: white;
  color: #374151;
}

select option:hover {
  background-color: #f3f4f6;
}

select option:checked {
  background-color: #3b82f6;
  color: white;
}

/* Disabled state */
select:disabled {
  opacity: 0.6;
}

select:disabled + div svg {
  color: #9ca3af;
}
</style>
