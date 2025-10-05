<template>
  <div class="disease-selector">
    <!-- Label -->
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>

    <!-- Buscador principal -->
    <div class="mb-4">
      <div class="flex gap-2">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="placeholder"
          :disabled="disabled || isSearching"
          class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-colors bg-white"
          @input="handleSearchInput"
          @keydown.enter="handleSearch"
          autocomplete="off"
        />
        <button
          @click="handleSearch"
          :disabled="disabled || isSearching || !searchQuery.trim()"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <svg v-if="isSearching" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span v-else>Buscar</span>
        </button>
      </div>
    </div>

    <!-- Checkbox para activar diagnóstico de cáncer -->
    <div class="mb-4">
      <FormCheckbox
        v-model="showCIEODiagnosis"
        label="Incluir diagnóstico de cáncer (CIEO)"
        id="cieo-checkbox"
      />
    </div>

    <!-- Buscador CIEO (solo visible si está activado el checkbox) -->
    <div v-if="showCIEODiagnosis" class="mb-4">
      <label class="block text-xs font-medium text-gray-600 mb-2">Diagnóstico de cáncer:</label>
      <div class="flex gap-2">
        <input
          v-model="searchQueryCIEO"
          type="text"
          placeholder="Buscar cáncer CIEO..."
          :disabled="disabled || isSearching"
          class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-colors bg-white"
          @input="handleSearchInputCIEO"
          @keydown.enter="handleSearchCIEO"
          autocomplete="off"
        />
        <button
          @click="handleSearchCIEO"
          :disabled="disabled || isSearching || !searchQueryCIEO.trim()"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <svg v-if="isSearching" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span v-else>Buscar</span>
        </button>
      </div>
    </div>

    <!-- Diagnósticos Seleccionados -->
    <div v-if="displayDisease || selectedDiseaseCIEO" class="mb-4 space-y-3">
      <!-- Diagnóstico CIE-10 Seleccionado -->
      <div v-if="displayDisease" class="p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 class="text-sm font-medium text-blue-900 mb-2">Diagnóstico CIE-10 Seleccionado</h4>
        <div class="text-xs text-blue-800">
          <span class="font-medium">{{ displayDisease.code }}</span> - {{ displayDisease.name }}
        </div>
      </div>

      <!-- Diagnóstico CIEO Seleccionado -->
      <div v-if="selectedDiseaseCIEO" class="p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 class="text-sm font-medium text-blue-900 mb-2">Diagnóstico CIEO Seleccionado</h4>
        <div class="text-xs text-blue-800">
          <span class="font-medium">{{ selectedDiseaseCIEO.code }}</span> - {{ selectedDiseaseCIEO.name }}
        </div>
      </div>
    </div>

    <!-- Results Table -->
    <div v-if="showResultsTable && searchResults.length > 0" class="border border-gray-300 rounded-lg overflow-hidden">
      <div class="max-h-60 overflow-y-auto">
        <table class="w-full">
          <thead class="bg-gray-50 sticky top-0">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Código</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tabla</th>
              <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acción</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="disease in searchResults"
              :key="disease.id"
              class="hover:bg-gray-50 cursor-pointer"
              @click="selectDisease(disease)"
            >
              <td class="px-3 py-2 text-sm">
                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                  {{ disease.code }}
                </span>
              </td>
              <td class="px-3 py-2 text-sm text-gray-900">{{ disease.name }}</td>
              <td class="px-3 py-2 text-sm">
                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                  {{ disease.table }}
                </span>
              </td>
              <td class="px-3 py-2 text-sm">
                <button
                  @click.stop="selectDisease(disease)"
                  class="text-blue-600 hover:text-blue-800 font-medium"
                >
                  Seleccionar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Results Info -->
      <div class="px-3 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-500">
        {{ searchResults.length }} resultado{{ searchResults.length !== 1 ? 's' : '' }} encontrado{{ searchResults.length !== 1 ? 's' : '' }}
      </div>
    </div>

    <!-- No Results -->
    <div v-else-if="showResultsTable && hasSearched && !isSearching" class="text-center py-8 text-gray-500">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <p class="mt-2">No se encontraron enfermedades</p>
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
        <svg class="w-5 h-5 text-amber-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
        <div>
          <p class="text-sm text-amber-800">No se pudieron cargar las enfermedades.</p>
          <button
            @click="reloadDiseases"
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
import { computed, ref, watch, onMounted } from 'vue'
import { useDiseaseAPI } from '@/shared/composables/useDiseaseAPI'
import { FormCheckbox } from '../forms'

// Types
interface Disease {
  id?: string
  table: string
  code: string
  name: string
  description?: string
  is_active: boolean
}

