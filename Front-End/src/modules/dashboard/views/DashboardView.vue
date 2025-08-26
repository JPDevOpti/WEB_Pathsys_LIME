<template>
  <AdminLayout>
    <div class="grid grid-cols-12 gap-4 md:gap-6 p-6 bg-gray-50 min-h-screen">
      <!-- Columna izquierda: Métricas y Casos por mes -->
      <div class="col-span-12 space-y-4 xl:col-span-7">
        <!-- Bloque de métricas (pacientes y casos) -->
        <div class="flex-shrink-0">
          <MetricsBlocks />
        </div>
        
        <!-- Casos por mes (más alto, más importante) -->
        <div class="flex-1">
          <CasesByMonth />
        </div>
      </div>
      
      <!-- Columna derecha: Progreso (misma altura que la columna izquierda) -->
      <div class="col-span-12 xl:col-span-5">
        <div class="h-full">
          <ProgressPercentage />
        </div>
      </div>
      
      <!-- Fila completa: Casos urgentes -->
      <div class="col-span-12">
        <UrgentCases 
          @show-details="handleShowDetails"
          @edit="handleEdit"
          @perform="handlePerform"
          @validate="handleValidate"
        />
      </div>
    </div>

    <!-- Modal de detalles del caso urgente -->
    <UrgentCaseDetailsModal 
      :case-item="selectedUrgentCase" 
      @close="closeUrgentCaseDetails" 
      @edit="handleEdit" 
      @preview="handlePerform" 
    />
  </AdminLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AdminLayout from '@/shared/layouts/AdminLayout.vue'
import MetricsBlocks from '../components/MetricsBlocks.vue'
import CasesByMonth from '../components/CasesByMonth.vue'
import UrgentCases from '../components/UrgentCases.vue'
import ProgressPercentage from '../components/ProgressPercentage.vue'
import UrgentCaseDetailsModal from '../components/UrgentCaseDetailsModal.vue'

import { useDashboard } from '../composables/useDashboard'
import { testBackendConnection } from '../utils/testConnection'
import type { CasoUrgente } from '../types/dashboard.types'

// Usar el composable del dashboard para cargar datos iniciales
const { cargarTodosDatos } = useDashboard()

// Router para navegación
const router = useRouter()

// Estado para el modal de detalles
const selectedUrgentCase = ref<CasoUrgente | null>(null)

// Funciones manejadoras para los eventos de UrgentCases
function handleShowDetails(caso: CasoUrgente) {
  selectedUrgentCase.value = caso
}

function closeUrgentCaseDetails() {
  selectedUrgentCase.value = null
}

function handleEdit(caso: CasoUrgente) {
  // Navegar a la edición del caso
  router.push(`/cases/edit/${caso.codigo}`)
}

function handlePerform(caso: CasoUrgente) {
  // Navegar a realizar resultados
  router.push(`/results/perform?case=${caso.codigo}`)
}

function handleValidate(caso: CasoUrgente) {
  // Navegar a validar el caso
  router.push(`/results/sign?case=${caso.codigo}`)
}

// Cargar todos los datos del dashboard al montar la vista
onMounted(async () => {
  // Probar conexión con el backend
  await testBackendConnection()
  
  // Los componentes individuales cargarán sus propios datos
  // pero podríamos usar cargarTodosDatos() para una carga centralizada
})
</script>

<style scoped>
/* Asegurar que las columnas tengan la misma altura en desktop */
@media (min-width: 1280px) {
  .xl\:col-span-7 {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  
  .xl\:col-span-5 {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  
  /* Métricas: altura fija más pequeña */
  .xl\:col-span-7 .flex-shrink-0 {
    flex: 0 0 auto;
  }
  
  /* Casos por mes: ocupa el espacio restante */
  .xl\:col-span-7 .flex-1 {
    flex: 1 1 auto;
    min-height: 0;
  }
  
  .xl\:col-span-5 > * {
    flex: 1;
  }
}

/* Animaciones suaves para las transiciones */
.grid {
  transition: all 0.3s ease-in-out;
}

/* Efecto hover sutil en las tarjetas */
.grid > div > * {
  transition: transform 0.2s ease-in-out;
}

.grid > div > *:hover {
  transform: translateY(-2px);
}
</style>