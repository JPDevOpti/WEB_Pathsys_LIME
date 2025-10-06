<template>
  <transition enter-active-class="transition ease-out duration-300" enter-from-class="opacity-0 transform scale-95" enter-to-class="opacity-100 transform scale-100" leave-active-class="transition ease-in duration-200" leave-from-class="opacity-100 transform scale-100" leave-to-class="opacity-0 transform scale-95">
    <div
      v-if="visible"
      :class="[
        'fixed right-0 bottom-0 z-[10000] flex items-end sm:items-center justify-center p-2 sm:p-4 bg-black/40',
        'top-16',
        overlayLeftClass
      ]"
      @click.self="emit('close')"
    >
      <!-- Contenedor -->
      <div class="relative bg-white w-full max-w-3xl rounded-t-2xl sm:rounded-2xl shadow-2xl h-[75vh] sm:h-auto sm:max-h-[90vh] flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-200 bg-white">
          <h3 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Marcar técnicas como completadas
          </h3>
          <button @click="emit('close')" class="text-gray-400 hover:text-gray-600 transition-colors">✕</button>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-5 space-y-6">
          <div>
            <h4 class="text-sm font-semibold text-gray-700 mb-3">Técnicas Seleccionadas ({{ techniques.length }})</h4>
            <ul class="divide-y divide-gray-200 border border-gray-200 rounded-md overflow-hidden text-sm">
              <li
                v-for="t in techniques"
                :key="t.id"
                class="group bg-white focus-within:bg-blue-50/50"
              >
                <button
                  type="button"
                  class="w-full px-3 py-2 flex items-center gap-3 text-left hover:bg-blue-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/60 transition-colors"
                  @click="toggleExpanded(t.id)"
                  :aria-expanded="isExpanded(t.id) ? 'true' : 'false'"
                >
                  <span class="inline-flex items-center justify-center w-5 h-5 rounded border border-gray-300 text-[10px] font-medium text-gray-500 bg-white flex-shrink-0">
                    {{ indexOfTechnique(t.id) + 1 }}
                  </span>
                  <div class="flex-1 min-w-0">
                    <p class="font-medium text-gray-800 truncate flex items-center gap-2">
                      <span class="font-mono">{{ t.caseCode || t.id }}</span>
                      <span
                        v-if="t.isSpecialCase"
                        class="inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold bg-orange-50 text-orange-700"
                      >
                        Caso Especial
                      </span>
                    </p>
                    <p class="text-gray-500 text-xs truncate">{{ t.patientName || (t.isSpecialCase ? 'Caso Especial' : 'Sin nombre') }}</p>
                  </div>
                  <svg
                    class="w-4 h-4 text-gray-500 transition-transform duration-200 flex-shrink-0"
                    :class="{ 'rotate-90': isExpanded(t.id) }"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>

                <transition
                  enter-active-class="overflow-hidden transition-all duration-300 ease-out"
                  enter-from-class="max-h-0 opacity-0"
                  enter-to-class="max-h-[600px] opacity-100"
                  leave-active-class="overflow-hidden transition-all duration-200 ease-in"
                  leave-from-class="max-h-[600px] opacity-100"
                  leave-to-class="max-h-0 opacity-0"
                >
                  <div v-if="isExpanded(t.id)" class="px-4 pb-4 pt-1 bg-gray-50/60 border-t border-gray-200 space-y-4">
                    <!-- Información general -->
                    <div class="bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
                      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        <div>
                          <p class="text-[10px] font-medium text-gray-500 uppercase tracking-wide">Institución</p>
                          <p class="text-[11px] font-semibold text-gray-800 truncate">{{ t.institution || '—' }}</p>
                        </div>
                        <div>
                          <p class="text-[10px] font-medium text-gray-500 uppercase tracking-wide">N° Placas</p>
                          <p class="text-[11px] font-semibold text-gray-800">{{ t.numberOfPlates || 0 }}</p>
                        </div>
                        <div>
                          <p class="text-[10px] font-medium text-gray-500 uppercase tracking-wide">Fecha ingreso</p>
                          <p class="text-[11px] font-semibold text-gray-800">{{ formatDate(t.entryDate) }}</p>
                        </div>
                      </div>
                    </div>

                    <!-- Pruebas realizadas -->
                    <div v-if="t.testGroups && t.testGroups.length > 0">
                      <p class="text-[11px] uppercase tracking-wide font-semibold text-gray-500 mb-2">Pruebas Realizadas</p>
                      <div class="space-y-2">
                        <div 
                          v-for="(group, gIdx) in t.testGroups" 
                          :key="gIdx"
                          :class="['rounded-lg p-3 border', getTestGroupColorClass(group.type)]"
                        >
                          <div class="flex items-center justify-between mb-2">
                            <p :class="['text-xs font-semibold', getTestGroupTextClass(group.type)]">
                              {{ getTestTypeLabel(group.type) }}
                            </p>
                            <span :class="['px-2 py-0.5 text-[10px] font-bold rounded', getTestGroupBadgeClass(group.type)]">
                              {{ getTotalQuantity(group.tests) }} {{ getTotalQuantity(group.tests) === 1 ? 'placa' : 'placas' }}
                            </span>
                          </div>
                          <div class="flex flex-wrap gap-1">
                            <span 
                              v-for="(test, tIdx) in group.tests" 
                              :key="tIdx"
                              :class="['inline-flex items-center bg-white/50 font-mono text-[11px] px-2 py-1 rounded border-2 relative', getTestBadgeBorderClass(group.type)]"
                              :title="test.name || test.code"
                            >
                              {{ test.code }}
                              <sub v-if="test.quantity > 1" :class="['absolute -top-1 -right-1 w-4 h-4 rounded-full flex items-center justify-center text-[9px] font-bold', getTestCountBadgeClass(group.type)]">
                                {{ test.quantity }}
                              </sub>
                            </span>
                          </div>
                          <p v-if="group.observations" class="text-[11px] italic text-gray-600 mt-2 pt-2 border-t border-current/20">
                            <svg class="w-3 h-3 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            {{ group.observations }}
                          </p>
                        </div>
                      </div>
                    </div>

                    <!-- Nota especial -->
                    <div v-if="t.notes" class="p-2 bg-yellow-50 border border-yellow-200 rounded text-xs">
                      <p class="text-yellow-800"><strong>Nota:</strong> {{ t.notes }}</p>
                    </div>
                  </div>
                </transition>
              </li>
            </ul>
          </div>
        </div>

        <!-- Footer actions -->
        <div class="px-5 py-4 border-t border-gray-200 bg-gray-50 space-y-3">
          <!-- Campo "Entregado a" -->
          <div>
            <label for="entregado-a" class="block text-sm font-medium text-gray-700 mb-2">
              Entregado a
            </label>
            <input
              id="entregado-a"
              v-model="entregadoA"
              type="text"
              maxlength="100"
              placeholder="Nombre de la persona que recibe las técnicas..."
              class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              :class="{ 'border-red-300 focus:ring-red-500 focus:border-red-500': entregadoAError }"
            />
            <div class="flex justify-between items-center mt-1">
              <p v-if="entregadoAError" class="text-red-600 text-xs">{{ entregadoAError }}</p>
              <p class="text-gray-500 text-xs ml-auto">{{ entregadoA.length }}/100</p>
            </div>
          </div>

          <!-- Botones de acción -->
          <div class="flex flex-col sm:flex-row justify-end gap-2">
            <button
              @click="emit('close')"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <button
              @click="emitConfirm"
              :disabled="techniques.length === 0 || !entregadoA.trim()"
              class="px-4 py-2 text-sm font-medium text-green-600 bg-transparent border-2 border-green-600 rounded-lg hover:bg-green-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Confirmar ({{ techniques.length }})
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ComplementaryTechnique } from '../../types'
import { useSidebar } from '@/shared/composables/SidebarControl'

