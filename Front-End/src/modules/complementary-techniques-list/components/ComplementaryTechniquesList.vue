<template>
  <!-- Complementary techniques list with filters, table (desktop) and cards (mobile) -->
  <div class="overflow-hidden bg-white rounded-xl border border-gray-200">
    <!-- Loading state -->
    <div v-if="isLoading" class="flex flex-col items-center justify-center space-y-3 sm:space-y-4 py-6 sm:py-8 lg:py-12">
      <div class="relative">
        <svg class="animate-spin h-6 w-6 sm:h-8 sm:w-8 lg:h-12 lg:w-12 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
      <div class="text-center px-3 sm:px-4">
        <h3 class="text-sm sm:text-base lg:text-lg font-semibold text-gray-800 mb-1 sm:mb-2">Cargando técnicas...</h3>
        <p class="text-xs sm:text-sm text-gray-600">Obteniendo datos desde el servidor</p>
      </div>
    </div>

    <!-- Error state with retry -->
    <div v-else-if="errorCarga" class="flex flex-col items-center justify-center space-y-3 sm:space-y-4 py-6 sm:py-8 lg:py-12">
      <div class="relative">
        <svg class="h-6 w-6 sm:h-8 sm:w-8 lg:h-12 lg:w-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <div class="text-center px-3 sm:px-4">
        <h3 class="text-sm sm:text-base lg:text-lg font-semibold text-red-800 mb-1 sm:mb-2">Error al cargar técnicas</h3>
        <p class="text-xs sm:text-sm text-red-600 mb-3 sm:mb-4 max-w-sm mx-auto">{{ errorCarga }}</p>
        <button @click="cargarTecnicas" class="inline-flex items-center px-3 sm:px-4 py-1.5 sm:py-2 border border-red-300 text-red-700 bg-red-50 rounded-lg font-medium hover:bg-red-100 transition-colors text-xs sm:text-sm">
          <svg class="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Intentar nuevamente
        </button>
      </div>
    </div>

    <!-- Content: desktop table and mobile cards -->
    <div v-else class="overflow-hidden bg-white">
      <div class="hidden md:block overflow-x-auto custom-scrollbar">
          <table class="min-w-full text-sm lg:text-base">
            <thead>
              <tr class="border-b border-gray-200 bg-gray-50">
                <th 
                  v-for="columna in columnasDesktop" 
                  :key="columna.key"
                  class="px-1 sm:px-2 py-2 text-center text-gray-700"
                  :class="columna.class"
                >
                  <button 
                    class="flex items-center gap-1 font-medium text-gray-600 text-xs sm:text-sm hover:text-gray-700 justify-center w-full" 
                    @click="sortBy(columna.key)"
                  >
                    {{ columna.label }}
                    <span v-if="sortKey === columna.key" class="text-xs">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
                  </button>
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr
                v-for="tecnica in tecnicasPaginadas" 
                :key="tecnica.id"
                class="hover:bg-gray-50"
              >
                <td class="px-1 py-2 sm:py-3 text-center">
                  <span class="font-medium text-gray-800 text-xs sm:text-sm">{{ tecnica.codigo }}</span>
                </td>
                
                <td class="px-1 sm:px-2 py-2 sm:py-3 text-center">
                  <div>
                    <p class="text-gray-800 text-xs sm:text-sm truncate">{{ tecnica.nombre }}</p>
                    <p class="text-gray-500 text-xs">{{ tecnica.tipo }}</p>
                  </div>
                </td>
                
                <td class="px-1 sm:px-2 py-2 sm:py-3 text-center">
                  <p class="text-gray-800 text-xs sm:text-sm truncate">{{ tecnica.descripcion }}</p>
                  <p class="text-gray-500 text-xs truncate">{{ tecnica.categoria }}</p>
                </td>
                
                <td class="px-1 sm:px-3 py-2 sm:py-3 text-center">
                  <span class="inline-flex items-center justify-center rounded-full px-2 sm:px-3 py-0.5 sm:py-1 text-xs font-medium" :class="statusClass(tecnica)">
                    {{ tecnica.estado }}
                  </span>
                </td>
                
                <td class="px-1 sm:px-2 py-2 sm:py-3 text-center">
                  <div class="flex flex-col gap-1">
                    <p class="text-gray-800 text-xs sm:text-sm font-medium">{{ formatDate(tecnica.fechaCreacion) }}</p>
                    <p class="text-gray-500 text-xs">{{ tecnica.fechaEntrega ? formatDate(tecnica.fechaEntrega) : 'Pendiente' }}</p>
                  </div>
                </td>
                
                <td class="px-1 sm:px-2 py-2 sm:py-3 text-center">
                  <div class="flex gap-1 justify-center min-w-[100px] sm:min-w-[120px]">
                    <button class="p-1 sm:p-1.5 rounded-md hover:bg-gray-100 text-gray-600" @click.stop="() => emit('show-details', tecnica)" title="Ver detalles">
                      <InfoCircleIcon class="w-3 h-3 sm:w-4 sm:h-4" />
                    </button>
                    <button v-if="!isPatologo && !isResidente" class="p-1 sm:p-1.5 rounded-md hover:bg-gray-100 text-gray-600" @click.stop="handleEdit(tecnica)" title="Editar técnica">
                      <SettingsIcon class="w-3 h-3 sm:w-4 sm:h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
      </div>

      <div class="md:hidden">
          <div class="space-y-2 sm:space-y-3 p-2 sm:p-4">
            <div
              v-for="tecnica in tecnicasPaginadas" 
              :key="tecnica.id"
              class="bg-white border border-gray-200 rounded-lg p-3 sm:p-4 hover:shadow-md transition-shadow"
            >
              <div class="flex items-start justify-between mb-2 sm:mb-3">
                <div class="flex-1 min-w-0">
                  <h4 class="font-semibold text-gray-800 text-xs sm:text-sm truncate">{{ tecnica.codigo }}</h4>
                  <p class="text-gray-600 text-xs mt-0.5 sm:mt-1 truncate">{{ tecnica.nombre }}</p>
                  <p class="text-gray-500 text-xs truncate">{{ tecnica.tipo }}</p>
                </div>
                <div class="flex-shrink-0 ml-2 sm:ml-3">
                  <span class="inline-flex items-center justify-center rounded-full px-1.5 sm:px-2 py-0.5 sm:py-1 text-xs font-medium" :class="statusClass(tecnica)">
                    {{ tecnica.estado }}
                  </span>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-2 sm:gap-3 mb-2 sm:mb-3 text-xs">
                <div>
                  <p class="text-gray-500">Categoría</p>
                  <p class="text-gray-800 font-medium truncate">{{ tecnica.categoria }}</p>
                </div>
                <div>
                  <p class="text-gray-500">Fecha creación/entrega</p>
                  <div class="flex flex-col gap-1">
                    <p class="text-gray-800 font-medium text-xs">{{ formatDate(tecnica.fechaCreacion) }}</p>
                    <p class="text-gray-600 text-xs">{{ tecnica.fechaEntrega ? formatDate(tecnica.fechaEntrega) : 'Pendiente' }}</p>
                  </div>
                </div>
                <div>
                  <p class="text-gray-500">Estado</p>
                  <p class="text-gray-800 font-medium">
                    {{ tecnica.estado }}
                  </p>
                </div>
              </div>

              <div class="mb-2 sm:mb-3">
                <p class="text-gray-500 text-xs mb-1 sm:mb-2">Descripción</p>
                <p class="text-gray-800 text-xs leading-relaxed">{{ tecnica.descripcion }}</p>
              </div>

              <div class="flex gap-1 sm:gap-2 pt-2 border-t border-gray-100">
                <button class="flex-1 flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-3 py-1.5 sm:py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors text-xs font-medium" @click.stop="() => emit('show-details', tecnica)">
                  <InfoCircleIcon class="w-3 h-3" />
                  <span class="hidden xs:inline">Ver detalles</span>
                  <span class="xs:hidden">Ver</span>
                </button>
                <button v-if="!isPatologo && !isResidente" class="flex-1 flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-3 py-1.5 sm:py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors text-xs font-medium" @click.stop="handleEdit(tecnica)">
                  <SettingsIcon class="w-3 h-3" />
                  Editar
                </button>
              </div>
            </div>

            <div v-if="paginacion.total === 0" class="text-center py-6 sm:py-8">
              <div class="flex flex-col items-center space-y-2">
                <svg class="w-8 h-8 sm:w-12 sm:h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="text-center">
                  <p class="text-gray-500 text-xs sm:text-sm font-medium">No hay técnicas complementarias registradas</p>
                  <p class="text-gray-400 text-xs mt-1">En el sistema</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Pagination controls -->
        <div class="px-2 sm:px-4 lg:px-5 py-3 sm:py-4 border-t border-gray-200 bg-gray-50">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4">
            <div class="flex items-center gap-1 sm:gap-2 text-xs sm:text-sm text-gray-500">
              <span class="hidden sm:inline">Mostrando</span>
              <select 
                :value="paginacion.elementosPorPagina" 
                @change="updateItemsPerPage" 
                class="h-7 sm:h-8 rounded-lg border border-gray-300 bg-white px-1.5 sm:px-2 py-0.5 sm:py-1 text-xs sm:text-sm text-gray-700"
              >
                <option v-for="option in itemsPerPageOptions" :key="option" :value="option">{{ option }}</option>
              </select>
              <span class="text-xs sm:text-sm">de {{ paginacion.total }}</span>
            </div>
            
            <div class="flex items-center justify-center gap-1 sm:gap-2">
              <button 
                @click="goToPrevPage" 
                :disabled="paginacion.pagina === 1" 
                class="px-2 sm:px-3 py-1 sm:py-1.5 border rounded-lg text-xs sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
              >
                <span class="hidden sm:inline">Anterior</span>
                <span class="sm:hidden">←</span>
              </button>
              
              <div class="flex items-center gap-1 text-xs sm:text-sm text-gray-500">
                <span class="hidden sm:inline">Página</span>
                <span class="font-medium">{{ paginacion.pagina }}</span>
                <span class="hidden sm:inline">de</span>
                <span class="hidden sm:inline">{{ totalPages }}</span>
                <span class="sm:hidden">/ {{ totalPages }}</span>
              </div>
              
              <button 
                @click="goToNextPage" 
                :disabled="paginacion.pagina === totalPages" 
                class="px-2 sm:px-3 py-1 sm:py-1.5 border rounded-lg text-xs sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
              >
                <span class="hidden sm:inline">Siguiente</span>
                <span class="sm:hidden">→</span>
              </button>
            </div>
          </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { usePermissions } from '@/shared/composables/usePermissions'
