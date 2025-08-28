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
          <span class="font-medium">{{ displayDisease.codigo }}</span> - {{ displayDisease.nombre }}
        </div>
      </div>

      <!-- Diagnóstico CIEO Seleccionado -->
      <div v-if="selectedDiseaseCIEO" class="p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 class="text-sm font-medium text-blue-900 mb-2">Diagnóstico CIEO Seleccionado</h4>
        <div class="text-xs text-blue-800">
          <span class="font-medium">{{ selectedDiseaseCIEO.codigo }}</span> - {{ selectedDiseaseCIEO.nombre }}
        </div>
      </div>
    </div>

    <!-- Results Table -->
    <div v-if="searchResults.length > 0" class="border border-gray-300 rounded-lg overflow-hidden">
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
                  {{ disease.codigo }}
                </span>
              </td>
              <td class="px-3 py-2 text-sm text-gray-900">{{ disease.nombre }}</td>
              <td class="px-3 py-2 text-sm">
                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                  {{ disease.tabla }}
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
    <div v-else-if="hasSearched && !isSearching" class="text-center py-8 text-gray-500">
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
import { useDiseaseAPI } from '../../composables/useDiseaseAPI'
import { FormCheckbox } from '../forms'

// Types
interface Disease {
  id: string
  tabla: string
  codigo: string
  nombre: string
  descripcion?: string
  isActive: boolean
}

// Props
interface Props {
  modelValue?: Disease | null
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
  
  try {
    const result = await searchDiseases(searchQuery.value, 'CIE10')
    
    if (result.success) {
      searchResults.value = result.diseases || []
    } else {
      searchResults.value = []
      loadError.value = result.error || 'Error al buscar enfermedades'
    }
  } catch (error: any) {
    searchResults.value = []
    loadError.value = 'Error al buscar enfermedades'
  }
}

const handleSearchCIEO = async () => {
  if (!searchQueryCIEO.value.trim() || props.disabled) return
  
  hasSearched.value = true
  
  try {
    const result = await searchDiseases(searchQueryCIEO.value, 'CIEO')
    
    if (result.success) {
      searchResults.value = result.diseases || []
    } else {
      searchResults.value = []
      loadError.value = result.error || 'Error al buscar enfermedades'
    }
  } catch (error: any) {
    searchResults.value = []
    loadError.value = 'Error al buscar enfermedades'
  }
}

const selectDisease = (disease: Disease) => {
  // Determinar si es CIE-10 o CIEO basándose en la tabla
  if (disease.tabla === 'CIEO') {
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

// Función para limpiar diagnóstico CIEO
const clearCIEODiagnosis = () => {
  selectedDiseaseCIEO.value = null
}

// Función para limpiar diagnóstico CIE-10
const clearCIE10Diagnosis = () => {
  selectedDisease.value = null
  emit('update:modelValue', null)
}

// Función para recargar enfermedades (mantenida por compatibilidad)
const reloadDiseases = async () => {
  try {
    loadError.value = ''
    // En el nuevo diseño, no necesitamos cargar todas las enfermedades
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
