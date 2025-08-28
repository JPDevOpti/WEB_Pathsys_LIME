<template>
  <div class="body-region-combobox">
    <!-- Label -->
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>

    <!-- Combobox Container -->
    <div class="relative">
      <!-- Input field -->
      <div class="relative">
<input
          ref="inputRef"
          :value="displayText"
          type="text"
          :placeholder="placeholder"
          :disabled="disabled"
          :class="[
            'w-full px-3 py-2 pr-10 border rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors',
            errorString ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300',
            disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : 'bg-white text-gray-900'
          ]"
          @focus="handleFocus"
          @blur="handleBlur"
          @keydown="handleKeyDown"
          @input="(e:any) => { searchQuery = e?.target?.value || '' }"
          autocomplete="off"
        />
        
        <div class="absolute inset-y-0 right-0 pr-3 flex items-center">
          <svg 
            class="h-4 w-4 text-gray-400 cursor-pointer transition-transform"
            :class="{ 'transform rotate-180': isOpen }"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
            @click="toggleDropdown"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      <!-- Dropdown options -->
      <div
        v-if="isOpen && !disabled"
        class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto"
      >
        <!-- No results -->
        <div v-if="filteredOptions.length === 0" class="px-3 py-2 text-sm text-gray-500 text-center">
          {{ searchQuery.trim() ? 'No se encontraron regiones' : 'No hay regiones disponibles' }}
        </div>
        
        <!-- Options -->
        <div
          v-for="(option, index) in filteredOptions"
          :key="option.value"
          :class="[
            'px-3 py-2 text-sm cursor-pointer transition-colors',
            index === highlightedIndex ? 'bg-blue-50 text-blue-900' : 'text-gray-900 hover:bg-gray-50',
            selectedRegion === option.value ? 'bg-blue-100 text-blue-900 font-medium' : ''
          ]"
          @click="selectOption(option)"
          @mouseenter="highlightedIndex = index"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-gray-400 text-xs">{{ option.category }}</span>
              <span class="font-medium">{{ option.label }}</span>
            </div>
            <svg 
              v-if="selectedRegion === option.value"
              class="h-4 w-4 text-blue-600"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Help text -->
    <p v-if="helpText" class="mt-1 text-xs text-gray-500">
      {{ helpText }}
    </p>

    <!-- Error message -->
    <p v-if="errorString" class="mt-1 text-sm text-red-600">
      {{ errorString }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick, onMounted } from 'vue'
import { useBodyRegionsAPI } from '@/modules/cases/composables/useBodyRegionsAPI'

// Props
interface Props {
  modelValue?: string
  label?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  helpText?: string
  errors?: string[]
  autoLoad?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  label: '',
  placeholder: 'Buscar región del cuerpo...',
  required: false,
  disabled: false,
  helpText: '',
  errors: () => [],
  autoLoad: true
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string]
  'region-selected': [region: BodyRegion | null]
}>()

// Tipos
interface BodyRegion {
  value: string
  label: string
  category: string
}

