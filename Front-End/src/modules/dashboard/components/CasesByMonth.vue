<template>
  <Card class="overflow-hidden px-5 pt-5 sm:px-6 sm:pt-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-800">
        {{ esPatologo ? 'Casos asignados por mes' : 'Casos ingresados por mes' }} ({{ anioActual }})
      </h3>
      <button @click="cargarEstadisticas(true)" :disabled="isLoading" class="p-2 text-gray-500 hover:text-blue-600 disabled:opacity-50 rounded-lg hover:bg-gray-100 transition-colors" title="Actualizar datos" aria-label="Actualizar datos">
        <svg class="w-4 h-4" :class="{ 'animate-spin': isLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>
    </div>

    <OptimizedLoader v-if="isLoading" :message="loadingMessage" :show-pulse="true" size="md" />

    <div v-else-if="localError" class="flex items-center justify-center py-8">
      <div class="flex flex-col items-center space-y-3">
        <svg class="h-8 w-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-sm text-red-500">{{ localError }}</p>
        <button @click="cargarEstadisticas(true)" class="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">Intentar nuevamente</button>
      </div>
    </div>

    <div v-else-if="totalCasosAño > 0" class="max-w-full overflow-x-auto custom-scrollbar">
      <div class="-ml-5 min-w-[650px] xl:min-w-full pl-2">
        <VueApexCharts v-if="chartReady" type="bar" height="180" :options="chartOptions" :series="series" :key="chartKey" />
        <div v-else class="h-[180px] flex items-center justify-center">
          <div class="text-gray-400 text-sm">Preparando gráfico...</div>
        </div>
      </div>
    </div>
    
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
  </Card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import { Card } from '@/shared/components/layout'
import OptimizedLoader from '@/shared/components/ui/OptimizedLoader.vue'
import { useDashboard } from '../composables/useDashboard'
import { useAuthStore } from '@/stores/auth.store'

const authStore = useAuthStore()
const { casosPorMes, loadingCasosPorMes: isLoading, cargarCasosPorMes, totalCasosAño, añoActual: anioActual } = useDashboard()

const chartReady = ref(false)
const chartKey = ref(0)
const loadingMessage = ref('Cargando estadísticas...')
const lastLoadTime = ref(0)
const localError = ref<string | null>(null)

const esPatologo = computed(() => authStore.user?.rol === 'patologo' && authStore.userRole !== 'administrador')

const series = computed(() => [{
  name: esPatologo.value ? 'Casos asignados' : 'Casos',
  data: Array.isArray(casosPorMes.value?.datos) ? casosPorMes.value.datos : Array(12).fill(0)
}])

const chartOptions = ref({
  colors: ['#3D8D5B'],
  chart: { fontFamily: 'Outfit, sans-serif', type: 'bar', toolbar: { show: false }, animations: { enabled: true, easing: 'easeinout', speed: 800, animateGradually: { enabled: true, delay: 150 } } },
  plotOptions: { bar: { horizontal: false, columnWidth: '39%', borderRadius: 5, borderRadiusApplication: 'end' } },
  dataLabels: { enabled: false },
  stroke: { show: true, width: 4, colors: ['transparent'] },
  xaxis: { categories: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'], axisBorder: { show: false }, axisTicks: { show: false } },
  legend: { show: true, position: 'top', horizontalAlign: 'left', fontFamily: 'Outfit', markers: { radius: 99 } },
  yaxis: { title: false },
  grid: { yaxis: { lines: { show: true } } },
  fill: { opacity: 1 },
  tooltip: { x: { show: false }, y: { formatter: (val: any) => val.toString() } }
})

const cargarEstadisticas = async (forceRefresh = false) => {
  const now = Date.now()
  if (now - lastLoadTime.value < 500 && !forceRefresh) return
  lastLoadTime.value = now

  try {
    localError.value = null
    loadingMessage.value = esPatologo.value ? 'Cargando casos asignados...' : 'Cargando casos del laboratorio...'
    chartReady.value = false
    await cargarCasosPorMes(anioActual.value, esPatologo.value)
    await nextTick()
    chartReady.value = true
    chartKey.value++
  } catch (e: any) {
    localError.value = e?.message || 'Error al cargar estadísticas de casos por mes'
    chartReady.value = false
  }
}

watch(esPatologo, () => cargarEstadisticas(true), { immediate: false })
onMounted(() => cargarEstadisticas())
</script>

<style scoped>
.custom-scrollbar { scrollbar-width: thin; scrollbar-color: #CBD5E1 transparent; }
.custom-scrollbar::-webkit-scrollbar { height: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #CBD5E1; border-radius: 3px; }
</style> 