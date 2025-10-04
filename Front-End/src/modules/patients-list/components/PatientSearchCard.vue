<template>
  <ComponentCard 
    title="Buscar Pacientes"
    description="Filtre y busque pacientes por diferentes criterios."
  >
    <template #icon>
      <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
      </svg>
    </template>

    <div class="space-y-4">
      <!-- Search filters section -->
      <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <h3 class="text-sm font-semibold text-gray-700 mb-4 flex items-center">
          <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/>
          </svg>
          Filtros de Búsqueda
        </h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <!-- Search by name/document -->
          <div>
            <FormInputField
              id="search-text"
              v-model="searchFilters.searchText"
              type="text"
              label="Nombre o Documento"
              placeholder="Buscar por nombre o documento..."
              @update:model-value="handleSearchChange"
            />
          </div>

          <!-- Gender filter -->
          <div>
            <FormSelect
              id="gender-filter"
              v-model="searchFilters.gender"
              label="Sexo"
              :options="genderOptions"
              @update:model-value="handleFilterChange"
            />
          </div>

          <!-- Entity filter -->
          <div>
            <FormSelect
              id="entity-filter"
              v-model="searchFilters.entityId"
              label="Entidad"
              :options="entityOptions"
              @update:model-value="handleFilterChange"
            />
          </div>

          <!-- Care type filter -->
          <div>
            <FormSelect
              id="care-type-filter"
              v-model="searchFilters.careType"
              label="Tipo de Atención"
              :options="careTypeOptions"
              @update:model-value="handleFilterChange"
            />
          </div>

          <!-- Age range -->
          <div>
            <FormInputField
              id="age-from"
              v-model="searchFilters.ageFrom"
              type="number"
              label="Edad Desde"
              placeholder="Edad mínima"
              min="0"
              max="120"
              @update:model-value="handleFilterChange"
            />
          </div>

          <div>
            <FormInputField
              id="age-to"
              v-model="searchFilters.ageTo"
              type="number"
              label="Edad Hasta"
              placeholder="Edad máxima"
              min="0"
              max="120"
              @update:model-value="handleFilterChange"
            />
          </div>
        </div>

        <!-- Action buttons -->
        <div class="flex flex-wrap gap-3 mt-4 pt-4 border-t border-gray-200">
          <SearchButton 
            text="Buscar" 
            loading-text="Buscando..." 
            :loading="isSearching" 
            @click="handleSearch" 
            size="md" 
            variant="primary" 
          />
          <ClearButton 
            text="Limpiar Filtros" 
            @click="handleClearFilters" 
          />
          <button
            @click="handleToggleAdvanced"
            class="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4"/>
            </svg>
            {{ showAdvanced ? 'Ocultar Avanzado' : 'Búsqueda Avanzada' }}
          </button>
        </div>

        <!-- Advanced filters (collapsible) -->
        <div v-if="showAdvanced" class="mt-4 pt-4 border-t border-gray-200">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Date range -->
            <div>
              <FormInputField
                id="created-from"
                v-model="searchFilters.createdFrom"
                type="date"
                label="Creado Desde"
                @update:model-value="handleFilterChange"
              />
            </div>
            <div>
              <FormInputField
                id="created-to"
                v-model="searchFilters.createdTo"
                type="date"
                label="Creado Hasta"
                @update:model-value="handleFilterChange"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Search results summary -->
      <div v-if="searchResults" class="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <svg class="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <div>
              <h4 class="text-sm font-semibold text-blue-800">Resultados de Búsqueda</h4>
              <p class="text-xs text-blue-600 mt-0.5">
                {{ searchResults.totalItems }} paciente{{ searchResults.totalItems !== 1 ? 's' : '' }} encontrado{{ searchResults.totalItems !== 1 ? 's' : '' }}
              </p>
            </div>
          </div>
          <div class="text-right">
            <p class="text-xs text-blue-600 font-medium">Página</p>
            <p class="text-sm font-bold text-blue-800">{{ searchResults.currentPage }} de {{ searchResults.totalPages }}</p>
          </div>
        </div>
      </div>

      <!-- Error message -->
      <div v-if="searchError" class="bg-red-50 border border-red-200 rounded-lg p-3">
        <div class="flex items-center">
          <svg class="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
          </svg>
          <p class="text-sm text-red-600">{{ searchError }}</p>
        </div>
      </div>
    </div>
  </ComponentCard>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ComponentCard } from '@/shared/components'
import { FormInputField, FormSelect } from '@/shared/components/forms'
import { SearchButton, ClearButton } from '@/shared/components/buttons'

// Types
interface SearchFilters {
  searchText: string
  gender: string
  entityId: string
  careType: string
  ageFrom: string
  ageTo: string
  createdFrom: string
  createdTo: string
}

interface SearchResults {
  totalItems: number
  currentPage: number
  totalPages: number
}

// Props
interface Props {
  isSearching?: boolean
  searchError?: string
  searchResults?: SearchResults | null
  genderOptions?: Array<{ value: string; label: string }>
  entityOptions?: Array<{ value: string; label: string }>
  careTypeOptions?: Array<{ value: string; label: string }>
}

const props = withDefaults(defineProps<Props>(), {
  isSearching: false,
  searchError: '',
  searchResults: null,
  genderOptions: () => [
    { value: '', label: 'Todos' },
    { value: 'M', label: 'Masculino' },
    { value: 'F', label: 'Femenino' }
  ],
  entityOptions: () => [
    { value: '', label: 'Todas las entidades' }
  ],
  careTypeOptions: () => [
    { value: '', label: 'Todos los tipos' },
    { value: 'Contributivo', label: 'Contributivo' },
    { value: 'Subsidiado', label: 'Subsidiado' },
    { value: 'Particular', label: 'Particular' }
  ]
})

// Emits
const emit = defineEmits<{
  'search': [filters: SearchFilters]
  'clear-filters': []
  'filter-change': [filters: SearchFilters]
}>()

// State
const showAdvanced = ref(false)
const searchFilters = reactive<SearchFilters>({
  searchText: '',
  gender: '',
  entityId: '',
  careType: '',
  ageFrom: '',
  ageTo: '',
  createdFrom: '',
  createdTo: ''
})

// Methods
const handleSearch = () => {
  emit('search', { ...searchFilters })
}

const handleClearFilters = () => {
  Object.keys(searchFilters).forEach(key => {
    searchFilters[key as keyof SearchFilters] = ''
  })
  emit('clear-filters')
}

const handleFilterChange = () => {
  emit('filter-change', { ...searchFilters })
}

const handleSearchChange = () => {
  // Debounced search for text input
  handleFilterChange()
}

const handleToggleAdvanced = () => {
  showAdvanced.value = !showAdvanced.value
}
</script>