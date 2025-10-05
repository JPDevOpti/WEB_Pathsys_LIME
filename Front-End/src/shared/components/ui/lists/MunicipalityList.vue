<template>
  <div class="municipality-combobox">
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
          v-model="searchQuery"
          type="text"
          :placeholder="placeholder"
          :disabled="disabled"
          :class="[
            'w-full px-3 py-2 pr-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-colors bg-white appearance-none',
            errorString ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : (selectedMunicipality ? 'border-green-500' : 'border-gray-300'),
            disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : 'text-gray-900'
          ]"
          @focus="handleFocus"
          @blur="handleBlur"
          @keydown="handleKeyDown"
          autocomplete="off"
        />
        
        <!-- Dropdown arrow -->
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
        class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto"
      >
        <!-- No results -->
        <div v-if="filteredOptions.length === 0" class="px-3 py-2 text-sm text-gray-500 text-center">
          {{ searchQuery.trim() ? 'No se encontraron municipios' : 'No hay municipios disponibles' }}
        </div>
        
        <!-- Options -->
        <div
          v-for="(option, index) in filteredOptions"
          :key="option.value"
          :class="[
            'px-3 py-2 text-sm cursor-pointer transition-colors',
            index === highlightedIndex ? 'bg-blue-50 text-blue-900' : 'text-gray-900 hover:bg-gray-100',
            selectedMunicipality === option.value ? 'bg-blue-100 text-blue-900 font-medium' : ''
          ]"
          @click="selectOption(option)"
          @mouseenter="highlightedIndex = index"
        >
          <div class="flex items-center justify-between">
            <div class="flex flex-col">
              <span class="font-medium">{{ option.label }}</span>
              <span class="text-xs text-gray-500">{{ option.municipality.codigo }}</span>
            </div>
            <svg 
              v-if="selectedMunicipality === option.value"
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
import { computed, ref, watch, nextTick } from 'vue'

// Types
interface MunicipalityInfo {
  codigo: string
  nombre: string
  subregion: string
}

interface SelectOption {
  value: string
  label: string
  municipality: MunicipalityInfo
}

// Props
interface Props {
  modelValue?: string
  label?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  helpText?: string
  errors?: string[]
  selectedName?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  label: '',
  placeholder: 'Buscar y seleccionar municipio...',
  required: false,
  disabled: false,
  helpText: '',
  errors: () => [],
  selectedName: ''
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string]
  'municipality-selected': [municipality: MunicipalityInfo | null]
  'municipality-code-change': [code: string]
  'municipality-name-change': [name: string]
  'subregion-change': [subregion: string]
}>()

// Refs
const inputRef = ref<HTMLInputElement>()
const searchQuery = ref('')
const isOpen = ref(false)
const highlightedIndex = ref(-1)
const isFocused = ref(false)

// Estado interno del componente seleccionado
const selectedMunicipality = ref(props.modelValue)

// Lista completa de municipios de Antioquia
const municipalities: MunicipalityInfo[] = [
  { codigo: '05001', nombre: 'MEDELLÍN', subregion: 'Valle de Aburrá' },
  { codigo: '05002', nombre: 'ABEJORRAL', subregion: 'Oriente' },
  { codigo: '05004', nombre: 'ABRIAQUÍ', subregion: 'Occidente' },
  { codigo: '05021', nombre: 'ALEJANDRÍA', subregion: 'Oriente' },
  { codigo: '05030', nombre: 'AMAGÁ', subregion: 'Valle de Aburrá' },
  { codigo: '05031', nombre: 'AMALFI', subregion: 'Nordeste' },
  { codigo: '05034', nombre: 'ANDES', subregion: 'Suroeste' },
  { codigo: '05036', nombre: 'ANGELÓPOLIS', subregion: 'Suroeste' },
  { codigo: '05038', nombre: 'ANGOSTURA', subregion: 'Norte' },
  { codigo: '05040', nombre: 'ANORÍ', subregion: 'Nordeste' },
  { codigo: '05042', nombre: 'SANTA FÉ DE ANTIOQUIA', subregion: 'Occidente' },
  { codigo: '05044', nombre: 'ANZÁ', subregion: 'Occidente' },
  { codigo: '05045', nombre: 'APARTADÓ', subregion: 'Urabá' },
  { codigo: '05051', nombre: 'ARBOLETES', subregion: 'Urabá' },
  { codigo: '05055', nombre: 'ARGELIA', subregion: 'Oriente' },
  { codigo: '05059', nombre: 'ARMENIA', subregion: 'Suroeste' },
  { codigo: '05079', nombre: 'BARBOSA', subregion: 'Norte' },
  { codigo: '05086', nombre: 'BELMIRA', subregion: 'Norte' },
  { codigo: '05088', nombre: 'BELLO', subregion: 'Valle de Aburrá' },
  { codigo: '05091', nombre: 'BETANIA', subregion: 'Suroeste' },
  { codigo: '05093', nombre: 'BETULIA', subregion: 'Suroeste' },
  { codigo: '05101', nombre: 'CIUDAD BOLÍVAR', subregion: 'Suroeste' },
  { codigo: '05107', nombre: 'BRICEÑO', subregion: 'Norte' },
  { codigo: '05113', nombre: 'BURITICÁ', subregion: 'Occidente' },
  { codigo: '05120', nombre: 'CÁCERES', subregion: 'Bajo Cauca' },
  { codigo: '05125', nombre: 'CAICEDO', subregion: 'Bajo Cauca' },
  { codigo: '05129', nombre: 'CALDAS', subregion: 'Valle de Aburrá' },
  { codigo: '05134', nombre: 'CAMPAMENTO', subregion: 'Norte' },
  { codigo: '05138', nombre: 'CAÑASGORDAS', subregion: 'Occidente' },
  { codigo: '05142', nombre: 'CARACOLÍ', subregion: 'Oriente' },
  { codigo: '05145', nombre: 'CARAMANTA', subregion: 'Suroeste' },
  { codigo: '05147', nombre: 'CAREPA', subregion: 'Urabá' },
  { codigo: '05148', nombre: 'EL CARMEN DE VIBORAL', subregion: 'Oriente' },
  { codigo: '05150', nombre: 'CAROLINA', subregion: 'Oriente' },
  { codigo: '05154', nombre: 'CAUCASIA', subregion: 'Bajo Cauca' },
  { codigo: '05172', nombre: 'CHIGORODÓ', subregion: 'Urabá' },
  { codigo: '05190', nombre: 'CISNEROS', subregion: 'Nordeste' },
  { codigo: '05197', nombre: 'COCORNÁ', subregion: 'Oriente' },
  { codigo: '05206', nombre: 'CONCEPCIÓN', subregion: 'Oriente' },
  { codigo: '05209', nombre: 'CONCORDIA', subregion: 'Suroeste' },
  { codigo: '05212', nombre: 'COPACABANA', subregion: 'Valle de Aburrá' },
  { codigo: '05234', nombre: 'DABEIBA', subregion: 'Occidente' },
  { codigo: '05237', nombre: 'DONMATÍAS', subregion: 'Norte' },
  { codigo: '05240', nombre: 'EBÉJICO', subregion: 'Occidente' },
  { codigo: '05250', nombre: 'EL BAGRE', subregion: 'Bajo Cauca' },
  { codigo: '05264', nombre: 'ENTRERRÍOS', subregion: 'Oriente' },
  { codigo: '05266', nombre: 'ENVIGADO', subregion: 'Valle de Aburrá' },
  { codigo: '05282', nombre: 'FREDONIA', subregion: 'Suroeste' },
  { codigo: '05284', nombre: 'FRONTINO', subregion: 'Occidente' },
  { codigo: '05306', nombre: 'GIRALDO', subregion: 'Norte' }
]

