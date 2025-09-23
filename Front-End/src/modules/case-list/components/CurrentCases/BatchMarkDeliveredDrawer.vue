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
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Marcar casos como entregados
          </h3>
          <button @click="emit('close')" class="text-gray-400 hover:text-gray-600 transition-colors">✕</button>
        </div>

        <!-- Content (placeholder for now) -->
        <div class="flex-1 overflow-y-auto p-5 space-y-6">
          <div>
            <h4 class="text-sm font-semibold text-gray-700 mb-3">Casos Seleccionados (click para ver detalles)</h4>
            <ul class="divide-y divide-gray-200 border border-gray-200 rounded-md overflow-hidden text-sm">
              <li
                v-for="c in cases"
                :key="c.id"
                class="group bg-white focus-within:bg-blue-50/50"
              >
                <!-- Header item clickable -->
                <button
                  type="button"
                  class="w-full px-3 py-2 flex items-center gap-3 text-left hover:bg-blue-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/60 transition-colors"
                  @click="toggleExpanded(c.id)"
                  :aria-expanded="isExpanded(c.id) ? 'true' : 'false'"
                >
                  <span class="inline-flex items-center justify-center w-5 h-5 rounded border border-gray-300 text-[10px] font-medium text-gray-500 bg-white flex-shrink-0">
                    {{ indexOfCase(c.id) + 1 }}
                  </span>
                  <div class="flex-1 min-w-0">
                    <p class="font-medium text-gray-800 truncate flex items-center gap-2">
                      {{ c.caseCode || c.id }}
                      <span
                        v-if="c.priority"
                        class="inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold"
                        :class="{
                          'bg-green-50 text-green-700': c.priority === 'Normal',
                          'bg-yellow-50 text-yellow-700': c.priority === 'Prioritario',
                          'bg-red-50 text-red-700': c.priority === 'Urgente'
                        }"
                      >{{ c.priority }}</span>
                    </p>
                    <p class="text-gray-500 text-xs truncate">{{ c.patient.fullName }}</p>
                  </div>
                  <svg
                    class="w-4 h-4 text-gray-500 transition-transform duration-200 flex-shrink-0"
                    :class="{ 'rotate-90': isExpanded(c.id) }"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>

                <!-- Details panel -->
                <transition
                  enter-active-class="overflow-hidden transition-all duration-300 ease-out"
                  enter-from-class="max-h-0 opacity-0"
                  enter-to-class="max-h-[600px] opacity-100"
                  leave-active-class="overflow-hidden transition-all duration-200 ease-in"
                  leave-from-class="max-h-[600px] opacity-100"
                  leave-to-class="max-h-0 opacity-0"
                >
                  <div v-if="isExpanded(c.id)" class="px-4 pb-4 pt-1 bg-gray-50/60 border-t border-gray-200 space-y-4">
                    <!-- Metadata Card (Entidad, Patólogo, Fecha Creación, Oportunidad) -->
                    <div class="bg-white border border-gray-200 rounded-lg p-3 shadow-sm">
                      <div class="grid grid-cols-1 sm:grid-cols-4 gap-3">
                        <div>
                          <p class="text-[10px] font-medium text-gray-500 uppercase tracking-wide">Entidad</p>
                          <p class="text-[11px] font-semibold text-gray-800 truncate">{{ c.entity || '—' }}</p>
                        </div>
                        <div>
                          <p class="text-[10px] font-medium text-gray-500 uppercase tracking-wide">Patólogo</p>
                          <p class="text-[11px] font-semibold text-gray-800 truncate">{{ c.pathologist || 'Sin asignar' }}</p>
                        </div>
                        <div>
                          <p class="text-[10px] font-medium text-gray-500 uppercase tracking-wide">Fecha creación</p>
                          <p class="text-[11px] font-semibold text-gray-800">{{ c.receivedAt ? formatDate(c.receivedAt) : 'N/A' }}</p>
                        </div>
                        <div>
                          <p class="text-[10px] font-medium text-blue-600 uppercase tracking-wide">Oportunidad</p>
                          <p class="text-[11px] font-bold text-blue-700 bg-blue-50 px-2 py-1 rounded" :title="`${calculateBusinessDays(c.receivedAt || '')} días hábiles transcurridos`">
                            {{ calculateBusinessDays(c.receivedAt || '') }} días
                          </p>
                        </div>
                      </div>
                    </div>

                    <!-- Submuestras y pruebas -->
                    <div>
                      <p class="text-[11px] uppercase tracking-wide font-semibold text-gray-500 mb-2">Submuestras</p>
                      <div v-if="c.subsamples && c.subsamples.length" class="space-y-3">
                        <div
                          v-for="(s, sIdx) in c.subsamples"
                          :key="sIdx"
                          class="relative bg-white border border-gray-200 rounded-lg p-3 shadow-sm group/sub overflow-hidden"
                          :class="{ 'opacity-60': isSubsampleRemoved(c.id, sIdx) }"
                        >
                          <!-- Botón remover submuestra (más grande) -->
                          <button
                            type="button"
                            class="absolute top-1.5 right-1.5 w-6 h-6 flex items-center justify-center rounded-full text-gray-400 hover:text-red-600 hover:bg-red-100/70 active:scale-95 transition text-sm font-bold border border-transparent hover:border-red-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-red-400/60"
                            :title="isSubsampleRemoved(c.id, sIdx) ? 'Restaurar submuestra' : 'Marcar submuestra para eliminar'"
                            @click.stop="toggleRemoveSubsample(c.id, sIdx)"
                          >
                            <span v-if="!isSubsampleRemoved(c.id, sIdx)">×</span>
                            <span v-else class="text-[11px]">↺</span>
                          </button>
                          <div class="flex items-center justify-between mb-2 pr-8">
                            <p class="text-xs font-semibold text-gray-700 max-w-full truncate" :class="{ 'line-through': isSubsampleRemoved(c.id, sIdx) }">
                              {{ s.bodyRegion || 'Sin región' }}
                            </p>
                            <span v-if="isSubsampleRemoved(c.id, sIdx)" class="text-[10px] font-medium text-red-600 bg-red-50 px-2 py-0.5 rounded-full flex-shrink-0">Eliminada</span>
                          </div>
                          <div class="flex flex-wrap gap-1">
                            <span
                              v-for="(t, tIdx) in getExpandedTestsCached(c.id, sIdx, s.tests || [])"
                              :key="tIdx"
                              class="relative inline-flex items-center bg-gray-100 text-gray-700 font-mono text-[11px] pl-2 pr-6 py-0.5 rounded border"
                              :class="{ 'opacity-40 line-through': isTestRemoved(c.id, sIdx, tIdx) || isSubsampleRemoved(c.id, sIdx) }"
                              :title="t.name && t.name !== t.id ? t.name : ''"
                            >
                              <span class="truncate max-w-[90px]">{{ t.id }}</span>
                              <button
                                type="button"
                                class="absolute top-0.5 right-0.5 w-5 h-5 flex items-center justify-center rounded-full text-gray-400 hover:text-red-600 hover:bg-red-100/80 active:scale-95 transition text-[11px] font-bold border border-transparent hover:border-red-300"
                                :title="isTestRemoved(c.id, sIdx, tIdx) ? 'Restaurar prueba' : 'Marcar prueba para eliminar'"
                                @click.stop="toggleRemoveTest(c.id, sIdx, tIdx)"
                                :disabled="isSubsampleRemoved(c.id, sIdx)"
                              >
                                <span v-if="!isTestRemoved(c.id, sIdx, tIdx)">×</span>
                                <span v-else class="font-bold">↺</span>
                              </button>
                            </span>
                          </div>
                        </div>
                      </div>
                      <p v-else class="text-xs text-gray-500 italic">Sin submuestras registradas</p>
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
              placeholder="Nombre de la persona que recibe los casos..."
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
            <BaseButton size="sm" variant="outline" @click="emit('close')">Cancelar</BaseButton>
            <BaseButton 
              size="sm" 
              variant="primary" 
              :disabled="cases.length === 0 || !entregadoA.trim()" 
              @click="emitConfirm"
            >
              Confirmar ({{ cases.length }})
            </BaseButton>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Case } from '../../types/case.types'