// Lista fija de regiones del cuerpo comunes en patología
const bodyRegions: BodyRegion[] = [
  // Cabeza y Cuello
  { value: 'cabeza', label: 'Cabeza', category: 'Cabeza y Cuello' },
  { value: 'cuello', label: 'Cuello', category: 'Cabeza y Cuello' },
  { value: 'cara', label: 'Cara', category: 'Cabeza y Cuello' },
  { value: 'cuero_cabelludo', label: 'Cuero Cabelludo', category: 'Cabeza y Cuello' },
  { value: 'oreja', label: 'Oreja', category: 'Cabeza y Cuello' },
  { value: 'nariz', label: 'Nariz', category: 'Cabeza y Cuello' },
  { value: 'boca', label: 'Boca', category: 'Cabeza y Cuello' },
  { value: 'lengua', label: 'Lengua', category: 'Cabeza y Cuello' },
  { value: 'garganta', label: 'Garganta', category: 'Cabeza y Cuello' },
  { value: 'tiroides', label: 'Tiroides', category: 'Cabeza y Cuello' },
  
  // Tórax
  { value: 'torax', label: 'Tórax', category: 'Tórax' },
  { value: 'mama_derecha', label: 'Mama Derecha', category: 'Tórax' },
  { value: 'mama_izquierda', label: 'Mama Izquierda', category: 'Tórax' },
  { value: 'pulmon_derecho', label: 'Pulmón Derecho', category: 'Tórax' },
  { value: 'pulmon_izquierdo', label: 'Pulmón Izquierdo', category: 'Tórax' },
  { value: 'corazon', label: 'Corazón', category: 'Tórax' },
  { value: 'mediastino', label: 'Mediastino', category: 'Tórax' },
  
  // Abdomen
  { value: 'abdomen', label: 'Abdomen', category: 'Abdomen' },
  { value: 'estomago', label: 'Estómago', category: 'Abdomen' },
  { value: 'intestino_delgado', label: 'Intestino Delgado', category: 'Abdomen' },
  { value: 'intestino_grueso', label: 'Intestino Grueso', category: 'Abdomen' },
  { value: 'colon', label: 'Colon', category: 'Abdomen' },
  { value: 'recto', label: 'Recto', category: 'Abdomen' },
  { value: 'higado', label: 'Hígado', category: 'Abdomen' },
  { value: 'vesicula_biliar', label: 'Vesícula Biliar', category: 'Abdomen' },
  { value: 'pancreas', label: 'Páncreas', category: 'Abdomen' },
  { value: 'bazo', label: 'Bazo', category: 'Abdomen' },
  { value: 'rinon_derecho', label: 'Riñón Derecho', category: 'Abdomen' },
  { value: 'rinon_izquierdo', label: 'Riñón Izquierdo', category: 'Abdomen' },
  { value: 'vejiga', label: 'Vejiga', category: 'Abdomen' },
  { value: 'utero', label: 'Útero', category: 'Abdomen' },
  { value: 'ovario_derecho', label: 'Ovario Derecho', category: 'Abdomen' },
  { value: 'ovario_izquierdo', label: 'Ovario Izquierdo', category: 'Abdomen' },
  { value: 'prostata', label: 'Próstata', category: 'Abdomen' },
  { value: 'testiculo_derecho', label: 'Testículo Derecho', category: 'Abdomen' },
  { value: 'testiculo_izquierdo', label: 'Testículo Izquierdo', category: 'Abdomen' },
  
  // Extremidades Superiores
  { value: 'brazo_derecho', label: 'Brazo Derecho', category: 'Extremidades Superiores' },
  { value: 'brazo_izquierdo', label: 'Brazo Izquierdo', category: 'Extremidades Superiores' },
  { value: 'antebrazo_derecho', label: 'Antebrazo Derecho', category: 'Extremidades Superiores' },
  { value: 'antebrazo_izquierdo', label: 'Antebrazo Izquierdo', category: 'Extremidades Superiores' },
  { value: 'mano_derecha', label: 'Mano Derecha', category: 'Extremidades Superiores' },
  { value: 'mano_izquierda', label: 'Mano Izquierda', category: 'Extremidades Superiores' },
  { value: 'dedo_derecho', label: 'Dedo', category: 'Extremidades Superiores' },
  { value: 'dedo_izquierdo', label: 'Dedo', category: 'Extremidades Superiores' },
  
  // Extremidades Inferiores
  { value: 'muslo_derecho', label: 'Muslo Derecho', category: 'Extremidades Inferiores' },
  { value: 'muslo_izquierdo', label: 'Muslo Izquierdo', category: 'Extremidades Inferiores' },
  { value: 'pierna_derecha', label: 'Pierna Derecha', category: 'Extremidades Inferiores' },
  { value: 'pierna_izquierda', label: 'Pierna Izquierda', category: 'Extremidades Inferiores' },
  { value: 'pie_derecho', label: 'Pie Derecho', category: 'Extremidades Inferiores' },
  { value: 'pie_izquierdo', label: 'Pie Izquierdo', category: 'Extremidades Inferiores' },
  { value: 'dedo_pie_derecho', label: 'Dedo del Pie', category: 'Extremidades Inferiores' },
  { value: 'dedo_pie_izquierdo', label: 'Dedo del Pie', category: 'Extremidades Inferiores' },
  
  // Piel
  { value: 'piel_cabeza', label: 'Piel de Cabeza', category: 'Piel' },
  { value: 'piel_torax', label: 'Piel de Tórax', category: 'Piel' },
  { value: 'piel_abdomen', label: 'Piel de Abdomen', category: 'Piel' },
  { value: 'piel_brazo', label: 'Piel de Brazo', category: 'Piel' },
  { value: 'piel_pierna', label: 'Piel de Pierna', category: 'Piel' },
  { value: 'piel_espalda', label: 'Piel de Espalda', category: 'Piel' },
  { value: 'piel_gluteo', label: 'Piel de Glúteo', category: 'Piel' },
  
  // Ganglios Linfáticos
  { value: 'ganglio_cervical', label: 'Ganglio Cervical', category: 'Ganglios Linfáticos' },
  { value: 'ganglio_axilar', label: 'Ganglio Axilar', category: 'Ganglios Linfáticos' },
  { value: 'ganglio_inguinal', label: 'Ganglio Inguinal', category: 'Ganglios Linfáticos' },
  { value: 'ganglio_mediastinico', label: 'Ganglio Mediastínico', category: 'Ganglios Linfáticos' },
  { value: 'ganglio_abdominal', label: 'Ganglio Abdominal', category: 'Ganglios Linfáticos' },
  
  // Otros
  { value: 'otro', label: 'Otro (Especificar)', category: 'Otros' },
  { value: 'no_especificado', label: 'No Especificado', category: 'Otros' }
]

// Refs
const inputRef = ref<HTMLInputElement>()
const searchQuery = ref('')
const isOpen = ref(false)
const highlightedIndex = ref(-1)
const isFocused = ref(false)

