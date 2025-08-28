<template>
  <div class="h-full flex flex-col">
    <div class="flex flex-wrap items-center gap-4 mb-4 flex-shrink-0">
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
    <div class="flex-1 min-h-0">
      <FormTextarea 
        :model-value="modelValue" 
        @update:model-value="$emit('update:modelValue', $event)" 
        class="w-full h-full resize-none py-3 transition-colors"
        :class="getTextareaClasses()"
        :rows="12"
        :show-counter="false"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { FormTextarea } from '@/shared/components/forms'
import { computed } from 'vue'

type EditorSectionKey = 'method' | 'macro' | 'micro' | 'diagnosis'
const props = defineProps<{ 
  modelValue: string, 
  activeSection: EditorSectionKey,
  sections?: { method: string; macro: string; micro: string; diagnosis: string }
}>()
defineEmits<{ (e: 'update:modelValue', value: string): void, (e: 'update:activeSection', value: EditorSectionKey): void }>()

const tabs: Array<{ key: EditorSectionKey, label: string }> = [
  { key: 'method', label: 'Método' },
  { key: 'macro', label: 'Corte Macro' },
  { key: 'micro', label: 'Corte Micro' },
  { key: 'diagnosis', label: 'Diagnóstico' }
]

// Usar directamente la prop sin computed

function isFieldComplete(fieldKey: EditorSectionKey): boolean {
  if (!props.sections) return true
  return !!props.sections[fieldKey]?.trim()
}

function getTabClasses(tabKey: EditorSectionKey): string {
  const isActive = tabKey === props.activeSection
  const isComplete = isFieldComplete(tabKey)
  
  if (isActive) {
    return 'bg-blue-600 text-white border-blue-600'
  }
  
  if (!isComplete) {
    return 'bg-yellow-50 text-yellow-700 border-yellow-300 hover:bg-yellow-100'
  }
  
  return 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
}

function getTextareaClasses(): string {
  const isComplete = isFieldComplete(props.activeSection)
  
  if (!isComplete) {
    return 'border-yellow-300 focus:border-yellow-400 focus:ring-yellow-400'
  }
  
  return 'border-gray-300 focus:border-blue-400 focus:ring-blue-400'
}
</script>