import { BaseButton } from '@/shared/components'
import { useSidebar } from '@/shared/composables/SidebarControl'
import { casesApiService } from '@/modules/cases/services'

interface Props {
  modelValue: boolean
  selected: Case[]
}

const props = defineProps<Props>()
const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void; (e: 'close'): void; (e: 'confirm', ids: string[]): void; (e: 'confirm-removals', summary: any): void; (e: 'completed', result: any[]): void }>()

const visible = computed(() => props.modelValue)
const cases = computed(() => props.selected || [])

// Estado de paneles expandidos
const expandedIds = ref<Set<string>>(new Set())

// Campo "Entregado a"
const entregadoA = ref('')
const entregadoAError = ref('')

function toggleExpanded(id: string) {
  if (!id) return
  if (expandedIds.value.has(id)) {
    expandedIds.value.delete(id)
  } else {
    expandedIds.value.add(id)
  }
  // Forzar reactividad recreando el Set
  expandedIds.value = new Set(expandedIds.value)
}

function isExpanded(id: string): boolean {
  return expandedIds.value.has(id)
}

function indexOfCase(id: string): number {
  return cases.value.findIndex(c => c.id === id)
}

function formatDate(dateString: string) {
  if (!dateString) return 'N/A'
  const d = new Date(dateString)
  if (isNaN(d.getTime())) return 'N/A'
  return d.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

// ================= Eliminaciones diferidas =================
// Estructura: removedSubsamples[caseId] = Set<subsampleIndex>
const removedSubsamples = ref<Record<string, Set<number>>>({})
// removedTests[caseId] = { [subsampleIndex]: Set<testIndex> }
const removedTests = ref<Record<string, Record<number, Set<number>>>>({})

function ensureCaseStructures(caseId: string) {
  if (!removedSubsamples.value[caseId]) removedSubsamples.value[caseId] = new Set()
  if (!removedTests.value[caseId]) removedTests.value[caseId] = {}
}

function toggleRemoveSubsample(caseId: string, subsampleIndex: number) {
  ensureCaseStructures(caseId)
  const set = removedSubsamples.value[caseId]
  if (set.has(subsampleIndex)) {
    set.delete(subsampleIndex)
  } else {
    set.add(subsampleIndex)
  }
  // Si se remueve submuestra, limpiar pruebas marcadas de esa submuestra
  if (removedTests.value[caseId] && removedTests.value[caseId][subsampleIndex]) {
    delete removedTests.value[caseId][subsampleIndex]
  }
  // Forzar reactividad
  removedSubsamples.value = { ...removedSubsamples.value }
  removedTests.value = { ...removedTests.value }
}

function isSubsampleRemoved(caseId: string, subsampleIndex: number): boolean {
  return !!removedSubsamples.value[caseId]?.has(subsampleIndex)
}

function toggleRemoveTest(caseId: string, subsampleIndex: number, testIndex: number) {
  ensureCaseStructures(caseId)
  if (isSubsampleRemoved(caseId, subsampleIndex)) return // Si submuestra completa marcada, ignorar
  if (!removedTests.value[caseId][subsampleIndex]) removedTests.value[caseId][subsampleIndex] = new Set()
  const set = removedTests.value[caseId][subsampleIndex]
  if (set.has(testIndex)) {
    set.delete(testIndex)
  } else {
    set.add(testIndex)
  }
  removedTests.value = { ...removedTests.value }
}

function isTestRemoved(caseId: string, subsampleIndex: number, testIndex: number): boolean {
  return !!removedTests.value[caseId]?.[subsampleIndex]?.has(testIndex)
}

// Construir payload de confirmación incluyendo info de removidos
function buildRemovalSummary() {
  return cases.value.map(c => {
    const subsRemoved = Array.from(removedSubsamples.value[c.id] || [])
    const testsRemoved = Object.entries(removedTests.value[c.id] || {}).map(([sIdx, set]) => ({
      subsampleIndex: Number(sIdx),
      tests: Array.from(set)
    }))
    return {
      caseId: c.id,
      removedSubsamples: subsRemoved,
      removedTests: testsRemoved
    }
  }).filter(entry => entry.removedSubsamples.length > 0 || entry.removedTests.length > 0)
}

// Centrado adaptado al ancho del sidebar (igual que CaseDetailsModal)
const { isExpanded: sidebarExpanded, isMobileOpen, isHovered } = useSidebar()
const overlayLeftClass = computed(() => {
  const hasWideSidebar = (sidebarExpanded.value && !isMobileOpen.value) || (!sidebarExpanded.value && isHovered.value)
  return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})

function emitConfirm() {
  // Validar campo "Entregado a"
  entregadoAError.value = ''
  if (!entregadoA.value.trim()) {
    entregadoAError.value = 'Este campo es requerido'
    return
  }
  if (entregadoA.value.length > 100) {
    entregadoAError.value = 'Máximo 100 caracteres'
    return
  }


  const ids = cases.value.map(c => c.id).filter(Boolean)
  // Emitir primero ids (compatibilidad)
  emit('confirm', ids)
  // Emitir evento adicional opcional con detalle (si se decide usar después)
  // @ts-ignore (evento extendido posible a futuro)
  emit('confirm-removals', buildRemovalSummary())
  
  // Construir payload de casos a completar con muestras restantes
  const batchPayload = cases.value.map(c => {
    const subs = c.subsamples || []
    const remaining = subs
      .filter((_, sIdx) => !isSubsampleRemoved(c.id, sIdx))
      .map((s, sIdx) => {
        // Expandir pruebas según cantidad para permitir eliminación individual
        const expanded = getExpandedTestsCached(c.id, sIdx, s.tests || [])
        const remainingExpanded = expanded.filter((_t, eIdx: number) => !isTestRemoved(c.id, sIdx, eIdx))
        // Reagrupar por id para enviar payload correcto (cantidad ajustada)
        const grouped: Record<string, { id: string; nombre: string; cantidad: number }> = {}
        for (const t of remainingExpanded) {
          if (!grouped[t.id]) {
            grouped[t.id] = { id: t.id, nombre: t.name || t.id, cantidad: 1 }
          } else {
            grouped[t.id].cantidad += 1
          }
        }
        return {
          body_region: s.bodyRegion,
          tests: Object.values(grouped).map(test => ({
            id: test.id,
            name: test.nombre,
            quantity: test.cantidad
          }))
        }
      })
    
    // Calcular días hábiles de oportunidad (días transcurridos hasta el momento de completar)
    const oportunidad = calculateBusinessDays(c.receivedAt || '')
    
    return { 
      caseCode: c.caseCode || c.id, 
      remainingSubsamples: remaining,
      business_days: oportunidad, // Campo para registrar días hábiles al completar
      delivered_to: entregadoA.value.trim(), // Campo para registrar quién recibe
      delivered_at: new Date().toISOString() // Fecha actual de entrega
    }
  })
  
  casesApiService.batchCompleteCases(batchPayload)
    .then(r => {
      emit('completed', r)
      emit('update:modelValue', false)
      // Limpiar campo al cerrar exitosamente
      entregadoA.value = ''
      entregadoAError.value = ''
    })
    .catch((error) => {
      console.error('Error al completar casos:', error)
      // En caso de error simplemente mantenemos abierto? podría mejorarse con estado de error
      // Aquí se podría emitir un evento 'error' si se define posteriormente.
    })
}

// ================= Helpers para pruebas duplicadas =================
interface DrawerTestEntry { id: string; name?: string; quantity?: number }

// Cache de expansión por caso+submuestra para evitar recomputar en cada render
const expandedTestsCache = new Map<string, DrawerTestEntry[]>()

function getExpandedTestsCached(caseId: string, subsampleIndex: number, tests: DrawerTestEntry[]): DrawerTestEntry[] {
  const key = `${caseId || ''}|${subsampleIndex}|${tests.length}`
  const cached = expandedTestsCache.get(key)
  if (cached) return cached
  const expanded: DrawerTestEntry[] = []
  for (const t of tests) {
    const qty = t.quantity && t.quantity > 1 ? t.quantity : 1
    for (let i = 0; i < qty; i++) expanded.push({ id: t.id, name: t.name || t.id, quantity: 1 })
  }
  expandedTestsCache.set(key, expanded)
  return expanded
}

// ================= Cálculo de días hábiles para Oportunidad =================
function calculateBusinessDays(startDate: string, endDate?: string): number {
  const start = new Date(startDate)
  const end = endDate ? new Date(endDate) : new Date()
  
  // Validar fechas válidas
  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    return 0
  }
  
  // Asegurar que start sea anterior a end
  const fromDate = start <= end ? start : end
  const toDate = start <= end ? end : start
  
  let businessDays = 0
  const currentDate = new Date(fromDate)
  
  // Si la fecha de inicio es fin de semana, avanzar al próximo lunes
  while (currentDate.getDay() === 0 || currentDate.getDay() === 6) {
    currentDate.setDate(currentDate.getDate() + 1)
    // Si después de avanzar ya pasamos la fecha final, retornar 0
    if (currentDate > toDate) {
      return 0
    }
  }
  
  // Ahora currentDate está en el primer día hábil
  const firstBusinessDay = new Date(currentDate)
  
  // Si estamos en el mismo día que empezó (primer día hábil), retornar 0
  if (firstBusinessDay.toDateString() === toDate.toDateString()) {
    return 0
  }
  
  // Avanzar al siguiente día para empezar a contar días completados
  currentDate.setDate(currentDate.getDate() + 1)
  
  // Contar días hábiles completados (excluyendo el primer día)
  while (currentDate <= toDate) {
    const dayOfWeek = currentDate.getDay()
    
    // Contar solo lunes(1) a viernes(5)
    if (dayOfWeek >= 1 && dayOfWeek <= 5) {
      businessDays++
    }
    
    // Avanzar al siguiente día
    currentDate.setDate(currentDate.getDate() + 1)
  }
  
  // Nunca retornar números negativos
  return Math.max(0, businessDays)
}
</script>

<style scoped>
</style>
