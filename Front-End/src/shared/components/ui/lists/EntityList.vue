<template>
  <div class="entity-combobox">
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
            errorString ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : (selectedEntity ? 'border-green-500' : 'border-gray-300'),
            disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : 'text-gray-900'
          ]"
          @focus="handleFocus"
          @blur="handleBlur"
          @keydown="handleKeyDown"
          autocomplete="off"
        />
        
        <!-- Loading spinner -->
        <div v-if="isLoadingEntities" class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
          <svg class="animate-spin h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        
        <!-- Dropdown arrow -->
        <div v-else class="absolute inset-y-0 right-0 pr-3 flex items-center">
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
        <!-- Loading state -->
        <div v-if="isLoadingEntities" class="px-3 py-2 text-sm text-gray-500 text-center">
          Cargando entidades...
        </div>
        
        <!-- No results -->
        <div v-else-if="filteredOptions.length === 0" class="px-3 py-2 text-sm text-gray-500 text-center">
          {{ searchQuery.trim() ? 'No se encontraron entidades' : 'No hay entidades disponibles' }}
        </div>
        
        <!-- Options -->
        <div
          v-for="(option, index) in filteredOptions"
          :key="option.value"
          :class="[
            'px-3 py-2 text-sm cursor-pointer transition-colors',
            index === highlightedIndex ? 'bg-blue-50 text-blue-900' : 'text-gray-900 hover:bg-gray-100',
            selectedEntity === option.value ? 'bg-blue-100 text-blue-900 font-medium' : ''
          ]"
          @click="selectOption(option)"
          @mouseenter="highlightedIndex = index"
        >
          <div class="flex items-center justify-between">
            <div class="flex flex-col">
              <span class="font-medium">{{ option.label }}</span>
              <span v-if="(option.entity as any).codigo || (option.entity as any).id" class="text-xs text-gray-500">{{ (option.entity as any).codigo || (option.entity as any).id }}</span>
            </div>
            <svg 
              v-if="selectedEntity === option.value"
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

    <!-- Load error -->
    <div v-if="loadError" class="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-amber-600 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
        <div>
          <p class="text-sm text-amber-800">No se pudieron cargar las entidades.</p>
          <button
            @click="reloadEntities"
            class="mt-1 text-sm text-amber-700 hover:text-amber-800 underline font-medium"
          >
            Intentar cargar nuevamente
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted, nextTick } from 'vue'
import type { EntityInfo, SelectOption } from '@/modules/cases/types'
import { useEntityAPI } from '@/modules/cases/composables'

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
  placeholder: 'Buscar y seleccionar entidad...',
  required: false,
  disabled: false,
  helpText: '',
  errors: () => [],
  autoLoad: true
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string]
  'entity-selected': [entity: EntityInfo | null]
  'load-error': [error: string]
  'load-success': [entities: EntityInfo[]]
}>()

// Composables
const { entities, loadEntities, isLoading: isLoadingEntities } = useEntityAPI()

// Refs
const inputRef = ref<HTMLInputElement>()
const searchQuery = ref('')
const isOpen = ref(false)
const highlightedIndex = ref(-1)
const loadError = ref('')
const isFocused = ref(false)

// Estado interno del componente seleccionado
const selectedEntity = ref(props.modelValue)

// Computed
const errorString = computed(() => {
  return Array.isArray(props.errors) ? props.errors.join(', ') : ''
})

// Convertir entidades a opciones del select
const entityOptions = computed((): (SelectOption & { entity: EntityInfo })[] => {
  if (!Array.isArray(entities.value)) {
    return []
  }
  
  return entities.value.map(entity => ({
    value: (entity as any).codigo || (entity as any).id,
    label: (entity as any).nombre || (entity as any).name,
    entity
  }))
})

// Filtrar opciones basado en la búsqueda
const filteredOptions = computed((): (SelectOption & { entity: EntityInfo })[] => {
  if (!searchQuery.value.trim()) {
    return entityOptions.value
  }
  
  const query = searchQuery.value.toLowerCase().trim()
  return entityOptions.value.filter(option => {
    const label = option.label.toLowerCase()
    const entity = option.entity as any
    const nombre = (entity.nombre || entity.name || '').toLowerCase()
    const codigo = (entity.codigo || entity.id || '').toLowerCase()
    return label.includes(query) || nombre.includes(query) || codigo.includes(query)
  })
})

// Obtener la entidad seleccionada actual
const currentSelectedEntity = computed((): EntityInfo | null => {
  if (!selectedEntity.value) return null
  
  const option = entityOptions.value.find(opt => opt.value === selectedEntity.value)
  return option?.entity || null
})

// Texto que se muestra en el input
const displayText = computed(() => {
  if (isFocused.value) {
    return searchQuery.value
  }
  
  if (selectedEntity.value && currentSelectedEntity.value) {
    const e: any = currentSelectedEntity.value
    return e.nombre || e.name
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
    if (!selectedEntity.value) {
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

const selectOption = (option: SelectOption & { entity: EntityInfo }) => {
  selectedEntity.value = option.value
  searchQuery.value = ''
  isOpen.value = false
  highlightedIndex.value = -1
  
  // Emit events
  emit('update:modelValue', option.value)
  emit('entity-selected', option.entity)
  
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

// Función para recargar entidades
const reloadEntities = async () => {
  try {
    loadError.value = ''
    const result = await loadEntities()
    
    if (result.success) {
      emit('load-success', entities.value)
    } else {
      loadError.value = result.message || 'Error al cargar entidades'
      emit('load-error', loadError.value)
    }
  } catch (error: any) {
    const errorMessage = 'Error al cargar la lista de entidades'
    loadError.value = errorMessage
    emit('load-error', errorMessage)
    console.error('Error al recargar entidades:', error)
  }
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  selectedEntity.value = newValue || ''
}, { immediate: true })

watch(selectedEntity, (newValue) => {
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

// Lifecycle
onMounted(async () => {
  if (props.autoLoad && entities.value.length === 0) {
    await reloadEntities()
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
.entity-combobox {
  position: relative;
}
</style>
