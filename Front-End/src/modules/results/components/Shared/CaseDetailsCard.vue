<template>
  <div>
    <div class="flex items-center gap-2 mb-3">
      <DocsIcon class="w-5 h-5 text-gray-600" />
      <h3 class="text-lg font-semibold text-gray-800">Detalles del caso</h3>
    </div>
    <div v-if="loading" class="text-gray-400 text-sm">Cargando...</div>
    <div v-else-if="!details" class="text-gray-400 text-sm">Sin datos del caso</div>
    <div v-else class="space-y-4">
      <div class="grid grid-cols-1 gap-2 text-sm text-gray-700">
        <div><span class="font-bold">Caso:</span> {{ details.case_code }}</div>
        <div><span class="font-bold">Estado:</span> <span class="capitalize">{{ details.state }}</span></div>
        <div><span class="font-bold">Creación:</span> {{ formatDate(details.created_at) }}</div>
        <div v-if="details.updated_at"><span class="font-bold">Actualización:</span> {{ formatDate(details.updated_at) }}</div>
        <div v-if="details.entity_info"><span class="font-bold">Entidad:</span> {{ details.entity_info?.name }} ({{ details.entity_info?.id }})</div>
        <div v-if="details.requesting_physician"><span class="font-bold">Médico solicitante:</span> {{ details.requesting_physician }}</div>
        <div v-if="details.assigned_pathologist"><span class="font-bold">Patólogo asignado:</span> {{ details.assigned_pathologist?.name }} ({{ details.assigned_pathologist?.id }})</div>
      </div>

      <div class="space-y-2">
        <div class="text-sm text-gray-500">Muestras y pruebas</div>
        <div class="space-y-2">
          <div v-for="(m, i) in details.samples" :key="i" class="border rounded p-2">
            <div class="text-sm"><span class="font-bold">Región:</span> {{ m.body_region }}</div>
            <ul class="list-disc list-inside text-xs text-gray-700 mt-1">
              <li v-for="(p, j) in m.tests" :key="j"><span class="font-bold">{{ p.id }}</span> - {{ p.name }}</li>
            </ul>
          </div>
        </div>
      </div>

      <div v-if="details?.observations" class="text-sm text-gray-700">
        <span class="font-bold">Observaciones generales:</span>
        <div class="mt-1 p-2 bg-gray-50 rounded whitespace-pre-wrap text-sm">{{ details?.observations }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CaseDetails } from '../../types/results.types'
import { DocsIcon } from '@/assets/icons'

defineProps<{ details: CaseDetails | null, loading?: boolean }>()

function formatDate(iso?: string | null) {
  if (!iso) return '-'
  try { return new Date(iso).toLocaleString() } catch { return iso as string }
}
</script>


