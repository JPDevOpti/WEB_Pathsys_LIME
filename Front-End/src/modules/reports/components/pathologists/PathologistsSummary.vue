<template>
  <ComponentCard title="Resumen de Patólogos">
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-4">
      <div class="bg-blue-50 p-4 rounded-md border border-blue-100">
        <h4 class="text-sm font-semibold text-blue-700 mb-1">Dentro de Oportunidad</h4>
        <div class="flex items-end justify-between">
          <span class="text-2xl font-bold text-blue-600">{{ totalWithin }}</span>
          <span class="text-sm text-blue-500">{{ pctWithin }}%</span>
        </div>
      </div>
      <div class="bg-red-50 p-4 rounded-md border border-red-100">
        <h4 class="text-sm font-semibold text-red-700 mb-1">Fuera de Oportunidad</h4>
        <div class="flex items-end justify-between">
          <span class="text-2xl font-bold text-red-600">{{ totalOut }}</span>
          <span class="text-sm text-red-500">{{ pctOut }}%</span>
        </div>
      </div>
      <div class="bg-gray-50 p-4 rounded-md border border-gray-200">
        <h4 class="text-sm font-semibold text-gray-700 mb-1">Total Casos</h4>
        <div class="flex items-end justify-between">
          <span class="text-2xl font-bold text-gray-700">{{ total }}</span>
          <span class="text-sm text-gray-500">100%</span>
        </div>
      </div>
    </div>
    
    <div class="bg-gray-50 p-4 rounded-xl border border-gray-100">
      <h4 class="text-sm font-semibold text-gray-800 mb-3">Distribución General</h4>
      <apexchart type="donut" height="260" :options="donutOptions" :series="donutSeries" />
    </div>
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ComponentCard } from '@/shared/components/common'

const props = defineProps<{ 
  resumen?: { total: number; within: number; out: number } 
}>()

const totalWithin = computed(() => props.resumen?.within || 0)
const totalOut = computed(() => props.resumen?.out || 0)
const total = computed(() => props.resumen?.total || 0)
const pctWithin = computed(() => total.value ? ((totalWithin.value / total.value) * 100).toFixed(1) : '0.0')
const pctOut = computed(() => total.value ? ((totalOut.value / total.value) * 100).toFixed(1) : '0.0')

// Charts
const donutSeries = computed(() => [totalWithin.value, totalOut.value])
const donutOptions = computed(() => ({
  chart: { type: 'donut' },
  labels: ['Dentro de Oportunidad', 'Fuera de Oportunidad'],
  colors: ['#6ce9a6', '#f97066'],
  legend: { position: 'bottom' },
  plotOptions: { 
    pie: { 
      donut: { 
        labels: { 
          show: true, 
          total: { 
            show: true, 
            label: 'Total', 
            formatter: () => total.value 
          } 
        } 
      } 
    } 
  },
  dataLabels: { formatter: (val: number) => `${val.toFixed(1)}%` },
  tooltip: { y: { formatter: (val: number) => `${val} casos` } }
}))
</script>
