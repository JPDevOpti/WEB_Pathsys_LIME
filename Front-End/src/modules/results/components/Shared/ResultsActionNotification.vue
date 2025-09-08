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
}>(), {
  inline: true,
  autoClose: false,
  context: 'save',
  caseCode: ''
})

defineEmits<{ (e: 'close'): void }>()

const headerTitle = computed(() => props.title || (props.context === 'sign' ? 'Resumen de resultados firmados' : 'Resumen de resultados guardados'))
</script>


