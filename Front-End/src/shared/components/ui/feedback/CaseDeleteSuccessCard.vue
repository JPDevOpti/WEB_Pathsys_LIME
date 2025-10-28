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
              <h3 class="text-lg font-bold text-gray-900">Caso eliminado exitosamente</h3>
              <p class="text-gray-600 text-sm">El caso ha sido eliminado del sistema</p>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="px-4 py-4">
          <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Código del Caso</p>
                <p class="text-lg font-bold text-gray-900 font-mono">{{ caseCodeDisplay }}</p>
              </div>
              <div class="text-right">
                <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Estado</p>
                <p class="text-sm font-bold text-red-600">Eliminado</p>
              </div>
            </div>
          </div>

          <div class="flex items-center justify-end pt-4">
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

interface CaseData {
  case_code?: string
  codigo?: string
  code?: string
  id?: string
}

interface Props {
  visible: boolean
  caseData: CaseData
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

const caseCodeDisplay = computed(() => {
  const c: any = props.caseData || {}
  return c.case_code || c.codigo || c.code || c.id || 'Sin código'
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