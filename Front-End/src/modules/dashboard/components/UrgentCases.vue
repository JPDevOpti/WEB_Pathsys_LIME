<template>
  <Card class="overflow-hidden">
    <div class="px-3 sm:px-4 lg:px-6 py-3 sm:py-4 border-b border-gray-200">
      <div class="flex flex-col gap-3 sm:gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div class="flex-1 min-w-0">
          <h3 class="text-sm sm:text-base lg:text-lg font-semibold text-gray-800">Casos urgentes</h3>
          <p class="mt-1 text-xs sm:text-sm text-gray-500">
            {{ isLoading ? 'Cargando...' : `${casosUrgentes.length} casos urgentes (>6 días)` }}
          </p>
        </div>
        <div class="w-full sm:w-auto lg:w-80 flex-shrink-0">
          <PathologistList
            v-model="patologoSeleccionado"
            label="Patólogo"
            placeholder="Todos los Patólogos"
            @pathologist-selected="onPathologistSelected"
            @load-error="onPathologistLoadError"
          />
        </div>
      </div>
    </div>

    <div class="p-0">
      <div v-if="isLoading" class="flex flex-col items-center justify-center space-y-3 sm:space-y-4 py-6 sm:py-8 lg:py-12">
        <div class="relative">
          <svg class="animate-spin h-6 w-6 sm:h-8 sm:w-8 lg:h-12 lg:w-12 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        <div class="text-center px-3 sm:px-4">
          <h3 class="text-sm sm:text-base lg:text-lg font-semibold text-gray-800 mb-1 sm:mb-2">Cargando casos urgentes...</h3>
          <p class="text-xs sm:text-sm text-gray-600">Obteniendo datos desde el servidor</p>
        </div>
      </div>

      <div v-else-if="errorCarga" class="flex flex-col items-center justify-center space-y-3 sm:space-y-4 py-6 sm:py-8 lg:py-12">
        <div class="relative">
          <svg class="h-6 w-6 sm:h-8 sm:w-8 lg:h-12 lg:w-12 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div class="text-center px-3 sm:px-4">
          <h3 class="text-sm sm:text-base lg:text-lg font-semibold text-red-800 mb-1 sm:mb-2">Error al cargar casos urgentes</h3>
          <p class="text-xs sm:text-sm text-red-600 mb-3 sm:mb-4 max-w-sm mx-auto">{{ errorCarga }}</p>
          <button
            @click="cargarCasosUrgentesConFiltros"
            class="inline-flex items-center px-3 sm:px-4 py-1.5 sm:py-2 border border-red-300 text-red-700 bg-red-50 rounded-lg font-medium hover:bg-red-100 transition-colors text-xs sm:text-sm"
          >
            <svg class="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Intentar nuevamente
          </button>
        </div>
      </div>

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
                v-for="caso in casosPaginados" 
                :key="caso.codigo"
                class="hover:bg-gray-50"
              >
                <td class="px-1 py-2 sm:py-3 text-center">
                  <span class="font-medium text-gray-800 text-xs sm:text-sm">{{ caso.codigo }}</span>
                </td>
                
                <td class="px-1 sm:px-2 py-2 sm:py-3 text-center">
                  <div>
                    <p class="text-gray-800 text-xs sm:text-sm truncate">{{ caso.paciente.nombre }}</p>
                    <p class="text-gray-500 text-xs">{{ caso.paciente.cedula }}</p>
                  </div>
                </td>
                
                <td class="px-1 sm:px-2 py-2 sm:py-3 text-center">
                  <p class="text-gray-800 text-xs sm:text-sm truncate">{{ caso.paciente.entidad || 'Entidad' }}</p>
                  <p class="text-gray-500 text-xs truncate">{{ caso.patologo || 'No asignado' }}</p>
                </td>
                
                <td class="px-1 sm:px-3 py-2 sm:py-3 text-center">
                  <div class="flex flex-wrap gap-1 justify-center max-w-full">
                    <span
                      v-for="(g, idx) in groupTests(caso.pruebas).slice(0, 3)"
                      :key="idx"
                      class="test-badge inline-flex items-center justify-center bg-gray-100 text-gray-700 font-mono text-xs px-1.5 sm:px-2 py-0.5 sm:py-1 rounded border text-nowrap relative min-w-0 flex-shrink-0"
                      :title="getTestTooltip(caso.pruebas, g.code, g.count)"
                    >
                      <span class="truncate test-code">{{ extractTestCode(g.code) }}</span>
                      <sub v-if="g.count > 1" class="absolute right-0 bottom-0 translate-x-1/2 translate-y-1/2 text-[9px] sm:text-[10px] text-blue-600 font-bold">{{ g.count }}</sub>
                    </span>
                    <span
                      v-if="groupTests(caso.pruebas).length > 3"
                      class="inline-flex items-center justify-center bg-blue-50 text-blue-600 font-mono text-xs px-1.5 sm:px-2 py-0.5 sm:py-1 rounded border"
                      :title="`${groupTests(caso.pruebas).length - 3} pruebas más`"
                    >
                      +{{ groupTests(caso.pruebas).length - 3 }}
                    </span>
                  </div>
                </td>
                
                <td class="px-1 sm:px-2 py-2 sm:py-3 text-center">
                  <span class="inline-flex items-center justify-center rounded-full px-2 sm:px-3 py-0.5 sm:py-1 text-xs font-medium w-full" :class="statusClass(caso)">
                    {{ statusLabel(caso) }}
                  </span>
                  <p class="text-xs font-medium px-1.5 sm:px-2 py-0.5 rounded-full inline-block mt-1" :class="daysClass(caso)">
                    {{ caso.dias_en_sistema }} días
                  </p>
                </td>
                
                <td class="px-1 sm:px-2 py-2 sm:py-3 text-center">
                  <p class="text-gray-800 text-xs sm:text-sm">{{ formatDate(caso.fecha_creacion) }}</p>
                </td>
                
                <td class="px-1 sm:px-2 py-2 sm:py-3 text-center">
                  <div class="flex gap-1 justify-center min-w-[100px] sm:min-w-[120px]">
                    <button
                      class="p-1 sm:p-1.5 rounded-md hover:bg-gray-100 text-gray-600"
                      @click.stop="() => emit('show-details', caso)"
                      title="Ver detalles"
                    >
                      <svg class="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </button>
                    <button
                      v-if="!isPatologo && !isResidente"
                      class="p-1 sm:p-1.5 rounded-md hover:bg-gray-100 text-gray-600"
                      @click.stop="handleEdit(caso)"
                      title="Editar caso"
                    >
                      <svg class="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                    </button>
                    <button
                      v-if="caso.estado === 'En proceso'"
                      class="p-1 sm:p-1.5 rounded-md hover:bg-gray-100 text-gray-600"
                      @click.stop="handlePerform(caso)"
                      title="Realizar resultados"
                    >
                      <svg class="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                      </svg>
                    </button>
                    <button
                      v-if="['Por firmar','Por entregar'].includes(caso.estado)"
                      class="p-1 sm:p-1.5 rounded-md hover:bg-gray-100 text-gray-600"
                      @click.stop="handleValidate(caso)"
                      :title="caso.estado === 'Por firmar' ? 'Realizar validación del informe' : 'Validar'"
                    >
                      <svg v-if="caso.estado === 'Por firmar'" class="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
                      </svg>
                      <svg v-else class="w-3 h-3 sm:w-4 sm:h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
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
              v-for="caso in casosPaginados" 
              :key="caso.codigo"
              class="bg-white border border-gray-200 rounded-lg p-3 sm:p-4 hover:shadow-md transition-shadow"
            >
              <div class="flex items-start justify-between mb-2 sm:mb-3">
                <div class="flex-1 min-w-0">
                  <h4 class="font-semibold text-gray-800 text-xs sm:text-sm truncate">{{ caso.codigo }}</h4>
                  <p class="text-gray-600 text-xs mt-0.5 sm:mt-1 truncate">{{ caso.paciente.nombre }}</p>
                  <p class="text-gray-500 text-xs truncate">{{ caso.paciente.cedula }}</p>
                </div>
                <div class="flex-shrink-0 ml-2 sm:ml-3">
                  <span class="inline-flex items-center justify-center rounded-full px-1.5 sm:px-2 py-0.5 sm:py-1 text-xs font-medium" :class="statusClass(caso)">
                    {{ statusLabel(caso) }}
                  </span>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-2 sm:gap-3 mb-2 sm:mb-3 text-xs">
                <div>
                  <p class="text-gray-500">Entidad</p>
                  <p class="text-gray-800 font-medium truncate">{{ caso.paciente.entidad || 'Entidad' }}</p>
                </div>
                <div>
                  <p class="text-gray-500">Patólogo</p>
                  <p class="text-gray-800 font-medium truncate">{{ caso.patologo || 'No asignado' }}</p>
                </div>
                <div>
                  <p class="text-gray-500">Fecha creación</p>
                  <p class="text-gray-800 font-medium">{{ formatDate(caso.fecha_creacion) }}</p>
                </div>
                <div>
                  <p class="text-gray-500">Días en sistema</p>
                  <p class="text-gray-800 font-medium" :class="daysClass(caso)">
                    {{ caso.dias_en_sistema }} días
                  </p>
                </div>
              </div>

              <div class="mb-2 sm:mb-3">
                <p class="text-gray-500 text-xs mb-1 sm:mb-2">Pruebas</p>
                <div class="flex flex-wrap gap-1 justify-start">
                  <span
                    v-for="(g, idx) in groupTests(caso.pruebas).slice(0, 4)"
                    :key="idx"
                    class="test-badge inline-flex items-center justify-center bg-gray-100 text-gray-700 font-mono text-xs px-1.5 sm:px-2 py-0.5 sm:py-1 rounded border relative min-w-0 flex-shrink-0"
                    :title="getTestTooltip(caso.pruebas, g.code, g.count)"
                  >
                    <span class="truncate max-w-[50px] sm:max-w-[60px] test-code">{{ extractTestCode(g.code) }}</span>
                    <sub v-if="g.count > 1" class="absolute right-0 bottom-0 translate-x-1/2 translate-y-1/2 text-[9px] sm:text-[10px] text-blue-600 font-bold">{{ g.count }}</sub>
                  </span>
                  <span
                    v-if="groupTests(caso.pruebas).length > 4"
                    class="inline-flex items-center justify-center bg-blue-50 text-blue-600 font-mono text-xs px-1.5 sm:px-2 py-0.5 sm:py-1 rounded border"
                    :title="`${groupTests(caso.pruebas).length - 4} pruebas más`"
                  >
                    +{{ groupTests(caso.pruebas).length - 4 }}
                  </span>
                </div>
              </div>

              <div class="flex gap-1 sm:gap-2 pt-2 border-t border-gray-100">
                <button
                  class="flex-1 flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-3 py-1.5 sm:py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors text-xs font-medium"
                  @click.stop="() => emit('show-details', caso)"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span class="hidden xs:inline">Ver detalles</span>
                  <span class="xs:hidden">Ver</span>
                </button>
                <button
                  v-if="!isPatologo && !isResidente"
                  class="flex-1 flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-3 py-1.5 sm:py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors text-xs font-medium"
                  @click.stop="handleEdit(caso)"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Editar
                </button>
                <button
                  v-if="caso.estado === 'En proceso'"
                  class="flex-1 flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-3 py-1.5 sm:py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors text-xs font-medium"
                  @click.stop="handlePerform(caso)"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                  Realizar
                </button>
                <button
                  v-if="['Por firmar','Por entregar'].includes(caso.estado)"
                  class="flex-1 flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-3 py-1.5 sm:py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors text-xs font-medium"
                  @click.stop="handleValidate(caso)"
                >
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Validar
                </button>
              </div>
            </div>

            <div v-if="casosUrgentes.length === 0" class="text-center py-6 sm:py-8">
              <div class="flex flex-col items-center space-y-2">
                <svg class="w-8 h-8 sm:w-12 sm:h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div class="text-center">
                  <p class="text-gray-500 text-xs sm:text-sm font-medium">¡Excelente! No hay casos urgentes</p>
                  <p class="text-gray-400 text-xs mt-1">
                    {{ patologoSeleccionado ? 'Para el patólogo seleccionado' : 'En los últimos 1000 casos' }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="px-2 sm:px-4 lg:px-5 py-3 sm:py-4 border-t border-gray-200 bg-gray-50">
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4">
            <div class="flex items-center gap-1 sm:gap-2 text-xs sm:text-sm text-gray-500">
              <span class="hidden sm:inline">Mostrando</span>
              <select 
                :value="itemsPerPage" 
                @change="updateItemsPerPage" 
                class="h-7 sm:h-8 rounded-lg border border-gray-300 bg-white px-1.5 sm:px-2 py-0.5 sm:py-1 text-xs sm:text-sm text-gray-700"
              >
                <option v-for="option in itemsPerPageOptions" :key="option" :value="option">{{ option }}</option>
              </select>
              <span class="text-xs sm:text-sm">de {{ casosUrgentes.length }}</span>
            </div>
            
            <div class="flex items-center justify-center gap-1 sm:gap-2">
              <button 
                @click="goToPrevPage" 
                :disabled="currentPage === 1" 
                class="px-2 sm:px-3 py-1 sm:py-1.5 border rounded-lg text-xs sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
              >
                <span class="hidden sm:inline">Anterior</span>
                <span class="sm:hidden">←</span>
              </button>
              
              <div class="flex items-center gap-1 text-xs sm:text-sm text-gray-500">
                <span class="hidden sm:inline">Página</span>
                <span class="font-medium">{{ currentPage }}</span>
                <span class="hidden sm:inline">de</span>
                <span class="hidden sm:inline">{{ totalPages }}</span>
                <span class="sm:hidden">/ {{ totalPages }}</span>
              </div>
              
              <button 
                @click="goToNextPage" 
                :disabled="currentPage === totalPages" 
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

  </Card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Card } from '@/shared/components/layout'
