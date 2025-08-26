<template>
  <div>
    <div class="flex items-center justify-between mb-2">
      <div class="text-sm text-gray-500">Adjuntos</div>
      <AddButton size="sm" @click="$emit('add-attachment')">Agregar</AddButton>
    </div>
    <div v-if="!attachments.length" class="text-gray-400 text-sm">Sin adjuntos</div>
    <ul v-else class="space-y-2">
      <li v-for="file in attachments" :key="file.id" class="flex items-center justify-between p-2 border rounded">
        <div>
          <div class="font-medium text-sm">{{ file.fileName }}</div>
          <div class="text-xs text-gray-500">{{ file.fileType }} · {{ file.sizeKb }} KB</div>
        </div>
        <RemoveButton size="sm" @click="$emit('remove-attachment', file.id)" />
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { Attachment } from '../../types/results.types'
import { AddButton, RemoveButton } from '@/shared/components/ui/buttons'

defineProps<{ attachments: Attachment[] }>()
defineEmits<{ (e: 'add-attachment'): void, (e: 'remove-attachment', id: string): void }>()
</script>


