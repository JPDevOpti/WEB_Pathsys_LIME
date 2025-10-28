<template>
  <transition name="fade-scale">
    <div 
      v-if="visible" 
      :class="['fixed right-0 bottom-0 z-[10000] flex items-center justify-center p-4 bg-black/40 top-16', overlayLeftClass]"
      @click.self="$emit('close')"
    >
      <div class="relative w-full max-w-xl bg-white rounded-2xl shadow-2xl overflow-hidden">
        <!-- Close button -->
        <button
          @click="$emit('close')"
          class="absolute top-4 right-4 z-10 p-2 rounded-lg bg-white/90 hover:bg-white transition-all duration-200 text-gray-600 hover:text-gray-800 ring-1 ring-transparent hover:ring-gray-200 hover:scale-105"
          title="Cerrar"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <!-- Header -->
        <div class="px-4 py-4 pr-12 border-b border-gray-200">
          <div class="flex items-center space-x-3">
            <div class="flex-shrink-0">
              <div class="w-10 h-10 bg-red-50 rounded-full flex items-center justify-center">
                <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3m-4 0h14" />
                </svg>
              </div>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900">Paciente eliminado</h3>
              <p class="text-gray-600 text-xs mt-1">El paciente fue eliminado del sistema</p>
            </div>
          </div>
        </div>

        <!-- Body -->
        <div class="p-4 space-y-4">
          <div class="bg-white rounded-lg p-3 border border-gray-200">
            <div class="mb-3 pb-3 border-b border-gray-200">
              <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-1">Paciente</p>
              <h4 class="text-lg font-semibold text-gray-900">{{ displayName }}</h4>
            </div>
            <div class="grid grid-cols-1 gap-3">
              <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                <div class="flex items-center space-x-2">
                  <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                      <svg class="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0" />
                      </svg>
                    </div>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Documento</p>
                    <p class="text-sm font-bold text-gray-900 font-mono">{{ documentDisplay }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="flex items-center justify-end pt-2">
            <button
              @click="$emit('close')"
              class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-300 focus:ring-offset-2"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useSidebar } from '@/shared/composables/SidebarControl'
import { IDENTIFICATION_TYPE_NAMES, IdentificationType } from '@/modules/patients/types'

interface PatientData {
  name?: string
  first_name?: string
  second_name?: string
  first_lastname?: string
  second_lastname?: string
  identification_type?: number | string
  identification_number?: string
}

interface Props {
  visible: boolean
  patientData: PatientData
  closeOnEsc?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  closeOnEsc: true
})

const emit = defineEmits<{ (e: 'close'): void }>()

const { isExpanded, isMobileOpen, isHovered } = useSidebar()
const overlayLeftClass = computed(() => {
  const hasWideSidebar = (isExpanded.value && !isMobileOpen.value) || (!isExpanded.value && isHovered.value)
  return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})

const IDENTIFICATION_CODE_LABELS: Record<string, string> = {
  CC: 'Cédula de Ciudadanía',
  CE: 'Cédula de Extranjería',
  TI: 'Tarjeta de Identidad',
  PA: 'Pasaporte',
  RC: 'Registro Civil',
  NIT: 'NIT'
}

const getIdentificationTypeLabel = (value: unknown): string => {
  if (typeof value === 'number') {
    return IDENTIFICATION_TYPE_NAMES[value as IdentificationType] ?? String(value)
  }
  if (typeof value === 'string') {
    return IDENTIFICATION_CODE_LABELS[value] ?? value
  }
  return ''
}

const displayName = computed(() => {
  const p: any = props.patientData || {}
  if (p.name) return p.name
  const parts = [p.first_name, p.second_name, p.first_lastname, p.second_lastname].filter(Boolean)
  return parts.join(' ').trim() || 'Sin nombre'
})

const documentDisplay = computed(() => {
  const p: any = props.patientData || {}
  const typeLabel = getIdentificationTypeLabel(p.identification_type)
  const number = p.identification_number || ''
  return [typeLabel, number].filter(Boolean).join(' - ')
})

function onKey(e: KeyboardEvent) {
  if (!props.visible) return
  if (e.key === 'Escape' && props.closeOnEsc) {
    emit('close')
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
})
</script>

<style scoped>
.fade-scale-enter-active { transition: all 0.18s ease-out; }
.fade-scale-leave-active { transition: all 0.12s ease-in; }
.fade-scale-enter-from, .fade-scale-leave-to { opacity: 0; transform: scale(.95); }
</style>