import PathologistList from '@/shared/components/List/PathologistList.vue'
import { useDashboard } from '../composables/useDashboard'
import { usePermissions } from '@/shared/composables/usePermissions'
import type { CasoUrgente } from '../types/dashboard.types'
import type { FormPathologistInfo } from '@/modules/cases/types'

// Definir los eventos que emite el componente
const emit = defineEmits<{
  'show-details': [caso: CasoUrgente]
  'edit': [caso: CasoUrgente]
  'perform': [caso: CasoUrgente]
  'validate': [caso: CasoUrgente]
}>()

const { 
  casosUrgentes: casos,
  loadingCasosUrgentes: isLoading,
  error,
  cargarCasosUrgentes
} = useDashboard()

const router = useRouter()

// Permisos del usuario
const { isPatologo, isResidente } = usePermissions()

const errorCarga = error
const patologoSeleccionado = ref('')

const sortKey = ref('codigo')
const sortOrder = ref('desc')

const casosUrgentes = computed(() => {
  return casos.value.slice().sort((a, b) => {
    let aVal: any, bVal: any
    
    if (sortKey.value === 'codigo') {
      const getNumeroFromCodigo = (codigo: string): number => {
        const match = codigo.match(/(\d{4})-(\d{5})/)
        if (match) {
          const año = parseInt(match[1])
          const numero = parseInt(match[2])
          return año * 100000 + numero
        }
        return 0
      }
      aVal = getNumeroFromCodigo(a.codigo)
      bVal = getNumeroFromCodigo(b.codigo)
    } else if (sortKey.value === 'paciente') {
      aVal = a.paciente.nombre
      bVal = b.paciente.nombre
    } else if (sortKey.value === 'pruebas') {
      aVal = a.pruebas.join(', ')
      bVal = b.pruebas.join(', ')
    } else if (sortKey.value === 'patologo') {
      aVal = a.patologo
      bVal = b.patologo
    } else if (sortKey.value === 'fechaCreacion') {
      aVal = new Date(a.fecha_creacion)
      bVal = new Date(b.fecha_creacion)
    } else if (sortKey.value === 'diasSistema') {
      aVal = a.dias_en_sistema
      bVal = b.dias_en_sistema
    } else {
      aVal = a.estado
      bVal = b.estado
    }
    
    if (aVal == null) return 1
    if (bVal == null) return -1
    
    if (typeof aVal === 'string' && typeof bVal === 'string') {
      aVal = aVal.toLowerCase()
      bVal = bVal.toLowerCase()
    }
    
    if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1
    if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })
})

