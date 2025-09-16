<template>
  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 md:gap-6">
    <Card class="group p-4 md:p-4 relative">
      <div class="flex items-center gap-4">
        <div class="flex items-center justify-center w-10 h-10 bg-gray-100 rounded-lg transition-colors duration-300 group-hover:bg-blue-50">
          <svg class="fill-gray-800 transition-colors duration-300 group-hover:fill-blue-600" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" clip-rule="evenodd" d="M8.80443 5.60156C7.59109 5.60156 6.60749 6.58517 6.60749 7.79851C6.60749 9.01185 7.59109 9.99545 8.80443 9.99545C10.0178 9.99545 11.0014 9.01185 11.0014 7.79851C11.0014 6.58517 10.0178 5.60156 8.80443 5.60156ZM5.10749 7.79851C5.10749 5.75674 6.76267 4.10156 8.80443 4.10156C10.8462 4.10156 12.5014 5.75674 12.5014 7.79851C12.5014 9.84027 10.8462 11.4955 8.80443 11.4955C6.76267 11.4955 5.10749 9.84027 5.10749 7.79851ZM4.86252 15.3208C4.08769 16.0881 3.70377 17.0608 3.51705 17.8611C3.48384 18.0034 3.5211 18.1175 3.60712 18.2112C3.70161 18.3141 3.86659 18.3987 4.07591 18.3987H13.4249C13.6343 18.3987 13.7992 18.3141 13.8937 18.2112C13.9797 18.1175 14.017 18.0034 13.9838 17.8611C13.7971 17.0608 13.4132 16.0881 12.6383 15.3208C11.8821 14.572 10.6899 13.955 8.75042 13.955C6.81096 13.955 5.61877 14.572 4.86252 15.3208ZM3.8071 14.2549C4.87163 13.2009 6.45602 12.455 8.75042 12.455C11.0448 12.455 12.6292 13.2009 13.6937 14.2549C14.7397 15.2906 15.2207 16.5607 15.4446 17.5202C15.7658 18.8971 14.6071 19.8987 13.4249 19.8987H4.07591C2.89369 19.8987 1.73504 18.8971 2.05628 17.5202C2.28015 16.5607 2.76117 15.2906 3.8071 14.2549ZM15.3042 11.4955C14.4702 11.4955 13.7006 11.2193 13.0821 10.7533C13.3742 10.3314 13.6054 9.86419 13.7632 9.36432C14.1597 9.75463 14.7039 9.99545 15.3042 9.99545C16.5176 9.99545 17.5012 9.01185 17.5012 7.79851C17.5012 6.58517 16.5176 5.60156 15.3042 5.60156C14.7039 5.60156 14.1597 5.84239 13.7632 6.23271C13.6054 5.73284 13.3741 5.26561 13.082 4.84371C13.7006 4.37777 14.4702 4.10156 15.3042 4.10156C17.346 4.10156 19.0012 5.75674 19.0012 7.79851C19.0012 9.84027 17.346 11.4955 15.3042 11.4955ZM19.9248 19.8987H16.3901C16.7014 19.4736 16.9159 18.969 16.9827 18.3987H19.9248C20.1341 18.3987 20.2991 18.3141 20.3936 18.2112C20.4796 18.1175 20.5169 18.0034 20.4837 17.861C20.2969 17.0607 19.913 16.088 19.1382 15.3208C18.4047 14.5945 17.261 13.9921 15.4231 13.9566C15.2232 13.6945 14.9995 13.437 14.7491 13.1891C14.5144 12.9566 14.262 12.7384 13.9916 12.5362C14.3853 12.4831 14.8044 12.4549 15.2503 12.4549C17.5447 12.4549 19.1291 13.2008 20.1936 14.2549C21.2395 15.2906 21.7206 16.5607 21.9444 17.5202C22.2657 18.8971 21.107 19.8987 19.9248 19.8987Z" fill=""/>
          </svg>
        </div>
        <div>
          <span class="text-xs text-gray-500 transition-colors duration-300 group-hover:text-gray-700">
            {{ esPatologo ? 'Pacientes tratados este mes' : 'Pacientes ingresados el mes actual' }}
          </span>
          <h4 class="mt-1 font-bold text-gray-800 text-lg transition-colors duration-300 group-hover:text-blue-600">
            {{ isLoading ? '...' : formatearNumero(pacientesMesActual) }}
          </h4>
        </div>
      </div>
      <span v-if="!isLoading && metricas?.pacientes" :class="obtenerClasePorcentaje(pacientesCambio)" class="absolute bottom-2 right-2 flex items-center gap-1 rounded-full py-0.5 pl-2 pr-2.5 text-xs font-medium transition-all duration-300">
        <svg class="fill-current animate-bounce" width="10" height="10" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path v-if="pacientesCambio >= 0" fill-rule="evenodd" clip-rule="evenodd" d="M5.56462 1.62393C5.70193 1.47072 5.90135 1.37432 6.12329 1.37432C6.1236 1.37432 6.12391 1.37432 6.12422 1.37432C6.31631 1.37415 6.50845 1.44731 6.65505 1.59381L9.65514 4.5918C9.94814 4.88459 9.94831 5.35947 9.65552 5.65246C9.36273 5.94546 8.88785 5.94562 8.59486 5.65283L6.87329 3.93247L6.87329 10.125C6.87329 10.5392 6.53751 10.875 6.12329 10.875C5.70908 10.875 5.37329 10.5392 5.37329 10.125L5.37329 3.93578L3.65516 5.65282C3.36218 5.94562 2.8873 5.94547 2.5945 5.65248C2.3017 5.35949 2.30185 4.88462 2.59484 4.59182L5.56462 1.62393Z" fill=""/>
          <path v-else fill-rule="evenodd" clip-rule="evenodd" d="M5.31462 10.3761C5.45194 10.5293 5.65136 10.6257 5.87329 10.6257C5.8736 10.6257 5.8739 10.6257 5.87421 10.6257C6.0663 10.6259 6.25845 10.5527 6.40505 10.4062L9.40514 7.4082C9.69814 7.11541 9.69831 6.64054 9.40552 6.34754C9.11273 6.05454 8.63785 6.05438 8.34486 6.34717L6.62329 8.06753L6.62329 1.875C6.62329 1.46079 6.28751 1.125 5.87329 1.125C5.45908 1.125 5.12329 1.46079 5.12329 1.875L5.12329 8.06422L3.40516 6.34719C3.11218 6.05439 2.6373 6.05454 2.3445 6.34752C2.0517 6.64051 2.05185 7.11538 2.34484 7.40818L5.31462 10.3761Z" fill=""/>
        </svg>
        {{ Math.abs(pacientesCambio).toFixed(1) }}%
      </span>
    </Card>

    <Card class="group p-4 md:p-4 relative">
      <div class="flex items-center gap-4">
        <div class="flex items-center justify-center w-10 h-10 bg-gray-100 rounded-lg transition-colors duration-300 group-hover:bg-blue-50">
          <MuestraIcon class="w-5 h-5 text-gray-800 transition-colors duration-300 group-hover:text-blue-600" />
        </div>
        <div>
          <span class="text-xs text-gray-500 transition-colors duration-300 group-hover:text-gray-700">
            {{ esPatologo ? 'Casos asignados este mes' : 'Casos ingresados mes el actual' }}
          </span>
          <h4 class="mt-1 font-bold text-gray-800 text-lg transition-colors duration-300 group-hover:text-blue-600">
            {{ isLoading ? '...' : formatearNumero(casosMesActual) }}
          </h4>
        </div>
      </div>
      <span v-if="!isLoading && metricas?.casos" :class="obtenerClasePorcentaje(casosCambio)" class="absolute bottom-2 right-2 flex items-center gap-1 rounded-full py-0.5 pl-2 pr-2.5 text-xs font-medium transition-all duration-300">
        <svg class="fill-current animate-bounce" width="10" height="10" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path v-if="casosCambio >= 0" fill-rule="evenodd" clip-rule="evenodd" d="M5.56462 1.62393C5.70193 1.47072 5.90135 1.37432 6.12329 1.37432C6.1236 1.37432 6.12391 1.37432 6.12422 1.37432C6.31631 1.37415 6.50845 1.44731 6.65505 1.59381L9.65514 4.5918C9.94814 4.88459 9.94831 5.35947 9.65552 5.65246C9.36273 5.94546 8.88785 5.94562 8.59486 5.65283L6.87329 3.93247L6.87329 10.125C6.87329 10.5392 6.53751 10.875 6.12329 10.875C5.70908 10.875 5.37329 10.5392 5.37329 10.125L5.37329 3.93578L3.65516 5.65282C3.36218 5.94562 2.8873 5.94547 2.5945 5.65248C2.3017 5.35949 2.30185 4.88462 2.59484 4.59182L5.56462 1.62393Z" fill=""/>
          <path v-else fill-rule="evenodd" clip-rule="evenodd" d="M5.31462 10.3761C5.45194 10.5293 5.65136 10.6257 5.87329 10.6257C5.8736 10.6257 5.8739 10.6257 5.87421 10.6257C6.0663 10.6259 6.25845 10.5527 6.40505 10.4062L9.40514 7.4082C9.69814 7.11541 9.69831 6.64054 9.40552 6.34754C9.11273 6.05454 8.63785 6.05438 8.34486 6.34717L6.62329 8.06753L6.62329 1.875C6.62329 1.46079 6.28751 1.125 5.87329 1.125C5.45908 1.125 5.12329 1.46079 5.12329 1.875L5.12329 8.06422L3.40516 6.34719C3.11218 6.05439 2.6373 6.05454 2.3445 6.34752C2.0517 6.64051 2.05185 7.11538 2.34484 7.40818L5.31462 10.3761Z" fill=""/>
        </svg>
        {{ Math.abs(casosCambio).toFixed(1) }}%
      </span>
    </Card>

    <div v-if="error" class="col-span-full p-4 bg-red-50 border border-red-200 rounded-lg text-red-600">
      <p class="text-sm"><strong>Error al cargar estadísticas:</strong> {{ error }}</p>
      <button @click="cargarEstadisticas" class="mt-2 text-xs underline hover:no-underline">Reintentar</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { MuestraIcon } from '@/assets/icons'
import { onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { Card } from '@/shared/components/layout'
import { formatearNumero, obtenerClasePorcentaje } from '@/shared'
import { useDashboard } from '../composables/useDashboard'
import { useAuthStore } from '@/stores/auth.store'

const authStore = useAuthStore()
const { metricas, casosPorMes, loadingMetricas: isLoading, error, cargarMetricas, cargarCasosPorMes } = useDashboard()

const esPatologo = computed(() => authStore.user?.rol === 'patologo' && authStore.userRole !== 'administrador')
const pacientesMesActual = computed(() => Number(metricas.value?.pacientes?.mes_actual ?? 0))
const pacientesCambio = computed(() => {
  const mesAnt = Number(metricas.value?.pacientes?.mes_anterior ?? 0)
  const mesAntAnt = (metricas.value as any)?.pacientes?.mes_anterior_anterior
  if (typeof mesAntAnt === 'number') {
    const denom = mesAntAnt === 0 ? 1 : mesAntAnt
    return Math.round(((mesAnt - mesAntAnt) / denom) * 100)
  }
  return Number(metricas.value?.pacientes?.cambio_porcentual ?? 0)
})

const casosMesActual = computed(() => {
  if (esPatologo.value) return Number(metricas.value?.casos?.mes_actual ?? 0)
  const serie = casosPorMes.value?.datos
  if (Array.isArray(serie) && serie.length === 12) {
    const now = new Date()
    const m = now.getMonth()
    return serie[m] || 0
  }
  return Number(metricas.value?.casos?.mes_actual ?? 0)
})

const casosCambio = computed(() => {
  const backendCambio = Number(metricas.value?.casos?.cambio_porcentual ?? 0)
  if (esPatologo.value) return backendCambio
  if (backendCambio !== 0) return backendCambio
  const serie = casosPorMes.value?.datos
  if (Array.isArray(serie) && serie.length === 12) {
    const now = new Date()
    const m = now.getMonth()
    if (m >= 2) {
      const mesAnterior = serie[m - 1] || 0
      const mesAnteriorAnterior = serie[m - 2] || 0
      const denom = mesAnteriorAnterior === 0 ? 1 : mesAnteriorAnterior
      return Math.round(((mesAnterior - mesAnteriorAnterior) / denom) * 100)
    }
  }
  return backendCambio
})

const cargarEstadisticas = async () => {
  if (!authStore.user) return
  await Promise.all([cargarMetricas(esPatologo.value), cargarCasosPorMes(undefined, esPatologo.value)])
}

watch(() => authStore.user, (newUser) => { if (newUser) cargarEstadisticas() }, { immediate: true })
// Refresh helpers
const handleCaseCreated = () => cargarEstadisticas()
const handlePatientCreated = () => cargarEstadisticas()

onMounted(() => {
  cargarEstadisticas()
  window.addEventListener('case-created', handleCaseCreated as EventListener)
  window.addEventListener('patient-created', handlePatientCreated as EventListener)
})

onBeforeUnmount(() => {
  window.removeEventListener('case-created', handleCaseCreated as EventListener)
  window.removeEventListener('patient-created', handlePatientCreated as EventListener)
})
</script>

<style scoped>
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.animate-pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
</style>