<template>
  <transition name="fade-scale">
    <div
      v-if="modelValue && caseData"
      :class="[
        'fixed right-0 bottom-0 z-[10000] flex items-end sm:items-center justify-center p-4 bg-black/40',
        'top-16',
        overlayLeftClass
      ]"
      @click.self="onClose"
    >
      <div class="w-full max-w-3xl bg-white rounded-xl shadow-xl overflow-hidden">
        <!-- Header -->
        <div class="px-4 py-3 border-b border-green-200 bg-green-50 flex items-start gap-3">
          <div class="flex items-center gap-2 flex-1">
            <div class="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
              </svg>
            </div>
            <div>
              <h3 class="text-sm font-semibold text-green-900">¡Caso Creado Exitosamente!</h3>
              <p class="text-xs text-green-600 mt-0.5">{{ createdCaseFecha }}</p>
            </div>
          </div>
          <button @click="onClose" class="text-green-400 hover:text-green-600" aria-label="Cerrar">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <!-- Body -->
        <div class="p-4 sm:p-5">
          <div class="text-center pb-3 border-b border-gray-200">
            <div class="inline-block">
              <p class="font-mono font-bold text-2xl text-green-700 mb-1">{{ caseData?.caso_code || caseData?.codigo }}</p>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-4">
            <div>
              <h4 class="font-semibold text-gray-800 mb-3 text-base">Información del Paciente</h4>
              <div class="space-y-2 text-sm">
                <div><span class="text-gray-500 font-medium">Nombre:</span><p class="text-gray-900 font-semibold">{{ caseData?.paciente?.nombre }}</p></div>
                <div><span class="text-gray-500 font-medium">Código:</span><p class="text-gray-900 font-mono font-semibold">{{ caseData?.paciente?.paciente_code || caseData?.paciente?.cedula }}</p></div>
                <div><span class="text-gray-500 font-medium">Edad:</span><p class="text-gray-900 font-semibold">{{ caseData?.paciente?.edad }} años</p></div>
                <div><span class="text-gray-500 font-medium">Sexo:</span><p class="text-gray-900 font-semibold capitalize">{{ caseData?.paciente?.sexo }}</p></div>
                <div><span class="text-gray-500 font-medium">Entidad:</span><p class="text-gray-900 font-semibold">{{ caseData?.paciente?.entidad_info?.nombre }}</p></div>
                <div><span class="text-gray-500 font-medium">Tipo de Atención:</span><p class="text-gray-900 font-semibold">{{ caseData?.paciente?.tipo_atencion }}</p></div>
              </div>
            </div>
            <div>
              <h4 class="font-semibold text-gray-800 mb-3 text-base">Detalles del Caso</h4>
              <div class="space-y-2 text-sm">
                <div><span class="text-gray-500 font-medium">Estado:</span><p class="text-gray-900 font-semibold">{{ caseData?.estado || 'En proceso' }}</p></div>
                <div><span class="text-gray-500 font-medium">Prioridad:</span><p class="text-gray-900 font-semibold">{{ caseData?.prioridad || 'Normal' }}</p></div>
                <div><span class="text-gray-500 font-medium">Médico Solicitante:</span><p class="text-gray-900 font-semibold">{{ caseData?.medico_solicitante || 'No especificado' }}</p></div>
                <div><span class="text-gray-500 font-medium">Servicio:</span><p class="text-gray-900 font-semibold">{{ caseData?.servicio || 'No especificado' }}</p></div>
                <div><span class="text-gray-500 font-medium">Número de Submuestras:</span><p class="text-gray-900 font-semibold">{{ (caseData?.muestras || []).length }}</p></div>
                <div v-if="caseData?.observaciones_generales"><span class="text-gray-500 font-medium">Observaciones:</span><p class="text-gray-900">{{ caseData?.observaciones_generales }}</p></div>
              </div>
            </div>
          </div>

          <div class="mt-4">
            <h4 class="font-semibold text-gray-800 mb-3 text-base">Submuestras</h4>
            <div class="space-y-3">
              <div v-for="(muestra, index) in (caseData?.muestras || [])" :key="index" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
                <div class="flex items-center justify-between mb-2">
                  <span class="font-medium text-gray-900 text-sm">Submuestra {{ index + 1 }}</span>
                  <span class="text-sm text-gray-500">{{ (muestra.pruebas && muestra.pruebas.length) || 0 }} prueba{{ ((muestra.pruebas && muestra.pruebas.length) || 0) !== 1 ? 's' : '' }}</span>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                  <div><span class="text-gray-500 font-medium">Región:</span><p class="text-gray-900">{{ muestra.region_cuerpo || muestra.regionCuerpo || 'Sin especificar' }}</p></div>
                  <div>
                    <span class="text-gray-500 font-medium">Pruebas:</span>
                    <div class="text-gray-900">
                      <span v-if="muestra.pruebas && muestra.pruebas.length > 0">
                        {{ muestra.pruebas.map((p: any) => `${p.id || p.codigo || p.nombre || 'Sin código'} (${p.cantidad || 1})`).join(', ') }}
                      </span>
                      <span v-else class="text-gray-400">Sin pruebas</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-4 py-3 bg-green-50 border-t border-green-200 flex justify-end">
          <button type="button" class="inline-flex justify-center items-center px-4 py-2 rounded-md text-sm font-medium border border-green-300 bg-green-600 text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500" @click="onClose">Cerrar</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSidebar } from '@/shared/composables/SidebarControl'

interface Props {
  modelValue: boolean
  caseData: any | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
}>()

const onClose = () => emit('update:modelValue', false)

const formatDateDisplay = (value: string | undefined | null): string => {
  if (!value) return ''
  const date = new Date(String(value))
  if (isNaN(date.getTime())) return String(value)
  return new Intl.DateTimeFormat('es-CO', { day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' }).format(date)
}

const createdCaseFecha = computed(() => {
  const raw = (props.caseData?.fecha_creacion || props.caseData?.fechaIngreso) as string | undefined
  return formatDateDisplay(raw)
})

// Alineación consistente con CaseDetailsModal: respetar header y sidebar
const { isExpanded, isMobileOpen, isHovered } = useSidebar()
const overlayLeftClass = computed(() => {
  const hasWideSidebar = (isExpanded.value && !isMobileOpen.value) || (!isExpanded.value && isHovered.value)
  return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})
</script>

<style scoped>
.fade-scale-enter-active { transition: all 0.18s ease-out; }
.fade-scale-leave-active { transition: all 0.12s ease-in; }
.fade-scale-enter-from, .fade-scale-leave-to { opacity: 0; transform: scale(.98); }
</style>