const itemsPerPageOptions = [10, 20, 50, 100]
const itemsPerPage = ref(10)
const currentPage = ref(1)

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(casosUrgentes.value.length / itemsPerPage.value))
})

const casosPaginados = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return casosUrgentes.value.slice(start, end)
})

function goToPrevPage() {
  if (currentPage.value > 1) currentPage.value--
}

function goToNextPage() {
  if (currentPage.value < totalPages.value) currentPage.value++
}

function updateItemsPerPage(event: Event) {
  const val = Number((event.target as HTMLSelectElement).value)
  itemsPerPage.value = val
  currentPage.value = 1
}

watch([casosUrgentes, itemsPerPage], () => {
  currentPage.value = 1
})

watch(patologoSeleccionado, (newValue) => {
  // Solo cargar si el valor ha cambiado realmente
  if (newValue !== undefined) {
    cargarCasosUrgentesConFiltros()
  }
})

async function cargarCasosUrgentesConFiltros() {
  const filtros = {
    patologo: patologoSeleccionado.value || undefined,
  }
  
  // Debug temporal
  console.log('=== FILTRO PATOLOGO ===')
  console.log('Patólogo seleccionado:', patologoSeleccionado.value)
  console.log('Filtros enviados:', filtros)
  console.log('=====================')
  
  await cargarCasosUrgentes(filtros)
}

