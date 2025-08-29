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
        <div><span class="font-bold">Caso:</span> {{ details.caso_code }}</div>
        <div><span class="font-bold">Estado:</span> <span class="capitalize">{{ details.estado }}</span></div>
        <div><span class="font-bold">Creación:</span> {{ formatDate(details.fecha_creacion) }}</div>
        <div v-if="details.fecha_firma"><span class="font-bold">Firma:</span> {{ formatDate(details.fecha_firma) }}</div>
        <div v-if="details.entidad_info"><span class="font-bold">Entidad:</span> {{ details.entidad_info?.nombre }} ({{ details.entidad_info?.codigo }})</div>
        <div v-if="details.medico_solicitante"><span class="font-bold">Médico solicitante:</span> {{ details.medico_solicitante?.nombre }}</div>
        <div v-if="details.patologo_asignado"><span class="font-bold">Patólogo asignado:</span> {{ details.patologo_asignado?.nombre }} ({{ details.patologo_asignado?.codigo }})</div>
      </div>

      <div class="space-y-2">
        <div class="text-sm text-gray-500">Muestras y pruebas</div>
        <div class="space-y-2">
          <div v-for="(m, i) in details.muestras" :key="i" class="border rounded p-2">
            <div class="text-sm"><span class="font-bold">Región:</span> {{ m.region_cuerpo }}</div>
            <ul class="list-disc list-inside text-xs text-gray-700 mt-1">
              <li v-for="(p, j) in m.pruebas" :key="j"><span class="font-bold">{{ p.id }}</span> - {{ p.nombre }}</li>
            </ul>
          </div>
        </div>
      </div>

      <div v-if="details.observaciones_generales" class="text-sm text-gray-700">
        <span class="font-bold">Observaciones generales:</span>
        <div class="mt-1 p-2 bg-gray-50 rounded whitespace-pre-wrap text-sm">{{ details.observaciones_generales }}</div>
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