// Computed
const errorString = computed(() => {
  return Array.isArray(props.errors) ? props.errors.join(', ') : ''
})

// Convertir municipios a opciones del select
const municipalityOptions = computed((): SelectOption[] => {
  return municipalities.map(municipality => ({
    value: municipality.codigo,
    label: `${municipality.nombre} (${municipality.subregion})`,
    municipality
  }))
})

// Filtrar opciones basado en la búsqueda
const filteredOptions = computed((): SelectOption[] => {
  if (!searchQuery.value.trim()) {
    return municipalityOptions.value
  }
  
  const query = searchQuery.value.toLowerCase().trim()
  return municipalityOptions.value.filter(option => {
    const municipality = option.municipality
    const nombre = municipality.nombre.toLowerCase()
    const codigo = municipality.codigo.toLowerCase()
    const subregion = municipality.subregion.toLowerCase()
    return nombre.includes(query) || codigo.includes(query) || subregion.includes(query)
  })
})

// Obtener el municipio seleccionado actual
const currentSelectedMunicipality = computed((): MunicipalityInfo | null => {
  if (!selectedMunicipality.value) return null
  
  const option = municipalityOptions.value.find(opt => opt.value === selectedMunicipality.value)
  return option?.municipality || null
})

// Texto que se muestra en el input
const displayText = computed(() => {
  if (isFocused.value) {
    return searchQuery.value
  }
  
  if (selectedMunicipality.value) {
    // Si el código existe en la lista interna, mostrar su nombre
    if (currentSelectedMunicipality.value) {
      return currentSelectedMunicipality.value.nombre
    }
    // Fallback: si el código no está en la lista interna, mostrar el nombre externo o el código
    return props.selectedName || selectedMunicipality.value
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
    if (!selectedMunicipality.value) {
      searchQuery.value = ''
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

const selectOption = (option: SelectOption) => {
  selectedMunicipality.value = option.value
  searchQuery.value = ''
  isOpen.value = false
  highlightedIndex.value = -1
  
  // Emit events
  emit('update:modelValue', option.value)
  emit('municipality-selected', option.municipality)
  emit('municipality-code-change', option.municipality.codigo)
  emit('municipality-name-change', option.municipality.nombre)
  emit('subregion-change', option.municipality.subregion)
  
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
  selectedMunicipality.value = newValue || ''
  // Cuando el valor viene del padre (p.ej. carga de paciente), sincronizar el texto mostrado
  const externalName = currentSelectedMunicipality.value?.nombre || props.selectedName || ''
  // Actualizar el texto mostrado aunque el input esté enfocado para reflejar la selección externa
  searchQuery.value = externalName
  // Cerrar el dropdown si estaba abierto
  isOpen.value = false
  highlightedIndex.value = -1
}, { immediate: true })

watch(selectedMunicipality, (newValue) => {
  if (newValue !== props.modelValue) {
    emit('update:modelValue', newValue)
  }
})

// Watcher para la búsqueda
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
</script>

<style scoped>
.municipality-combobox {
  position: relative;
}
</style>