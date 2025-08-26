<!--
  Componente CasesByMonth
  Muestra un gráfico de barras con el número de casos ingresados por mes.
-->
<template>
  <Card class="overflow-hidden px-5 pt-5 sm:px-6 sm:pt-6">
    <div>
      <h3 class="text-lg font-semibold text-gray-800">
        Casos ingresados por mes ({{ anioActual }})
      </h3>
    </div>

    <!-- Estado de carga -->
    <div v-if="isLoading" class="flex items-center justify-center py-8">
      <div class="flex flex-col items-center space-y-3">
        <svg class="animate-spin h-8 w-8 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="text-sm text-gray-500">Cargando estadísticas...</p>
      </div>
    </div>

    <!-- Estado de error -->
    <div v-else-if="error" class="flex items-center justify-center py-8">
      <div class="flex flex-col items-center space-y-3">
        <svg class="h-8 w-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-sm text-red-500">{{ error }}</p>
        <button
          @click="cargarEstadisticas"
          class="text-sm text-blue-500 hover:text-blue-600 underline"
        >
          Intentar nuevamente
        </button>
      </div>
    </div>

    <!-- Gráfico -->
    <div v-else-if="totalCasos > 0" class="max-w-full overflow-x-auto custom-scrollbar">
      <div id="chartOne" class="-ml-5 min-w-[650px] xl:min-w-full pl-2">
        <VueApexCharts type="bar" height="180" :options="chartOptions" :series="series" />
      </div>
    </div>
    
    <!-- Estado sin datos -->
    <div v-else class="flex items-center justify-center py-8">
      <div class="flex flex-col items-center space-y-3">
        <svg class="h-12 w-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <div class="text-center">
          <p class="text-gray-500 text-sm font-medium">No hay datos para mostrar</p>
          <p class="text-gray-400 text-xs mt-1">No se encontraron casos para el año {{ anioActual }}</p>
        </div>
      </div>
    </div>

    <!-- Información adicional -->
    <div v-if="!isLoading && !error" class="mt-4 text-center">
      <p class="text-sm text-gray-500">
        Total de casos en {{ anioActual }}: <span class="font-semibold text-gray-700">{{ totalCasos }}</span>
      </p>
      <p v-if="totalCasos === 0" class="text-xs text-amber-600 mt-1">
        No se encontraron casos para el año {{ anioActual }}
      </p>
    </div>
  </Card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import { Card } from '@/shared/components/ui/data-display'
import { useDashboard } from '../composables/useDashboard'

// Usar el composable del dashboard
const {
  casosPorMes,
  loadingCasosPorMes: isLoading,
  error,
  cargarCasosPorMes,
  totalCasosAño,
  añoActual: anioActual
} = useDashboard()

// Alias para compatibilidad con el template existente
const estadisticas = casosPorMes
const totalCasos = totalCasosAño



// Datos de las series para el gráfico
const series = computed(() => {
  const datos = estadisticas.value?.datos
  const datosValidos = Array.isArray(datos) ? datos : [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  
  return [
    {
      name: 'Casos',
      data: datosValidos,
    },
  ]
})

// Configuración del gráfico
const chartOptions = ref({
  colors: ['#3D8D5B'],
  chart: {
    fontFamily: 'Outfit, sans-serif',
    type: 'bar',
    toolbar: {
      show: false,
    },
  },
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: '39%',
      borderRadius: 5,
      borderRadiusApplication: 'end',
    },
  },
  dataLabels: {
    enabled: false,
  },
  stroke: {
    show: true,
    width: 4,
    colors: ['transparent'],
  },
  xaxis: {
    categories: [
      'Ene',
      'Feb',
      'Mar',
      'Abr',
      'May',
      'Jun',
      'Jul',
      'Ago',
      'Sep',
      'Oct',
      'Nov',
      'Dic',
    ],
    axisBorder: {
      show: false,
    },
    axisTicks: {
      show: false,
    },
  },
  legend: {
    show: true,
    position: 'top',
    horizontalAlign: 'left',
    fontFamily: 'Outfit',
    markers: {
      radius: 99,
    },
  },
  yaxis: {
    title: false,
  },
  grid: {
    yaxis: {
      lines: {
        show: true,
      },
    },
  },
  fill: {
    opacity: 1,
  },
  tooltip: {
    x: {
      show: false,
    },
    y: {
      formatter: function (val: any) {
        return val.toString()
      },
    },
  },
})

// Función para cargar estadísticas
const cargarEstadisticas = async () => {
  try {
    await cargarCasosPorMes()
  } catch (error) {
    // Error ya manejado en el composable
  }
}

onMounted(() => {
  cargarEstadisticas()
})
</script>

<style scoped>
/* Estilos personalizados para el scrollbar */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #CBD5E1 transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  height: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #CBD5E1;
  border-radius: 3px;
}
</style> 