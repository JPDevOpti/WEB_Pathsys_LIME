<template>
  <div>
    <div class="text-sm text-gray-500 mb-2">Caso</div>
    <div v-if="loading" class="text-gray-400 text-sm">Cargando...</div>
    <div v-else-if="!sample" class="text-gray-400 text-sm">Sin datos del caso</div>
    <div v-else class="space-y-1">
      <div class="font-medium">{{ sample.id }}</div>
      <div class="text-sm text-gray-600">Tipo: {{ sample.type }}</div>
      <div class="text-sm text-gray-600">Fecha: {{ new Date(sample.collectedAt).toLocaleString() }}</div>
      <div class="text-sm text-gray-600">Estado: {{ sample.status }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Sample } from '../../types/results.types'

defineProps<{ sample: Sample | null, loading?: boolean }>()
</script>