function onPathologistSelected(pathologist: FormPathologistInfo | null) {
  // Actualizar el valor seleccionado con el documento del patólogo
  patologoSeleccionado.value = pathologist?.documento || ''
  cargarCasosUrgentesConFiltros()
}

function onPathologistLoadError(error: string) {
}

const columnasDesktop = [
  { key: 'codigo', label: 'Código', class: 'w-[12%]' },
  { key: 'paciente', label: 'Paciente', class: 'w-[18%]' },
  { key: 'entidad', label: 'Entidad/Patólogo', class: 'w-[15%]' },
  { key: 'pruebas', label: 'Pruebas', class: 'w-[28%]' },
  { key: 'estado', label: 'Estado/Días', class: 'w-[12%]' },
  { key: 'fechaCreacion', label: 'Fecha de creación', class: 'w-[10%]' },
  { key: 'acciones', label: 'Acciones', class: 'w-[15%]' }
]

const sortBy = (key: string) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

function formatDate(dateString: string) {
  if (!dateString) return 'N/A'
  const d = new Date(dateString)
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function extractTestCode(testString: string) {
  const match = testString.match(/^\d{6}/)
  return match ? match[0] : testString.split(' ')[0]
}

function groupTests(tests: string[]): { code: string; count: number }[] {
  const groups: Record<string, number> = {}
  tests.forEach(t => {
    const code = extractTestCode(t)
    groups[code] = (groups[code] || 0) + 1
  })
  return Object.entries(groups).map(([code, count]) => ({ code, count }))
}

function getTestTooltip(tests: string[], code: string, count: number): string {
  const normalizedCode = extractTestCode(code)
  const matching = tests.filter(t => extractTestCode(t) === normalizedCode)
  const names = matching
    .map(t => (t.includes(' - ') ? t.split(' - ').slice(1).join(' - ') : t))
    .filter(Boolean)
  const uniqueNames = Array.from(new Set(names))
  const nameStr = uniqueNames.length ? uniqueNames.join(', ') : `Código ${normalizedCode}`
  return `${nameStr} • ${count} vez${count > 1 ? 'es' : ''}`
}

function statusLabel(caso: CasoUrgente): string {
  const days = caso.dias_en_sistema
  if (caso.estado === 'Por entregar') return 'Por entregar'
  if (days > 6 && caso.estado !== 'Completado') return 'URGENTE'
  return caso.estado
}

function statusClass(caso: CasoUrgente): string {
  const days = caso.dias_en_sistema
  if (caso.estado === 'Por entregar') return 'bg-red-50 text-red-700 font-semibold'
  if (days > 6 && caso.estado !== 'Completado') return 'bg-red-50 text-red-700 font-semibold'
  if (caso.estado === 'Por firmar') return 'bg-yellow-50 text-yellow-700'
  // 'Por entregar' deprecado -> tratar como 'Requiere cambios'
  if (caso.estado === 'Por entregar') return 'bg-red-50 text-red-700'
  if (caso.estado === 'En proceso') return 'bg-blue-50 text-blue-700'
  if (caso.estado === 'Completado') return 'bg-green-50 text-green-700'
  return ''
}

function daysClass(caso: CasoUrgente): string {
  const days = caso.dias_en_sistema
  if (days > 6 && caso.estado !== 'Completado') return 'bg-red-50 text-red-700'
  return 'bg-blue-50 text-blue-700'
}

function handleEdit(caso: CasoUrgente) {
  emit('edit', caso)
  router.push(`/cases/edit/${caso.codigo}`)
}

function handlePerform(caso: CasoUrgente) {
  emit('perform', caso)
  router.push(`/results/perform?case=${caso.codigo}&auto=1`)
}

function handleValidate(caso: CasoUrgente) {
  emit('validate', caso)
  router.push(`/results/sign?case=${caso.codigo}&auto=1`)
}

onMounted(() => {
  cargarCasosUrgentesConFiltros()
})
</script>

<style scoped>
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.custom-scrollbar::-webkit-scrollbar {
  height: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #555;
}

@media (min-width: 640px) {
  .custom-scrollbar::-webkit-scrollbar {
    height: 6px;
  }
}

@media (hover: none) and (pointer: coarse) {
  .hover\:bg-gray-50:hover,
  .hover\:shadow-md:hover,
  .hover\:bg-green-50:hover,
  .hover\:bg-blue-50:hover,
  .hover\:bg-purple-50:hover,
  .hover\:bg-orange-50:hover {
    background-color: transparent;
    box-shadow: none;
  }
}

.transition-shadow {
  transition: box-shadow 0.2s ease-in-out;
}

.transition-colors {
  transition: color 0.2s ease-in-out, background-color 0.2s ease-in-out;
}

button:focus-visible,
select:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

.test-code {
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  line-height: 1;
}

.test-badge {
  transition: all 0.2s ease-in-out;
}

.test-badge:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

@media (max-width: 480px) {
  .xs\:hidden {
    display: none;
  }
  
  .xs\:inline {
    display: inline;
  }
}

@media (min-width: 481px) {
  .xs\:hidden {
    display: inline;
  }
  
  .xs\:inline {
    display: none;
  }
}
</style>