import { InfoCircleIcon, SettingsIcon } from '@/assets/icons'
import { useComplementaryTechniques } from '../composables/useComplementaryTechniques'
import type { TecnicaComplementaria } from '../types/ctl.types'

// Events emitted to parent
const emit = defineEmits<{
  'show-details': [tecnica: TecnicaComplementaria]
  'edit-technique': [tecnica: TecnicaComplementaria]
}>()

const { isPatologo, isResidente } = usePermissions()

const {
  tecnicasComplementarias,
  isLoading,
  errorCarga,
  sortKey,
  sortOrder,
  tecnicasPaginadas,
  totalPages,
  paginacion,
  cargarTecnicas,
  ordenarPor,
  formatDate,
  statusClass,
  cambiarPagina,
  cambiarElementosPorPagina
} = useComplementaryTechniques()

const itemsPerPageOptions = [10, 20, 50, 100]

// Desktop table columns
const columnasDesktop = [
  { key: 'codigo', label: 'Código', class: 'w-[8%]' },
  { key: 'nombre', label: 'Nombre', class: 'w-[20%]' },
  { key: 'descripcion', label: 'Descripción', class: 'w-[25%]' },
  { key: 'estado', label: 'Estado', class: 'w-[12%]' },
  { key: 'fechaCreacion', label: 'Fecha de creación/entrega', class: 'w-[15%]' },
  { key: 'acciones', label: 'Acciones', class: 'w-[10%]' }
]

