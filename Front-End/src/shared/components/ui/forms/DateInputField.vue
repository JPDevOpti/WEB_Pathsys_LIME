<template>
  <div class="relative">
    <FormInputField
      :label="label"
      :placeholder="placeholder || 'Seleccione fecha'"
      :type="'date'"
      :required="required"
      :errors="combinedErrors"
      :warnings="warnings"
      :help-text="helpText"
      :min="minIso"
      :max="maxIso"
      rightAdornmentWidth="1.5rem"
      v-model="innerValue"
      ref="container"
      class="date-input-field"
    />
    <button 
      type="button" 
      class="absolute right-2 top-0 h-full flex items-center p-1 text-blue-600 hover:text-blue-700 z-10" 
      @click="openCalendar" 
      aria-label="Abrir calendario"
      :style="buttonStyle"
    >
      <CalendarSearchIcon class="w-5 h-5" aria-hidden="true" />
    </button>
  </div>
  
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import FormInputField from './FormInputField.vue'
import CalendarSearchIcon from '@/assets/icons/CalendarSearchIcon.vue'

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
  minYear?: number
  notBefore?: string
  notAfter?: string
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
  max: '',
  minYear: undefined,
  notBefore: '',
  notAfter: ''
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

// Errores combinados: añade validación opcional por año mínimo
const combinedErrors = computed(() => {
  const list = Array.isArray(props.errors) ? [...props.errors] : []
  if (props.minYear && innerValue.value) {
    const iso = innerValue.value
    const year = /^\d{4}-\d{2}-\d{2}$/.test(iso) ? Number(iso.slice(0, 4)) : NaN
    if (!Number.isNaN(year) && year < (props.minYear as number)) {
      list.push(`La fecha no puede ser anterior al año ${props.minYear}`)
    }
  }
  // Comparaciones relativas (aceptan DD/MM/AAAA o ISO)
  const norm = (v: string): string => {
    if (!v) return ''
    if (/^\d{4}-\d{2}-\d{2}$/.test(v)) return v
    if (/^\d{2}\/\d{2}\/\d{4}$/.test(v)) {
      const [dd, mm, yyyy] = v.split('/')
      return `${yyyy}-${mm}-${dd}`
    }
    return ''
  }
  if (innerValue.value) {
    const current = innerValue.value
    const nb = norm(props.notBefore || '')
    const na = norm(props.notAfter || '')
    if (nb && current < nb) {
      const disp = convertISOToDisplay(nb)
      list.push(`La fecha debe ser mayor o igual a ${disp}`)
    }
    if (na && current > na) {
      const disp = convertISOToDisplay(na)
      list.push(`La fecha debe ser menor o igual a ${disp}`)
    }
  }
  return list
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

// Calculate button position to align with input field
const buttonStyle = computed(() => {
  // Ajustar alineación vertical del botón del calendario
  const labelHeight = props.label ? '1.5rem' : '0rem'
  const labelSpacing = props.label ? '0.25rem' : '0rem'
  const inputHeight = '2.5rem'
  const nudgePx = -2 // levantar 2px para alinear con adornos derechos

  const topOffset = `calc(${labelHeight} + ${labelSpacing} + ${nudgePx}px)`

  return { top: topOffset, height: inputHeight }
})

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