// Props
interface Props {
  modelValue?: Disease | null
  cieoValue?: Disease | null
  label?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  helpText?: string
  errors?: string[]
  autoLoad?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  cieoValue: null,
  label: '',
  placeholder: 'Buscar enfermedad CIE-10...',
  required: false,
  disabled: false,
  helpText: '',
  errors: () => [],
  autoLoad: false
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: Disease | null]
  'disease-selected': [disease: Disease | null]
  'cieo-disease-selected': [disease: Disease | null]
  'load-error': [error: string]
  'load-success': [results: Disease[]]
}>()

// Composables
const { searchDiseases, isLoading: isSearching } = useDiseaseAPI()

// Refs
const searchQuery = ref('')
const searchQueryCIEO = ref('')
const searchResults = ref<Disease[]>([])
const hasSearched = ref(false)
const loadError = ref('')
const showCIEODiagnosis = ref(false)

// Refs para búsqueda
const searchTimeout = ref<NodeJS.Timeout | null>(null)
const searchTimeoutCIEO = ref<NodeJS.Timeout | null>(null)
const showResultsTable = ref(false) // Controla si se muestra la tabla de resultados

// Estado interno del componente seleccionado
const selectedDisease = ref<Disease | null>(props.modelValue)
const selectedDiseaseCIEO = ref<Disease | null>(null) // Nuevo estado para CIEO

// Computed que combine el valor interno y el externo
const displayDisease = computed(() => {
  return selectedDisease.value || props.modelValue
})

// Computed
const errorString = computed(() => {
  return Array.isArray(props.errors) ? props.errors.join(', ') : ''
})

// Funciones del componente
const handleSearch = async () => {
  if (!searchQuery.value.trim() || props.disabled) return
  
  hasSearched.value = true
  showResultsTable.value = true // Mostrar tabla solo cuando se hace clic en "Buscar"
  
  try {
    // Hacer búsqueda amplia en el servidor para obtener más resultados
    const result = await searchDiseases('', 'CIE10', 10000) // Obtener todas las enfermedades
    
    if (result.success && result.diseases) {
      // Filtrar localmente con búsqueda flexible
      const filteredResults = filterDiseasesFlexibly(result.diseases, searchQuery.value)
      searchResults.value = filteredResults
    } else {
      searchResults.value = []
      loadError.value = result.error || 'Error al buscar enfermedades'
    }
  } catch (error: any) {
    searchResults.value = []
    loadError.value = 'Error al buscar enfermedades'
  }
}

// Nueva función para manejar input en tiempo real
const handleSearchInput = () => {
  // Limpiar timeout anterior
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  
  // Limpiar tabla si el campo está vacío
  if (searchQuery.value.length < 2) {
    showResultsTable.value = false
    return
  }
  
  // No hacer nada más - solo limpiar la tabla cuando el campo está vacío
  // La tabla solo se muestra cuando se hace clic en "Buscar"
}

const handleSearchCIEO = async () => {
  if (!searchQueryCIEO.value.trim() || props.disabled) return
  
  hasSearched.value = true
  showResultsTable.value = true // Mostrar tabla solo cuando se hace clic en "Buscar"
  
  try {
    // Hacer búsqueda amplia en el servidor para obtener más resultados
    const result = await searchDiseases('', 'CIEO', 10000) // Obtener todas las enfermedades
    
    if (result.success && result.diseases) {
      // Filtrar localmente con búsqueda flexible
      const filteredResults = filterDiseasesFlexibly(result.diseases, searchQueryCIEO.value)
      searchResults.value = filteredResults
    } else {
      searchResults.value = []
      loadError.value = result.error || 'Error al buscar enfermedades'
    }
  } catch (error: any) {
    searchResults.value = []
    loadError.value = 'Error al buscar enfermedades'
  }
}

// Nueva función para manejar input CIEO en tiempo real
const handleSearchInputCIEO = () => {
  // Limpiar timeout anterior
  if (searchTimeoutCIEO.value) {
    clearTimeout(searchTimeoutCIEO.value)
  }
  
  // Limpiar tabla si el campo está vacío
  if (searchQueryCIEO.value.length < 2) {
    showResultsTable.value = false
    return
  }
  
  // No hacer nada más - solo limpiar la tabla cuando el campo está vacío
  // La tabla solo se muestra cuando se hace clic en "Buscar"
}

const selectDisease = (disease: Disease) => {
  // Determinar si es CIE-10 o CIEO basándose en la tabla
  if (disease.table === 'CIEO') {
    selectedDiseaseCIEO.value = disease
    // Emitir evento para CIEO
    emit('cieo-disease-selected', disease)
  } else {
    selectedDisease.value = disease
    // Emitir evento para CIE-10
    emit('update:modelValue', disease)
    emit('disease-selected', disease)
  }
  
  searchResults.value = [] // Limpiar resultados después de seleccionar
  hasSearched.value = false
}

