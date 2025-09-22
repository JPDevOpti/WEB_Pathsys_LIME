<template>
  <div v-if="estaBuscando || busquedaRealizada">
    <h4 class="text-base font-semibold text-gray-800 mb-1">Resultados</h4>
    
    <div v-if="estaBuscando" class="text-sm text-gray-500 text-center py-4">
      <div class="inline-flex items-center">
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Buscando...
      </div>
    </div>
    
    <div v-else-if="resultados.length === 0 && busquedaRealizada" class="text-sm text-gray-500 text-center py-4">
      Sin resultados para tu búsqueda
    </div>
    
    <div v-else-if="resultados.length > 0" class="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 rounded-lg">
      <table class="min-w-full divide-y divide-gray-300">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-3 md:px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Nombre
            </th>
            <th scope="col" class="px-3 md:px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Tipo
            </th>
            <th scope="col" class="hidden sm:table-cell px-3 md:px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Código
            </th>
            <th scope="col" class="px-3 md:px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Estado
            </th>
            <th scope="col" class="relative px-3 md:px-4 py-2">
              <span class="sr-only">Seleccionar</span>
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr 
            v-for="r in resultados" 
            :key="r.id"
            class="cursor-pointer transition-colors"
            :class="r.id === selectedId 
              ? 'bg-blue-50 ring-2 ring-blue-400' 
              : 'hover:bg-gray-50'"
            @click="$emit('usuario-seleccionado', r)"
          >
            <td class="px-3 md:px-4 py-3 whitespace-nowrap">
              <div class="flex items-center">
                <div>
                  <div class="text-sm font-medium text-gray-900">
                    {{ r.nombre }}
                  </div>
                  <div class="sm:hidden text-xs text-gray-500">
                    {{ r.documento || r.nit || r.codigo || '-' }}
                  </div>
                </div>
              </div>
            </td>
            <td class="px-3 md:px-4 py-3 whitespace-nowrap">
              <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                :class="{
                  'bg-blue-100 text-blue-800': r.tipo === 'auxiliar',
                  'bg-green-100 text-green-800': r.tipo === 'patologo',
                  'bg-yellow-100 text-yellow-800': r.tipo === 'residente',
                  'bg-purple-100 text-purple-800': r.tipo === 'entidad',
                  'bg-orange-100 text-orange-800': r.tipo === 'pruebas'
                }">
                <span class="md:hidden">
                  {{ r.tipo === 'auxiliar' ? 'Aux' : 
                     r.tipo === 'patologo' ? 'Pat' : 
                     r.tipo === 'residente' ? 'Res' :
                     r.tipo === 'entidad' ? 'Ent' : 'Pru' }}
                </span>
                <span class="hidden md:inline">
                  {{ r.tipo === 'auxiliar' ? 'Auxiliar' : 
                     r.tipo === 'patologo' ? 'Patólogo' : 
                     r.tipo === 'residente' ? 'Residente' :
                     r.tipo === 'entidad' ? 'Entidad' : 'Pruebas' }}
                </span>
              </span>
            </td>
            <td class="hidden sm:table-cell px-3 md:px-4 py-3 whitespace-nowrap text-sm text-gray-500">
              {{ r.documento || r.nit || r.codigo || '-' }}
            </td>
            <td class="px-3 md:px-4 py-3 whitespace-nowrap">
              <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                :class="r.activo ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                <span class="md:hidden">{{ r.activo ? '✓' : '✗' }}</span>
                <span class="hidden md:inline">{{ r.activo ? 'Activo' : 'Inactivo' }}</span>
              </span>
            </td>
            <td class="px-3 md:px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ resultados: any[]; busquedaRealizada: boolean; estaBuscando: boolean; selectedId?: string }>()
defineEmits<{ (e: 'usuario-seleccionado', item: any): void }>()
</script>


