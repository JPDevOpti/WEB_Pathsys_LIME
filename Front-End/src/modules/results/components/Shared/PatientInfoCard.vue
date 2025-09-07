<template>
  <div>
    <div class="flex items-center gap-2 mb-3">
      <UserCircleIcon class="w-5 h-5 text-gray-600" />
      <h3 class="text-lg font-semibold text-gray-800">Información del paciente</h3>
    </div>
    <div v-if="loading" class="text-gray-400 text-sm">Cargando...</div>
    <div v-else-if="!patient" class="text-gray-400 text-sm">Sin datos de paciente</div>
    <div v-else class="space-y-4">
      <div class="grid grid-cols-1 gap-2 text-sm text-gray-700">
        <div class="font-medium">{{ patient.fullName }}</div>
        <div><span class="font-bold">Documento:</span> {{ patient.id }}</div>
        <div><span class="font-bold">Edad:</span> {{ patient.age }} años</div>
        <div v-if="patient.sexo"><span class="font-bold">Sexo:</span> {{ patient.sexo }}</div>
        <div v-if="patient.tipoAtencion"><span class="font-bold">Tipo de atención:</span> {{ patient.tipoAtencion }}</div>
        <div v-if="patient.entity">
          <span class="font-bold">Entidad:</span> {{ patient.entity }}
          <span v-if="patient.entityCode" class="text-xs text-gray-500">({{ patient.entityCode }})</span>
        </div>
      </div>

      <div v-if="patient.observaciones" class="text-sm text-gray-700">
        <span class="font-bold">Observaciones:</span>
        <div class="mt-1 p-2 bg-gray-50 rounded whitespace-pre-wrap text-sm">{{ patient.observaciones }}</div>
      </div>

      <!-- Casos anteriores del paciente -->
      <div class="text-sm text-gray-700">
        <span class="font-bold">Casos anteriores:</span>
        <div v-if="!previousCases?.length" class="mt-1 text-xs text-gray-500">Sin casos anteriores</div>
        <div v-else class="mt-2 overflow-x-auto rounded-lg border border-gray-200">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Código</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha creación</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr 
                v-for="c in previousCases" 
                :key="c._id" 
                class="hover:bg-gray-50 cursor-pointer"
                @click="$emit('caseClick', c)"
              >
                <td class="px-3 py-2 whitespace-nowrap text-xs text-gray-900 font-medium">{{ c.caso_code }}</td>
                <td class="px-3 py-2 text-xs text-gray-900">{{ c.estado }}</td>
                <td class="px-3 py-2 whitespace-nowrap text-xs text-gray-500">{{ new Date(c.fecha_ingreso).toLocaleDateString() }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Patient } from '../../types/results.types'
import type { CaseListItem } from '@/modules/cases/types/case'
import { UserCircleIcon } from '@/assets/icons'

defineProps<{ patient: Patient | null, loading?: boolean, previousCases?: CaseListItem[] }>()
defineEmits<{ (e: 'caseClick', caseItem: CaseListItem): void }>()
</script>


