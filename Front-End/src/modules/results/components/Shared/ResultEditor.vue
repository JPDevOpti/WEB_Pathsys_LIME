<template>
  <div class="bg-white border border-gray-200 rounded-lg shadow-sm flex flex-col h-96">
    <!-- Header con tabs -->
    <div class="p-4 border-b border-gray-200 flex-shrink-0">
      <div class="flex flex-wrap items-center gap-4">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="px-3 py-1.5 rounded text-sm border transition-colors"
          :class="getTabClasses(tab.key)"
          @click="$emit('update:activeSection', tab.key)"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Contenido principal -->
    <div class="flex-1 min-h-0 p-4">
      <!-- Sección de métodos cuando la pestaña activa es 'method' -->
      <div v-if="activeSection === 'method'" class="h-full">
        <MethodSection
          :model-value="Array.isArray(modelValue) ? modelValue : []"
          @update:model-value="$emit('update:modelValue', $event)"
        />
      </div>
      
      <!-- Textarea para otras secciones -->
      <FormTextareaUnlimited 
        v-else
        :model-value="typeof modelValue === 'string' ? modelValue : ''" 
        @update:model-value="$emit('update:modelValue', $event)" 
        class="w-full h-full resize-none transition-colors"
        :class="getTextareaClasses()"
        :rows="8"
        :preview-text="getPreviewText(activeSection)"
      />
    </div>

    <!-- Footer con botones -->
    <div class="p-4 border-t border-gray-200 bg-gray-50 flex-shrink-0">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FormTextareaUnlimited } from '@/shared/components/forms'
import MethodSection from './MethodSection.vue'

type EditorSectionKey = 'method' | 'macro' | 'micro' | 'diagnosis'
const props = defineProps<{ 
  modelValue: string | string[], 
  activeSection: EditorSectionKey,
  sections?: { method: string[]; macro: string; micro: string; diagnosis: string }
}>()
defineEmits<{ (e: 'update:modelValue', value: string | string[]): void, (e: 'update:activeSection', value: EditorSectionKey): void }>()

const tabs: Array<{ key: EditorSectionKey, label: string }> = [
  { key: 'method', label: 'Método' },
  { key: 'macro', label: 'Corte Macro' },
  { key: 'micro', label: 'Corte Micro' },
  { key: 'diagnosis', label: 'Diagnóstico' }
]

// Funciones para estilos
function getTabClasses(tabKey: EditorSectionKey): string {
  const isActive = tabKey === props.activeSection
  
  if (isActive) {
    return 'bg-blue-600 text-white border-blue-600'
  }
  
  return 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
}

function getTextareaClasses(): string {
  return 'border-gray-300 focus:border-blue-400 focus:ring-blue-400'
}

// Función para obtener el texto de previsualización según la sección
function getPreviewText(section: EditorSectionKey): string {
  switch (section) {
    case 'macro':
      return 'Describa aquí los hallazgos macroscópicos observados en la muestra. Incluya características como tamaño, forma, color, consistencia, superficie, bordes, y cualquier otra característica relevante visible a simple vista...'
    case 'micro':
      return 'Describa aquí los hallazgos microscópicos observados en las preparaciones histológicas. Incluya características celulares, arquitectura tisular, patrones de crecimiento, presencia de inflamación, necrosis, y cualquier otro hallazgo relevante...'
    case 'diagnosis':
      return 'Escriba aquí el diagnóstico final basado en los hallazgos macroscópicos y microscópicos. Debe ser conciso, preciso y seguir la nomenclatura patológica estándar. Ejemplo: "Adenocarcinoma de colon moderadamente diferenciado"...'
    default:
      return ''
  }
}
</script>


