<template>
  <div class="relative">
    <FormInputField
      :label="label"
      :placeholder="placeholder || 'Seleccione fecha'"
      :type="'date'"
      :required="required"
      :errors="errors"
      :warnings="warnings"
      :help-text="helpText"
      :min="minIso"
      :max="maxIso"
      v-model="innerValue"
      ref="container"
    />
    <button type="button" class="absolute right-2 bottom-2 p-1 text-blue-600 hover:text-blue-700" @click="openCalendar" aria-label="Abrir calendario">
      <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <path d="M7 11H17M7 15H13M16 3V7M8 3V7M7 21H17C18.1046 21 19 20.1046 19 19V8C19 6.89543 18.1046 6 17 6H7C5.89543 6 5 6.89543 5 8V19C5 20.1046 5.89543 21 7 21Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
  </div>
  
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
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

// min/max: aceptar DD/MM/AAAA y convertir a ISO
const minIso = computed(() => {
  if (!props.min) return ''
  if (isISODateFormat(props.min)) return props.min
  if (isDisplayDateFormat(props.min)) return convertDisplayToISO(props.min)
  return ''
})
const maxIso = computed(() => {
  if (!props.max) return ''
  if (isISODateFormat(props.max)) return props.max
  if (isDisplayDateFormat(props.max)) return convertDisplayToISO(props.max)
  return ''
})

const container = ref<any>(null)
function openCalendar() {
  const root: any = container.value?.$el ?? container.value
  const input = (root && typeof root.querySelector === 'function') ? (root.querySelector('input') as HTMLInputElement | null) : null
  if (!input) return
  if (typeof (input as any).showPicker === 'function') {
    try { (input as any).showPicker() } catch { input.focus() }
  } else {
    input.focus()
  }
}
</script>


