<template>
  <div class="method-selector">
    <!-- Label -->
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>

    <!-- Selector Container -->
    <div class="relative">
      <!-- Select field -->
      <div class="relative">
        <select
          ref="selectRef"
          v-model="selectedMethod"
          :disabled="disabled"
          :class="[
            'w-full px-3 py-2 pr-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-colors bg-white appearance-none',
            errorString ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300',
            disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : 'text-gray-900'
          ]"
          @change="handleMethodChange"
        >
          <option value="" disabled>{{ placeholder }}</option>
          <option v-for="method in methods" :key="method.value" :value="method.value">
            {{ method.label }}
          </option>
        </select>
        
        <!-- Dropdown arrow -->
        <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
          <svg 
            class="h-4 w-4 text-gray-400"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      <!-- Error message -->
      <p v-if="errorString" class="mt-1 text-sm text-red-600">{{ errorString }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'

// Props
interface Props {
  modelValue?: string
  label?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  errorMessage?: string
  // Opciones externas para permitir mostrar valores dinámicos
  options?: Array<{ value: string; label: string }>
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  label: '',
  placeholder: 'Seleccionar método...',
  required: false,
  disabled: false,
  errorMessage: '',
  options: undefined
})

// Emits
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'method-selected', method: { value: string; label: string } | null): void
}>()

// Local state
const selectRef = ref<HTMLSelectElement>()
const selectedMethod = ref(props.modelValue)

// Métodos predefinidos (lista actualizada)
const defaultMethods = [
  { value: 'hematoxilina-eosina', label: 'Hematoxilina-Eosina' },
  { value: 'inmunohistoquimica-polimero-peroxidasa', label: 'Inmunohistoquimica: Polímero-Peroxidasa' },
  { value: 'coloraciones-especiales', label: 'Coloraciones especiales' },
  { value: 'inmunofluorescencia-metodo-directo', label: 'Inmunoflurescencia: método directo' }
]

// Usar opciones externas si se proporcionan, sino la lista por defecto
const methods = computed(() => {
  return (props.options && props.options.length) ? props.options : defaultMethods
})

// Computed
const errorString = computed(() => {
  if (props.errorMessage) return props.errorMessage
  if (props.required && !selectedMethod.value) return 'El método es requerido'
  return ''
})

const handleMethodChange = () => {
  const selectedMethodObj = methods.value.find(m => m.value === selectedMethod.value)
  emit('update:modelValue', selectedMethod.value)
  emit('method-selected', selectedMethodObj || null)
}

onMounted(() => {
  if (props.modelValue !== selectedMethod.value) selectedMethod.value = props.modelValue
})

watch(() => props.modelValue, (nv) => {
  if (nv !== selectedMethod.value) selectedMethod.value = nv
})

// Si las opciones cambian y el valor actual ya no existe, mantenerlo visible si fue pasado como prop
watch(() => props.options, (opts) => {
  const optList = (opts && opts.length) ? opts : defaultMethods
  if (selectedMethod.value && !optList.find(m => m.value === selectedMethod.value)) {
    // Emitir selected con null para que el padre pueda reaccionar si lo desea
    emit('method-selected', null)
  }
})

// Expose focus method
defineExpose({
  focus: () => selectRef.value?.focus()
})
</script>
