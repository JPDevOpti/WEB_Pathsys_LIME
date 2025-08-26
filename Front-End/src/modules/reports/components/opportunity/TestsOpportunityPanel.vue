<template>
  <div class="bg-white rounded-xl border border-gray-200 overflow-hidden transition-all duration-200 hover:shadow-sm">
    <div class="p-4 border-b border-gray-200 flex justify-between items-center">
      <div>
        <h3 class="font-semibold text-gray-800">{{ prueba.name }}</h3>
        <div class="text-xs text-gray-500 mt-1">Código: {{ prueba.code }}</div>
      </div>
      <div class="text-xs font-medium px-2.5 py-1 rounded-full" :class="badgeClass">
        {{ completion }}% 
      </div>
    </div>
    <div class="p-4">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
        <div class="bg-blue-50 p-3 rounded-md border border-blue-100">
          <div class="text-xs text-blue-600 mb-1">Dentro de Oportunidad</div>
          <div class="text-xl font-semibold text-blue-700">{{ prueba.withinOpportunity }}</div>
        </div>
        <div class="bg-red-50 p-3 rounded-md border border-red-100">
          <div class="text-xs text-red-600 mb-1">Fuera de Oportunidad</div>
          <div class="text-xl font-semibold text-red-700">{{ prueba.outOfOpportunity }}</div>
        </div>
        <div class="bg-gray-50 p-3 rounded-md border border-gray-200">
          <div class="text-xs text-gray-600 mb-1">Total Procedimientos</div>
          <div class="text-xl font-semibold text-gray-700">{{ total }}</div>
        </div>
      </div>
      <div class="mt-2">
        <div class="flex justify-between text-xs text-gray-500 mb-1">
          <span>Tiempo de Oportunidad: {{ prueba.opportunityTime }}</span>
          <span>{{ completion }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
          <div class="h-2.5 rounded-full" :class="barClass" :style="{ width: `${completion}%` }"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { OpportunityTest } from '../../types/opportunity.types'

const props = defineProps<{ prueba: OpportunityTest }>()

const total = computed(() => props.prueba.withinOpportunity + props.prueba.outOfOpportunity)
const completion = computed(() => total.value ? Math.round((props.prueba.withinOpportunity / total.value) * 100) : 0)

const badgeClass = computed(() => {
  if (completion.value >= 85) return 'bg-green-100 text-green-800'
  if (completion.value >= 70) return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
})

const barClass = computed(() => {
  if (completion.value >= 85) return 'bg-green-500'
  if (completion.value >= 70) return 'bg-yellow-500'
  return 'bg-red-500'
})
</script>


