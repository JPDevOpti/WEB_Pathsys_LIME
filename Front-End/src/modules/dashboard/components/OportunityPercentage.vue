<template>
<Card :class="cardClass">
    <!-- Card header: title and subtitle -->
    <div class="px-4 pt-2 bg-white shadow-default rounded-2xl pb-0 sm:px-5 sm:pt-3 flex-1 flex flex-col">
      <div class="mb-2 flex-shrink-0">
        <div>
          <h3 class="text-base font-semibold text-gray-800">Oportunidad de atención</h3>
          <p class="mt-1 text-gray-500 text-xs">
            {{ datosOportunidad?.mes_anterior?.nombre || 'Mes anterior' }} - 
            Porcentaje de casos dentro de la oportunidad
          </p>
        </div>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="flex items-center justify-center flex-1">
        <div class="text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <span class="ml-2 text-gray-600 text-sm mt-2 block">Cargando datos...</span>
        </div>
      </div>

      <!-- Error state with retry -->
      <div v-else-if="error" class="flex items-center justify-center flex-1">
        <div class="text-center">
          <svg class="mx-auto h-10 w-10 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <p class="mt-2 text-sm text-gray-600">{{ error }}</p>
          <button 
            @click="cargarDatos"
            class="mt-3 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            Reintentar
          </button>
        </div>
      </div>

      <!-- Content: radial bar chart and delta badge -->
      <div v-else class="flex-1 flex flex-col justify-center">
        <div class="relative flex-1 flex items-center justify-center min-h-[160px] sm:min-h-[180px] lg:min-h-[200px]">
          <div id="chartTwo" class="h-full w-full flex items-center justify-center">
            <div class="radial-bar-chart">
              <VueApexCharts 
                v-if="!loading && !error && datosOportunidad"
                type="radialBar" 
                :height="chartHeight" 
                :options="chartOptions" 
                :series="series"
                class="transition-all duration-500 hover:scale-105" 
              />
            </div>
          </div>
          <!-- Percentage delta vs previous month -->
          <span
            :class="[
              'absolute left-1/2 top-[65%] -translate-x-1/2 -translate-y-[65%] rounded-full px-2 py-0.5 text-xs font-medium transition-all duration-300',
              (datosOportunidad?.cambio_porcentual || 0) > 0 
                ? 'bg-green-50 text-green-600 hover:bg-green-100' 
                : (datosOportunidad?.cambio_porcentual || 0) < 0 
                  ? 'bg-red-50 text-red-600 hover:bg-red-100'
                  : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
            ]"
          >
            {{ (datosOportunidad?.cambio_porcentual || 0) > 0 ? '+' : '' }}{{ datosOportunidad?.cambio_porcentual || 0 }}%
          </span>
        </div>
        <!-- Caption below chart -->
        <p class="mx-auto -mt-2 w-full max-w-[320px] text-center text-xs sm:text-sm text-gray-500 transition-colors duration-300 flex-shrink-0 px-2">
          <span class="hidden sm:inline">Progreso en el cumplimiento de tiempos de oportunidad ({{ datosOportunidad?.mes_anterior?.nombre || 'Mes anterior' }})</span>
          <span class="sm:hidden">Cumplimiento de oportunidad ({{ datosOportunidad?.mes_anterior?.nombre || 'Mes anterior' }})</span>
        </p>
      </div>
    </div>

    <!-- Footer stats: totals and breakdown -->
    <div v-if="!loading && !error" class="grid grid-cols-2 sm:flex sm:items-center sm:justify-center gap-2 sm:gap-4 px-3 py-2.5 sm:px-5 bg-gray-50 rounded-b-2xl flex-shrink-0">
      <div class="group transition-all duration-300 hover:scale-105 text-center">
        <p class="mb-1 text-gray-500 text-xs transition-colors duration-300 group-hover:text-gray-700">
          Total casos
        </p>
        <p class="flex items-center justify-center gap-1 text-sm font-semibold text-gray-800 transition-colors duration-300 group-hover:text-blue-600">
          {{ datosOportunidad?.total_casos_mes_anterior || 0 }}
        </p>
      </div>

      <div class="hidden sm:block w-px bg-gray-200 h-6"></div>

      <div class="group transition-all duration-300 hover:scale-105 text-center">
        <p class="mb-1 text-gray-500 text-xs transition-colors duration-300 group-hover:text-gray-700">
          <span class="hidden sm:inline">Tiempo promedio</span>
          <span class="sm:hidden">Promedio</span>
        </p>
        <p class="flex items-center justify-center gap-1 text-sm font-semibold text-gray-800 transition-colors duration-300 group-hover:text-blue-600">
          {{ datosOportunidad?.tiempo_promedio || 0 }}
          <span class="text-xs text-gray-500">días</span>
        </p>
      </div>

      <div class="hidden sm:block w-px bg-gray-200 h-6"></div>

      <div class="group transition-all duration-300 hover:scale-105 text-center">
        <p class="mb-1 text-gray-500 text-xs transition-colors duration-300 group-hover:text-gray-700">
          <span class="hidden sm:inline">Dentro de oportunidad</span>
          <span class="sm:hidden">Dentro</span>
        </p>
        <p class="flex items-center justify-center gap-1 text-sm font-semibold text-gray-800 transition-colors duration-300 group-hover:text-blue-600">
          {{ datosOportunidad?.casos_dentro_oportunidad || 0 }}
          <svg class="transition-transform duration-300 group-hover:translate-y-[-2px] w-3 h-3" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M7.60141 2.33683C7.73885 2.18084 7.9401 2.08243 8.16435 2.08243C8.16475 2.08243 8.16516 2.08243 8.16556 2.08243C8.35773 2.08219 8.54998 2.15535 8.69664 2.30191L12.6968 6.29924C12.9898 6.59203 12.9899 7.0669 12.6971 7.3599C12.4044 7.6529 11.9295 7.65306 11.6365 7.36027L8.91435 4.64004L8.91435 13.5C8.91435 13.9142 8.57856 14.25 8.16435 14.25C7.75013 14.25 7.41435 13.9142 7.41435 13.5L7.41435 4.64442L4.69679 7.36025C4.4038 7.65305 3.92893 7.6529 3.63613 7.35992C3.34333 7.06693 3.34348 6.59206 3.63646 6.29926L7.60141 2.33683Z" fill="#039855"/>
          </svg>
        </p>
      </div>

      <div class="hidden sm:block w-px bg-gray-200 h-6"></div>

      <div class="group transition-all duration-300 hover:scale-105 text-center">
        <p class="mb-1 text-gray-500 text-xs transition-colors duration-300 group-hover:text-gray-700">
          <span class="hidden sm:inline">Fuera de oportunidad</span>
          <span class="sm:hidden">Fuera</span>
        </p>
        <p class="flex items-center justify-center gap-1 text-sm font-semibold text-gray-800 transition-colors duration-300 group-hover:text-blue-600">
          {{ datosOportunidad?.casos_fuera_oportunidad || 0 }}
          <svg class="transition-transform duration-300 group-hover:translate-y-[-2px] w-3 h-3" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M7.26816 13.6632C7.4056 13.8192 7.60686 13.9176 7.8311 13.9176C7.83148 13.9176 7.83187 13.9176 7.83226 13.9176C8.02445 13.9178 8.21671 13.8447 8.36339 13.6981L12.3635 9.70076C12.6565 9.40797 12.6567 8.9331 12.3639 8.6401C12.0711 8.34711 11.5962 8.34694 11.3032 8.63973L8.5811 11.36L8.5811 2.5C8.5811 2.08579 8.24531 1.75 7.8311 1.75C7.41688 1.75 7.0811 1.46079 7.0811 1.75L7.0811 11.3556L4.36354 8.63975C4.07055 8.34695 3.59568 8.3471 3.30288 8.64009C3.01008 8.93307 3.01023 9.40794 3.30321 9.70075L7.26816 13.6632Z" fill="#D92D20"/>
          </svg>
        </p>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import { computed, onMounted, nextTick, useAttrs } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import VueApexCharts from 'vue3-apexcharts'