interface Props {
  modelValue: boolean
  selected: ComplementaryTechnique[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'close'): void
  (e: 'completed', techniques: ComplementaryTechnique[]): void
}>()

const visible = computed(() => props.modelValue)
const techniques = computed(() => props.selected || [])

const expandedIds = ref<Set<string>>(new Set())
const entregadoA = ref('')
const entregadoAError = ref('')

const toggleExpanded = (id: string) => {
  if (!id) return
  if (expandedIds.value.has(id)) {
    expandedIds.value.delete(id)
  } else {
    expandedIds.value.add(id)
  }
  expandedIds.value = new Set(expandedIds.value)
}

const isExpanded = (id: string): boolean => {
  return expandedIds.value.has(id)
}

const indexOfTechnique = (id: string): number => {
  return techniques.value.findIndex(t => t.id === id)
}

const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A'
  const d = new Date(dateString)
  if (isNaN(d.getTime())) return 'N/A'
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const { isExpanded: sidebarExpanded, isMobileOpen, isHovered } = useSidebar()
const overlayLeftClass = computed(() => {
  const hasWideSidebar = (sidebarExpanded.value && !isMobileOpen.value) || (!sidebarExpanded.value && isHovered.value)
  return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})

const emitConfirm = () => {
  entregadoAError.value = ''
  if (!entregadoA.value.trim()) {
    entregadoAError.value = 'Este campo es requerido'
    return
  }
  if (entregadoA.value.length > 100) {
    entregadoAError.value = 'Máximo 100 caracteres'
    return
  }

  // Actualizar técnicas con fecha y persona de entrega
  const updatedTechniques = techniques.value.map(t => ({
    ...t,
    deliveredTo: entregadoA.value.trim(),
    deliveryDate: new Date().toISOString(),
    status: 'Completado',
    updatedAt: new Date().toISOString()
  }))

  emit('completed', updatedTechniques)
  emit('update:modelValue', false)
  entregadoA.value = ''
  entregadoAError.value = ''
}

