<template>
  <Notification
    :visible="props.visible"
    :type="props.type"
    :title="props.title || ''"
    :message="props.message || ''"
    :inline="props.inline"
    :auto-close="props.autoClose"
    @close="$emit('close')"
  >
    <template v-if="props.type === 'success'" #content>
      <div class="relative p-4 sm:p-5 bg-white border border-gray-200 rounded-lg shadow-sm">
        <div class="space-y-4">
          <div class="text-center pb-3 border-b border-gray-200">
            <div class="inline-block">
              <p class="font-semibold text-gray-900 text-base">{{ headerTitle }}</p>
              <p class="text-gray-500 text-sm">{{ props.caseCode }}</p>
            </div>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <h5 class="font-medium text-gray-700 mb-1">Método</h5>
              <div class="text-gray-900 whitespace-pre-wrap break-words overflow-hidden bg-gray-50 border border-gray-200 rounded p-3 min-h-[60px] max-w-full">{{ (props.savedContent?.method?.length || 0) > 0 ? props.savedContent.method.join(', ') : '—' }}</div>
            </div>
            <div>
              <h5 class="font-medium text-gray-700 mb-1">Corte Macro</h5>
              <div class="text-gray-900 whitespace-pre-wrap break-words overflow-hidden bg-gray-50 border border-gray-200 rounded p-3 min-h-[60px] max-w-full">{{ props.savedContent?.macro || '—' }}</div>
            </div>
            <div>
              <h5 class="font-medium text-gray-700 mb-1">Corte Micro</h5>
              <div class="text-gray-900 whitespace-pre-wrap break-words overflow-hidden bg-gray-50 border border-gray-200 rounded p-3 min-h-[60px] max-w-full">{{ props.savedContent?.micro || '—' }}</div>
            </div>
            <div>
              <h5 class="font-medium text-gray-700 mb-1">Diagnóstico</h5>
              <div class="text-gray-900 whitespace-pre-wrap break-words overflow-hidden bg-gray-50 border border-gray-200 rounded p-3 min-h-[60px] max-w-full">{{ props.savedContent?.diagnosis || '—' }}</div>
            </div>
          </div>

          <div v-if="props.context === 'sign' && (props.diagnoses?.cie10 || props.diagnoses?.cieo)" class="pt-2 border-t border-gray-200">
            <h5 class="text-sm font-medium text-gray-700 mb-2">Diagnósticos Clasificados</h5>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div v-if="props.diagnoses?.cie10">
                <div class="flex items-center gap-2 mb-1">
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">CIE-10</span>
                  <span class="text-xs font-mono text-gray-600">{{ props.diagnoses.cie10.codigo }}</span>
                </div>
                <div class="text-gray-900 bg-gray-50 border border-gray-200 rounded p-2 min-h-[40px]">{{ props.diagnoses.cie10.nombre }}</div>
              </div>
              <div v-if="props.diagnoses?.cieo">
                <div class="flex items-center gap-2 mb-1">
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">CIE-O</span>
                  <span class="text-xs font-mono text-gray-600">{{ props.diagnoses.cieo.codigo }}</span>
                </div>
                <div class="text-gray-900 bg-gray-50 border border-gray-200 rounded p-2 min-h-[40px]">{{ props.diagnoses.cieo.nombre }}</div>
              </div>
            </div>
          </div>

          <!-- Sección de pruebas complementarias solicitadas -->
          <div v-if="props.complementaryTests && props.complementaryTests.length" class="pt-2 border-t border-gray-200">
            <h5 class="text-sm font-medium text-gray-700 mb-2">Pruebas Complementarias Solicitadas</h5>
            <div class="bg-orange-50 border border-orange-200 rounded-lg p-3">
              <div class="flex items-center gap-2 mb-2">
                <svg class="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                </svg>
                <span class="text-orange-800 font-medium text-sm">Se requieren pruebas adicionales para completar el diagnóstico</span>
              </div>
              <div class="space-y-2">
                <div v-for="(test, index) in props.complementaryTests" :key="index" class="flex justify-between items-center bg-white border border-orange-200 rounded p-2 text-sm">
                  <div class="flex items-center gap-2">
                    <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-orange-100 text-orange-800">{{ test.code }}</span>
                    <span class="text-gray-900">{{ test.name || test.code }}</span>
                  </div>
                  <div class="text-gray-600">
                    <span class="text-xs">Cant:</span> {{ test.quantity || 1 }}
                  </div>
                </div>
              </div>
              <div v-if="props.complementaryTestsReason" class="mt-3 pt-2 border-t border-orange-200">
                <p class="text-xs text-gray-600 mb-1">Motivo de la solicitud:</p>
                <p class="text-sm text-gray-900 bg-white border border-orange-200 rounded p-2">{{ props.complementaryTestsReason }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Notification>
</template>

<script setup lang="ts">
import Notification from '@/shared/components/feedback/Notification.vue'
import { computed } from 'vue'

type NotificationType = 'success' | 'error' | 'warning' | 'info'
type ContextType = 'sign' | 'save'

const props = withDefaults(defineProps<{
  visible: boolean
  type: NotificationType
  title?: string
  message?: string
  inline?: boolean
  autoClose?: boolean
  caseCode?: string | null
  savedContent: { method: string[]; macro: string; micro: string; diagnosis: string }
  context?: ContextType
  diagnoses?: { cie10?: { codigo: string; nombre: string }, cieo?: { codigo: string; nombre: string } }
  complementaryTests?: Array<{ code: string; name: string; quantity: number }>
  complementaryTestsReason?: string
}>(), {
  inline: true,
  autoClose: false,
  context: 'save',
  caseCode: ''
})

defineEmits<{ (e: 'close'): void }>()

const headerTitle = computed(() => props.title || (props.context === 'sign' ? 'Resumen de resultados firmados' : 'Resumen de resultados guardados'))
</script>