const goToPrevPage = () => cambiarPagina(paginacion.value.pagina - 1)
const goToNextPage = () => cambiarPagina(paginacion.value.pagina + 1)

const updateItemsPerPage = (event: Event) => {
  const newValue = Number((event.target as HTMLSelectElement).value)
  cambiarElementosPorPagina(newValue)
}

const sortBy = (key: string) => {
  ordenarPor(key)
}

const handleEdit = (tecnica: TecnicaComplementaria) => {
  emit('edit-technique', tecnica)
}

onMounted(() => {
  cargarTecnicas()
})
</script>

<style scoped>
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.animate-pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
.custom-scrollbar::-webkit-scrollbar { height: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 3px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: #888; border-radius: 3px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #555; }
@media (min-width: 640px) { .custom-scrollbar::-webkit-scrollbar { height: 6px; } }
@media (hover: none) and (pointer: coarse) {
  .hover\:bg-gray-50:hover, .hover\:shadow-md:hover { background-color: transparent; box-shadow: none; }
}
.transition-shadow { transition: box-shadow 0.2s ease-in-out; }
.transition-colors { transition: color 0.2s ease-in-out, background-color 0.2s ease-in-out; }
button:focus-visible, select:focus-visible { outline: 2px solid #3b82f6; outline-offset: 2px; }
@media (max-width: 480px) { .xs\:hidden { display: none; } .xs\:inline { display: inline; } }
@media (min-width: 481px) { .xs\:hidden { display: inline; } .xs\:inline { display: none; } }
</style>
