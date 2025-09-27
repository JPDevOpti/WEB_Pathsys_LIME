<template>
  <ComponentCard title="Distribución de Pacientes por Entidad" description="Gráfico de barras apiladas mostrando ambulatorios y hospitalizados por entidad.">
    <template #icon>
      <ChartIcon class="w-5 h-5 text-blue-600 mr-2" />
    </template>
    <apexchart type="bar" height="320" :options="chartOptions" :series="chartSeries" />
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ComponentCard } from '@/shared/components/common'
import type { EntityStats } from '../../types/entities.types'
import { ChartIcon } from '@/assets/icons'

const props = defineProps<{
  datos: EntityStats[]
}>()

const chartSeries = computed(() => [
  {
    name: 'Ambulatorios',
    data: props.datos.map(entity => entity.ambulatorios)
  },
  {
    name: 'Hospitalizados',
    data: props.datos.map(entity => entity.hospitalizados)
  }
])

const chartOptions = computed(() => ({
  chart: {
    type: 'bar',
    stacked: true,
    toolbar: {
      show: true,
      tools: { download: false, selection: false, zoom: false, zoomin: false, zoomout: false, pan: false, reset: false },
    },
    fontFamily: 'Inter, sans-serif',
    background: '#F9FAFB'
  },
  plotOptions: {
    bar: { horizontal: false, columnWidth: '55%', borderRadius: 4, dataLabels: { position: 'top' } }
  },
  dataLabels: {
    enabled: true,
    formatter: function(_: number, opts: { seriesIndex: number; dataPointIndex: number }) {
      const i = opts.dataPointIndex
      if (opts.seriesIndex === 1) {
        const ambulatorios = (chartSeries.value[0].data as number[])[i]
        const hospitalizados = (chartSeries.value[1].data as number[])[i]
        const total = ambulatorios + hospitalizados
        return total > 0 ? `${total}` : ''
      }
      return ''
    },
    style: { fontSize: '11px', fontWeight: 'bold', colors: ['#374151'] },
    offsetY: -18
  },
  stroke: { show: true, width: 2, colors: ['transparent'] },
  xaxis: {
    categories: props.datos.map(entity => entity.nombre),
    labels: { style: { fontSize: '12px', fontFamily: 'Inter, sans-serif' } },
    axisBorder: { show: false },
    axisTicks: { show: false }
  },
  yaxis: {
    title: { text: 'Pacientes', style: { fontSize: '12px', fontFamily: 'Inter, sans-serif' } },
    labels: { style: { fontSize: '12px', fontFamily: 'Inter, sans-serif' } }
  },
  fill: { opacity: 1 },
  tooltip: { y: { formatter: (val: number) => `${val} pacientes` }, theme: 'light', style: { fontSize: '12px', fontFamily: 'Inter, sans-serif' }},
  legend: { position: 'top', horizontalAlign: 'right', fontSize: '12px', fontFamily: 'Inter, sans-serif', markers: { width: 12, height: 12, radius: 12 } },
  colors: ['#22c55e', '#3b82f6'], // Verde para ambulatorios, azul para hospitalizados
  grid: { borderColor: '#E5E7EB', strokeDashArray: 4, xaxis: { lines: { show: false } } }
}))

// Responsive real: ajustar columnWidth y leyenda por breakpoint
;(
  chartOptions.value as any
).responsive = [
  {
    breakpoint: 1280,
    options: {
      plotOptions: { bar: { columnWidth: '60%' } },
      legend: { position: 'top' }
    }
  },
  {
    breakpoint: 1024,
    options: {
      plotOptions: { bar: { columnWidth: '70%' } },
      legend: { position: 'bottom' }
    }
  },
  {
    breakpoint: 640,
    options: {
      plotOptions: { bar: { columnWidth: '80%' } },
      xaxis: { labels: { rotate: -45 } },
      legend: { position: 'bottom' }
    }
  }
]
</script>