// Estado interno del componente seleccionado
const selectedRegion = ref(props.modelValue)

// Carga dinámica desde API con fallback
const { regions, isLoading, error, loadRegions } = useBodyRegionsAPI()

// Opciones disponibles (API o fallback local)
const availableOptions = computed<BodyRegion[]>(() => {
  if (regions.value && regions.value.length > 0) {
    return regions.value.map(r => ({
      value: r.value,
      label: r.label,
      category: r.category || ''
    }))
  }
  return bodyRegions
})

// Computed
const errorString = computed(() => {
  return Array.isArray(props.errors) ? props.errors.join(', ') : ''
})

// Filtrar opciones basado en la búsqueda
const filteredOptions = computed((): BodyRegion[] => {
  if (!searchQuery.value.trim()) {
    return availableOptions.value
  }
  
  const query = searchQuery.value.toLowerCase().trim()
  return availableOptions.value.filter(option => {
    const label = option.label.toLowerCase()
    const category = option.category.toLowerCase()
    const value = option.value.toLowerCase()
    
    return (
      label.includes(query) ||
      category.includes(query) ||
      value.includes(query)
    )
  })
})

// Obtener la región seleccionada actual
const currentSelectedRegion = computed((): BodyRegion | null => {
  if (!selectedRegion.value) return null
  
  const option = availableOptions.value.find(opt => opt.value === selectedRegion.value)
  return option || null
})

// Texto que se muestra en el input
const displayText = computed(() => {
  if (isFocused.value) {
    return searchQuery.value
  }
  
  if (selectedRegion.value && currentSelectedRegion.value) {
    return currentSelectedRegion.value.label
  }
  
  return searchQuery.value
})

// Funciones del combobox
const handleFocus = () => {
  isFocused.value = true
  searchQuery.value = ''
  isOpen.value = true
  highlightedIndex.value = -1
}

const handleBlur = () => {
  // Delay para permitir click en opciones
  setTimeout(() => {
    isFocused.value = false
    isOpen.value = false
    
    // Restaurar texto si no hay selección válida
    if (!selectedRegion.value) {
      searchQuery.value = ''
    }
    // Asegurar que el input muestre siempre el label de la selección
    if (selectedRegion.value) {
      nextTick(() => {
        searchQuery.value = displayText.value
      })
    }
  }, 150)
}

const toggleDropdown = () => {
  if (props.disabled) return
  
  if (isOpen.value) {
    inputRef.value?.blur()
  } else {
    inputRef.value?.focus()
  }
}

const selectOption = (option: BodyRegion) => {
  selectedRegion.value = option.value
  searchQuery.value = ''
  isOpen.value = false
  highlightedIndex.value = -1
  
  // Emit events
  emit('update:modelValue', option.value)
  emit('region-selected', option)
  
  // Quitar focus del input
  inputRef.value?.blur()
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (props.disabled) return
  
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      if (!isOpen.value) {
        isOpen.value = true
      }
      highlightedIndex.value = Math.min(highlightedIndex.value + 1, filteredOptions.value.length - 1)
      break
      
    case 'ArrowUp':
      event.preventDefault()
      if (isOpen.value) {
        highlightedIndex.value = Math.max(highlightedIndex.value - 1, -1)
      }
      break
      
    case 'Enter':
      event.preventDefault()
      if (isOpen.value && highlightedIndex.value >= 0 && filteredOptions.value[highlightedIndex.value]) {
        selectOption(filteredOptions.value[highlightedIndex.value])
      }
      break
      
    case 'Escape':
      event.preventDefault()
      isOpen.value = false
      highlightedIndex.value = -1
      inputRef.value?.blur()
      break
      
    case 'Tab':
      isOpen.value = false
      break
  }
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  selectedRegion.value = newValue || ''
}, { immediate: true })

watch(selectedRegion, (newValue) => {
  if (newValue !== props.modelValue) {
    emit('update:modelValue', newValue)
  }
})

// Watcher para la búsqueda - esto permite la búsqueda automática
watch(searchQuery, () => {
  if (isFocused.value && searchQuery.value.trim()) {
    isOpen.value = true
    highlightedIndex.value = -1
  }
})

// Sync display text
watch([displayText, isFocused], () => {
  if (!isFocused.value) {
    nextTick(() => {
      searchQuery.value = displayText.value
    })
  }
})

// Asegurar que el texto se refleje al montar y cuando cambie el modelo desde el padre
onMounted(() => {
  nextTick(() => {
    searchQuery.value = displayText.value
  })
  if (props.autoLoad && regions.value.length === 0) {
    loadRegions()
  }
})

watch(() => selectedRegion.value, () => {
  if (!isFocused.value) {
    nextTick(() => {
      searchQuery.value = displayText.value
    })
  }
}, { immediate: false })
</script>

<style scoped>
.body-region-combobox {
  position: relative;
}
</style> 