import { Card } from '@/shared/components/layout'
import { useDashboard } from '../composables/useDashboard'

const {
  estadisticasOportunidad,
  loadingOportunidad: loading,
  error,
  cargarEstadisticasOportunidad
} = useDashboard()

const authStore = useAuthStore()
// Align with app-wide rule: pathologist role but not administrator override
const esPatologo = computed(() => authStore.user?.role === 'pathologist' && authStore.userRole !== 'administrator')

const datosOportunidad = estadisticasOportunidad
// Chart renders when data exists; no local ready flag required

const attrs = useAttrs()
const cardClass = computed(() => {
  const extra = typeof attrs.class === 'string' ? (attrs.class as string) : ''
  return ['h-full flex flex-col', extra].filter(Boolean).join(' ')
})

// No watcher required; series and props are reactive

// Resolve role and fetch stats
const cargarDatos = async () => {
  await cargarEstadisticasOportunidad(esPatologo.value)
  await nextTick()
  // Apex will update via reactive series/options
}

// Responsive chart height
const chartHeight = computed(() => {
  return window.innerWidth < 640 ? 200 : window.innerWidth < 1024 ? 240 : 280
})

// Single radial value in percentage
const series = computed(() => {
  if (!datosOportunidad.value) return [0]
  const porcentaje = datosOportunidad.value.porcentaje_oportunidad
  return [typeof porcentaje === 'number' ? porcentaje : 0]
})

// Apex radial bar configuration
const chartOptions = {
  colors: ['#3D8D5B'],
  chart: {
    fontFamily: 'Outfit, sans-serif',
    sparkline: {
      enabled: true,
    },
    animations: {
      enabled: true,
      easing: 'easeinout',
      speed: 800,
      animateGradually: {
        enabled: true,
        delay: 150
      },
      dynamicAnimation: {
        enabled: true,
        speed: 350
      }
    }
  },
  plotOptions: {
    radialBar: {
      startAngle: -90,
      endAngle: 90,
      hollow: {
        size: '80%',
      },
      track: {
        background: '#E4E7EC',
        strokeWidth: '100%',
        margin: 5,
      },
      dataLabels: {
        name: {
          show: false,
        },
        value: {
          fontSize: '36px',
          fontWeight: '600',
          offsetY: 60,
          color: '#1D2939',
          formatter: function (val: number) {
            return val.toFixed(2) + '%'
          },
        },
      },
    },
  },
  fill: {
    type: 'gradient',
    gradient: {
      shade: 'dark',
      type: 'horizontal',
      shadeIntensity: 0.5,
      gradientToColors: ['#7FCB97'],
      inverseColors: true,
      opacityFrom: 1,
      opacityTo: 1,
      stops: [0, 100]
    }
  },
  stroke: {
    lineCap: 'round',
    width: 2
  },
  labels: ['Oportunidad'],
  states: {
    hover: {
      filter: {
        type: 'darken',
        value: 0.9
      }
    }
  }
}

onMounted(() => {
  cargarDatos()
})
</script>

<style scoped>
.radial-bar-chart {
  width: 100%;
  max-width: 280px;
  margin: 0 auto;
  transition: transform 0.3s ease;
}

.radial-bar-chart:hover {
  transform: scale(1.05);
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>