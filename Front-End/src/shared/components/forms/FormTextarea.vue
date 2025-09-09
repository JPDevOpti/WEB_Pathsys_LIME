<template>
  <div :class="[wrapperClasses, wrapperClass]">
    <label v-if="label" class="block text-sm font-medium text-gray-700">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    
    <textarea
      v-bind="textareaAttrs"
      :value="modelValue"
      @input="handleInput"
      :placeholder="computedPlaceholder"
      :rows="rows"
      :maxlength="maxLength"
      :disabled="disabled"
      :class="computedTextareaClasses"
    ></textarea>
    
    <!-- Contador de caracteres -->
    <div v-if="showCounter && maxLength" class="flex justify-between">
      <p v-if="helpText" class="text-xs text-gray-500">{{ helpText }}</p>
      <p class="text-xs text-gray-500">
        {{ modelValue.length }}/{{ maxLength }} caracteres
      </p>
    </div>
    
    <!-- Solo texto de ayuda si no hay contador -->
    <p v-else-if="helpText" class="text-xs text-gray-500">
      {{ helpText }}
    </p>
    
    <!-- Mensaje de error -->
    <div v-if="error" class="mt-1">
      <p class="text-sm text-red-600">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, useAttrs } from 'vue'
defineOptions({ inheritAttrs: false })

interface Props {
  modelValue: string
  label?: string
  placeholder?: string
  previewText?: string
  required?: boolean
  disabled?: boolean
  rows?: number
  maxLength?: number
  showCounter?: boolean
  error?: string
  helpText?: string
  hasAttemptedSubmit?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  required: false,
  disabled: false,
  rows: 3,
  showCounter: true,
  hasAttemptedSubmit: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const attrs = useAttrs()

// Extraer la clase para aplicarla al contenedor y no al textarea
const wrapperClass = computed(() => (attrs.class as string) || '')

// Remover class/style de los attrs que van al textarea
const textareaAttrs = computed(() => {
  const { class: _class, style: _style, ...rest } = attrs as Record<string, unknown>
  return rest
})

const wrapperClasses = computed(() => {
  return props.label ? 'space-y-2 w-full' : 'h-full flex flex-col w-full'
})

const handleInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
}

// Placeholder computado que muestra el texto de previsualización cuando está vacío
const computedPlaceholder = computed(() => {
  // Si hay contenido, no mostrar placeholder
  if (props.modelValue && props.modelValue.trim() !== '') {
    return ''
  }
  
  // Si hay previewText, mostrarlo siempre cuando está vacío
  if (props.previewText) {
    return props.previewText
  }
  
  // Si no hay previewText, mostrar placeholder normal
  if (props.placeholder) {
    return props.placeholder
  }
  
  return ''
})

const textareaClasses = computed(() => {
  const baseClasses = "w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-colors resize-none"
  
  if (props.error) {
    return `${baseClasses} border-red-500`
  }
  
  if (props.modelValue && !props.error) {
    return `${baseClasses} border-green-500`
  }
  
  return `${baseClasses} border-gray-300`
})

const computedTextareaClasses = computed(() => {
  // Si no hay label (modo editor), expandir a toda la altura disponible
  if (!props.label) {
    return `${textareaClasses.value} h-full`
  }
  return textareaClasses.value
})
</script>