// Funciones para limpiar diagnósticos (exportadas para uso externo si es necesario)
const clearCIEODiagnosis = () => {
  selectedDiseaseCIEO.value = null
}

const clearCIE10Diagnosis = () => {
  selectedDisease.value = null
  emit('update:modelValue', null)
}

// Función para búsqueda flexible y tolerante
const filterDiseasesFlexibly = (diseases: Disease[], query: string): Disease[] => {
  if (!query || query.trim().length < 1) return diseases
  
  const searchTerm = query.toLowerCase().trim()
  const searchWords = searchTerm.split(/\s+/).filter(word => word.length > 0)
  
  return diseases.filter(disease => {
    const code = disease.code.toLowerCase()
    const name = disease.name.toLowerCase()
    
    // Búsqueda exacta por código (máxima prioridad)
    if (code === searchTerm) return true
    
    // Búsqueda que empiece con el código
    if (code.startsWith(searchTerm)) return true
    
    // Búsqueda que contenga el código
    if (code.includes(searchTerm)) return true
    
    // Búsqueda exacta en el nombre
    if (name === searchTerm) return true
    
    // Búsqueda que empiece con el nombre
    if (name.startsWith(searchTerm)) return true
    
    // Búsqueda que contenga el nombre completo
    if (name.includes(searchTerm)) return true
    
    // Búsqueda por palabras individuales - todas las palabras deben estar en el nombre
    if (searchWords.length > 1) {
      return searchWords.every(word => name.includes(word))
    }
    
    // Búsqueda por palabras individuales - al menos una palabra debe estar en el nombre
    if (searchWords.length === 1) {
      const word = searchWords[0]
      const nameWords = name.split(/\s+/)
      return nameWords.some(nameWord => nameWord.includes(word))
    }
    
    return false
  }).sort((a, b) => {
    const aCode = a.code.toLowerCase()
    const bCode = b.code.toLowerCase()
    const aName = a.name.toLowerCase()
    const bName = b.name.toLowerCase()
    
    // Prioridad 1: Coincidencia exacta de código
    if (aCode === searchTerm && bCode !== searchTerm) return -1
    if (bCode === searchTerm && aCode !== searchTerm) return 1
    
    // Prioridad 2: Código que empiece con el término
    if (aCode.startsWith(searchTerm) && !bCode.startsWith(searchTerm)) return -1
    if (bCode.startsWith(searchTerm) && !aCode.startsWith(searchTerm)) return 1
    
    // Prioridad 3: Nombre que empiece con el término
    if (aName.startsWith(searchTerm) && !bName.startsWith(searchTerm)) return -1
    if (bName.startsWith(searchTerm) && !aName.startsWith(searchTerm)) return 1
    
    // Prioridad 4: Nombre que contenga el término
    if (aName.includes(searchTerm) && !bName.includes(searchTerm)) return -1
    if (bName.includes(searchTerm) && !aName.includes(searchTerm)) return 1
    
    // Prioridad 5: Orden alfabético por nombre
    return a.name.localeCompare(b.name)
  })
}



// Función para recargar enfermedades (mantenida por compatibilidad)
const reloadDiseases = async () => {
  try {
    loadError.value = ''
    // Limpiar resultados de búsqueda
    searchResults.value = []
    hasSearched.value = false
  } catch (error: any) {
    const errorMessage = 'Error al cargar la lista de enfermedades'
    loadError.value = errorMessage
    emit('load-error', errorMessage)
  }
}

// Watchers
watch(() => props.modelValue, (newValue) => {
  selectedDisease.value = newValue || null
}, { immediate: true })

watch(() => props.cieoValue, (newValue) => {
  selectedDiseaseCIEO.value = newValue || null
  if (newValue) {
    showCIEODiagnosis.value = true
  }
}, { immediate: true })

watch(selectedDisease, (newValue) => {
  if (newValue !== props.modelValue) {
    emit('update:modelValue', newValue)
  }
})

// Limpiar CIEO cuando se desactiva el checkbox
watch(showCIEODiagnosis, (newValue) => {
  if (!newValue) {
    selectedDiseaseCIEO.value = null
    emit('cieo-disease-selected', null)
  }
})

// Exponer funciones para uso externo
defineExpose({
  clearCIEODiagnosis,
  clearCIE10Diagnosis,
  reloadDiseases
})

// Lifecycle
onMounted(async () => {
  // En el nuevo diseño, no cargamos automáticamente todas las enfermedades
})
</script>

<style scoped>
.disease-selector {
  position: relative;
}
</style>
