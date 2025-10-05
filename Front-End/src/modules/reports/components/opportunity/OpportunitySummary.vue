<template>
  <ComponentCard title="Resumen de Oportunidad" description="Resumen de las oportunidades generales del laboratorio.">
    <template #icon>
      <StatisticsIcon class="w-5 h-5 text-blue-600 mr-2" />
    </template>
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
        <h4 class="text-sm font-semibold text-gray-700 mb-1">Total Procedimientos</h4>
        <div class="flex items-end justify-between">
          <span class="text-2xl font-bold text-gray-700">{{ total }}</span>
          <span class="text-sm text-gray-500">100%</span>
        </div>
      </div>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
      <div class="bg-gray-50 p-4 rounded-xl border border-gray-100">
        <h4 class="text-sm font-semibold text-gray-800 mb-3">Distribución General</h4>
        <apexchart type="donut" height="240" :options="donutOptions" :series="donutSeries" />
      </div>
      <div class="bg-gray-50 p-4 rounded-xl border border-gray-100">
        <h4 class="text-sm font-semibold text-gray-800 mb-3">Tendencia de Cumplimiento</h4>
        <apexchart type="line" height="240" :options="lineOptions" :series="lineSeries" />
      </div>
    </div>

  </ComponentCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import ComponentCard from '@/shared/components/layout/ComponentCard.vue'
import type { OpportunityTest } from '../../types/opportunity.types'
import { StatisticsIcon } from '@/assets/icons'

const props = defineProps<{ datos: OpportunityTest[]; monthlyPct?: number[]; resumen?: { total: number; within: number; out: number } }>()

const totalWithin = computed(() => (props.resumen ? props.resumen.within : props.datos.reduce((a, p) => a + p.withinOpportunity, 0)))
const totalOut = computed(() => (props.resumen ? props.resumen.out : props.datos.reduce((a, p) => a + p.outOfOpportunity, 0)))
const total = computed(() => (props.resumen ? props.resumen.total : totalWithin.value + totalOut.value))
const pctWithin = computed(() => total.value ? ((totalWithin.value / total.value) * 100).toFixed(1) : '0.0')
const pctOut = computed(() => total.value ? ((totalOut.value / total.value) * 100).toFixed(1) : '0.0')

const best = computed(() => {
  if (!props.datos.length) return null
  let candidate = props.datos[0]
  let candidatePct = ratio(candidate)
  for (const p of props.datos) {
    const r = ratio(p)
    if (r > candidatePct) { candidate = p; candidatePct = r }
  }
  return candidate
})

const bestPct = computed(() => best.value ? ratio(best.value).toFixed(1) : '0.0')

function ratio(p: OpportunityTest): number {
  const t = p.withinOpportunity + p.outOfOpportunity
  return t ? (p.withinOpportunity / t) * 100 : 0
}

// Charts
const donutSeries = computed(() => [totalWithin.value, totalOut.value])
const donutOptions = computed(() => ({
  chart: { type: 'donut' },
  labels: ['Dentro de Oportunidad', 'Fuera de Oportunidad'],
  colors: ['#6ce9a6', '#f97066'],
  legend: { position: 'bottom' },
  plotOptions: { pie: { donut: { labels: { show: true, total: { show: true, label: 'Total', formatter: () => total.value } } } } },
  dataLabels: { 
    formatter: (val: number) => `${val.toFixed(1)}%`,
    style: {
      textShadow: 'none',
      filter: 'none'
    }
  },
  tooltip: { y: { formatter: (val: number) => `${val} procedimientos` } }
}))

// Tendencia: desde enero hasta el mes inmediatamente anterior
const monthsFull = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
] as const

function getMonthsFromJanuaryToPrev(): string[] {
  const now = new Date()
  const prevMonth = (now.getMonth() + 11) % 12
  if (prevMonth < 0) return []
  return monthsFull.slice(0, prevMonth + 1)
}

const lineCategories = computed(() => getMonthsFromJanuaryToPrev())
const lineSeries = computed(() => [{
  name: 'Cumplimiento',
  data: ((): number[] => {
    const len = lineCategories.value.length
    if (props.monthlyPct && props.monthlyPct.length) {
      // Tomar desde enero hasta el mes inmediatamente anterior
      return props.monthlyPct.slice(0, len).map((v) => Number(Number(v).toFixed(1)))
    }
    const currentPct = Number(pctWithin.value)
    return Array.from({ length: len }, (_, i) => {
      const delta = ((i - len / 2) / len) * 6
      const v = Math.max(0, Math.min(100, currentPct + delta))
      return Number(v.toFixed(1))
    })
  })()
}])
const lineOptions = computed(() => ({
  chart: { type: 'line', toolbar: { show: false } },
  stroke: { curve: 'smooth', width: 3 },
  colors: ['#0ba5ec'],
  xaxis: { categories: lineCategories.value },
  yaxis: { min: 0, max: 100, title: { text: '% Cumplimiento' }, labels: { formatter: (v: number) => `${v.toFixed(0)}%` } },
  markers: { size: 5 },
  tooltip: { y: { formatter: (v: number) => `${v.toFixed(1)}%` } }
}))
</script>


