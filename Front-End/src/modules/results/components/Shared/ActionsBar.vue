<template>
  <div class="flex flex-wrap items-center gap-3 justify-between w-full">
    <div v-if="lastSavedAt" class="text-xs text-gray-500">
      Último guardado: {{ new Date(lastSavedAt).toLocaleTimeString() }}
    </div>
    <div class="flex items-center gap-3 ml-auto">
      <ClearButton :disabled="disabled" @click="$emit('clear')" />
      <PreviewButton :disabled="previewing || disabled" @click="$emit('preview')" />
      <SaveButton :disabled="saving || disabled" :loading="saving" :text="'Guardar'" :loading-text="'Guardando...'" @click="$emit('save-draft')" />
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { SaveButton, ClearButton, PreviewButton } from '@/shared/components/buttons'

defineProps<{ saving?: boolean, previewing?: boolean, lastSavedAt?: string, disabled?: boolean, canSave?: boolean }>()
defineEmits<{ (e: 'save-draft'): void, (e: 'preview'): void, (e: 'clear'): void }>()
</script>