// Helper functions para colores de badges
const getTestTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    'LOW_COMPLEXITY_IHQ': 'IHQ Baja Complejidad',
    'HIGH_COMPLEXITY_IHQ': 'IHQ Alta Complejidad',
    'SPECIAL_IHQ': 'IHQ Especiales',
    'HISTOCHEMISTRY': 'Histoquímicas'
  }
  return labels[type] || type
}

const getTestGroupColorClass = (type: string) => {
  const classes: Record<string, string> = {
    'LOW_COMPLEXITY_IHQ': 'bg-blue-50 border-blue-200',
    'HIGH_COMPLEXITY_IHQ': 'bg-purple-50 border-purple-200',
    'SPECIAL_IHQ': 'bg-orange-50 border-orange-200',
    'HISTOCHEMISTRY': 'bg-green-50 border-green-200'
  }
  return classes[type] || 'bg-gray-50 border-gray-200'
}

const getTestGroupTextClass = (type: string) => {
  const classes: Record<string, string> = {
    'LOW_COMPLEXITY_IHQ': 'text-blue-900',
    'HIGH_COMPLEXITY_IHQ': 'text-purple-900',
    'SPECIAL_IHQ': 'text-orange-900',
    'HISTOCHEMISTRY': 'text-green-900'
  }
  return classes[type] || 'text-gray-900'
}

const getTestGroupBadgeClass = (type: string) => {
  const classes: Record<string, string> = {
    'LOW_COMPLEXITY_IHQ': 'bg-blue-100 text-blue-800',
    'HIGH_COMPLEXITY_IHQ': 'bg-purple-100 text-purple-800',
    'SPECIAL_IHQ': 'bg-orange-100 text-orange-800',
    'HISTOCHEMISTRY': 'bg-green-100 text-green-800'
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const getTestBadgeBorderClass = (type: string) => {
  const classes: Record<string, string> = {
    'LOW_COMPLEXITY_IHQ': 'border-blue-300',
    'HIGH_COMPLEXITY_IHQ': 'border-purple-300',
    'SPECIAL_IHQ': 'border-orange-300',
    'HISTOCHEMISTRY': 'border-green-300'
  }
  return classes[type] || 'border-gray-300'
}

const getTestCountBadgeClass = (type: string) => {
  const classes: Record<string, string> = {
    'LOW_COMPLEXITY_IHQ': 'bg-blue-200 text-blue-800',
    'HIGH_COMPLEXITY_IHQ': 'bg-purple-200 text-purple-800',
    'SPECIAL_IHQ': 'bg-orange-200 text-orange-800',
    'HISTOCHEMISTRY': 'bg-green-200 text-green-800'
  }
  return classes[type] || 'bg-gray-200 text-gray-800'
}

const getTotalQuantity = (tests: Array<{ quantity: number }>) => {
  return tests.reduce((sum, test) => sum + (test.quantity || 0), 0)
}
</script>

<style scoped>
</style>
