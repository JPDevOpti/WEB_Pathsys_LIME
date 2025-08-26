<template>
  <FormInputField
    :label="label"
    :placeholder="placeholder || 'Seleccione fecha'"
    :type="'date'"
    :required="required"
    :errors="errors"
    :warnings="warnings"
    :help-text="helpText"
    :min="min"
    :max="max"
    v-model="innerValue"
  />
  
</template>

<script setup lang="ts">
import { computed } from 'vue'
import FormInputField from './FormInputField.vue'

interface Props {
  modelValue?: string
  label?: string
  placeholder?: string
  required?: boolean
  errors?: string[]
  warnings?: string[]
  helpText?: string
  min?: string
  max?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  label: '',
  placeholder: 'Seleccione fecha',
  required: false,
  errors: () => [],
  warnings: () => [],
  helpText: '',
  min: '',
  max: ''
})

const emit = defineEmits<{ (e: 'update:modelValue', value: string): void }>()

function isISODateFormat(value: string): boolean {
  return /^\d{4}-\d{2}-\d{2}$/.test(value)
}

function isDisplayDateFormat(value: string): boolean {
  return /^\d{2}\/\d{2}\/\d{4}$/.test(value)
}

function convertDisplayToISO(displayDate: string): string {
  if (!isDisplayDateFormat(displayDate)) return ''
  const [dd, mm, yyyy] = displayDate.split('/')
  return `${yyyy}-${mm}-${dd}`
}

function convertISOToDisplay(isoDate: string): string {
  if (!isISODateFormat(isoDate)) return ''
  const [yyyy, mm, dd] = isoDate.split('-')
  return `${dd}/${mm}/${yyyy}`
}

const innerValue = computed({
  get: () => {
    const value = props.modelValue || ''
    if (!value) return ''
    if (isISODateFormat(value)) return value
    if (isDisplayDateFormat(value)) return convertDisplayToISO(value)
    return ''
  },
  set: (val: string) => {
    if (!val) {
      emit('update:modelValue', '')
      return
    }
    if (isISODateFormat(val)) {
      emit('update:modelValue', convertISOToDisplay(val))
      return
    }
    // Si el navegador enviara un formato no esperado, preservamos el valor
    emit('update:modelValue', val)
  }
})
</script>


