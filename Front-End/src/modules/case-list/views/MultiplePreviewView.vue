<template>
  <div class="multiple-preview-view">
    <!-- Header de la vista -->
    <div class="print-hidden bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center gap-4">
            <button
              @click="goBack"
              class="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              Volver
            </button>
            <div class="h-6 w-px bg-gray-300"></div>
            <h1 class="text-lg font-semibold text-gray-900">
              Vista Previa Múltiple
            </h1>
            <span v-if="validCases.length > 0" class="text-sm text-gray-500">
              {{ validCases.length }} caso{{ validCases.length > 1 ? 's' : '' }}
            </span>
          </div>
          
          <div class="flex items-center gap-3">
            <button
              @click="printAllCases"
              :disabled="isLoading || validCases.length === 0 || isPrinting"
              class="inline-flex items-center gap-2 px-3 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium disabled:opacity-50"
            >
              <svg v-if="isPrinting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
              {{ isPrinting ? 'Imprimiendo...' : 'Imprimir Todo' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Contenido principal -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <!-- Estados de error o carga -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <div class="flex items-center gap-3">
          <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 class="text-sm font-medium text-red-800">Error al cargar casos</h3>
            <p class="text-sm text-red-700 mt-1">{{ error }}</p>
          </div>
        </div>
      </div>

      <div v-else-if="validCases.length === 0 && !isLoading" class="text-center py-12">
        <svg class="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No hay casos para mostrar</h3>
        <p class="text-gray-600 mb-4">No se encontraron casos válidos para la vista previa múltiple.</p>
        <button
          @click="goBack"
          class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Volver a la lista
        </button>
      </div>

      <!-- Componente de vista previa múltiple -->
      <PDFMultipleReportPreview
        v-else
        :cases="validCases"
        :show-on-mount="true"
        @close="goBack"
        @print-complete="handlePrintComplete"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Case } from '@/modules/case-list/types/case.types'
import PDFMultipleReportPreview from '@/shared/components/PDFs/PDFMultipleReportPreview.vue'
import { CasesApiService } from '@/modules/cases/services/casesApi.service'

// Services
const casesApiService = new CasesApiService()

// Router y route
const route = useRoute()
const router = useRouter()

// State
const isLoading = ref(false)
const isPrinting = ref(false)
const error = ref<string | null>(null)
const cases = ref<Case[]>([])

// Computed
const validCases = computed(() => {
  return cases.value.filter(c => c && c.id)
})

// Methods
async function loadCases() {
  const caseIdsParam = route.query.cases as string
  
  if (!caseIdsParam) {
    error.value = 'No se especificaron casos para previsualizar'
    return
  }

  isLoading.value = true
  error.value = null

  try {
    const caseIds = caseIdsParam.split(',').filter(Boolean)
    
    if (caseIds.length === 0) {
      error.value = 'No se encontraron IDs de casos válidos'
      return
    }

    console.log('Cargando casos con IDs:', caseIds)
    
    // Cargar cada caso usando el endpoint directo getCaseByCode (igual que single)
    const loaded: Case[] = []
    const fallidos: string[] = []

    for (const code of caseIds) {
      try {
        const fullCase: any = await casesApiService.getCaseByCode(code)
        // Mapear CaseModel -> Case (estructura usada en tablas y PDF múltiple)
        const mapped: Case = {
          id: fullCase._id || code,
          caseCode: fullCase.caso_code || code,
            // primera muestra
          sampleType: fullCase.muestras?.[0]?.region_cuerpo || 'No especificado',
          patient: {
            id: fullCase.paciente?.paciente_code || '',
            // BACKEND no expone cedula en CaseModel; usamos paciente_code como fallback
            dni: fullCase.paciente?.cedula || fullCase.paciente?.paciente_code || '',
            fullName: fullCase.paciente?.nombre || '',
            sex: fullCase.paciente?.sexo || '',
            age: fullCase.paciente?.edad ?? 0,
            entity: fullCase.paciente?.entidad_info?.nombre || fullCase.entidad_info?.nombre || '',
            attentionType: fullCase.paciente?.tipo_atencion || ''
          },
          entity: fullCase.entidad_info?.nombre || fullCase.paciente?.entidad_info?.nombre || '',
          requester: fullCase.medico_solicitante || '',
          status: fullCase.estado || '',
          receivedAt: fullCase.fecha_ingreso || fullCase.fecha_creacion || '',
          deliveredAt: (fullCase as any).fecha_entrega || '',
          signedAt: fullCase.fecha_firma || '',
          tests: (fullCase.muestras || []).flatMap((m: any) => (m.pruebas || []).map((p: any) => p.nombre || p.id)).filter(Boolean),
          pathologist: fullCase.patologo_asignado?.nombre || '',
          servicio: fullCase.servicio || '',
          notes: fullCase.observaciones_generales || '',
          priority: fullCase.prioridad || undefined,
          oportunidad: fullCase.oportunidad || undefined,
          entregado_a: fullCase.entregado_a || undefined,
          result: fullCase.resultado ? {
            method: Array.isArray(fullCase.resultado.metodo) ? fullCase.resultado.metodo.filter((x: string) => x && x.trim()).join(', ') : (fullCase.resultado.metodo || ''),
            macro: fullCase.resultado.resultado_macro || '',
            micro: fullCase.resultado.resultado_micro || '',
            diagnosis: fullCase.resultado.diagnostico || '',
            resultDate: fullCase.fecha_firma || '',
            observaciones: fullCase.resultado.observaciones || '',
            diagnostico_cie10: fullCase.resultado.diagnostico_cie10 || null,
            diagnostico_cieo: fullCase.resultado.diagnostico_cieo || null
          } : undefined,
          subsamples: (fullCase.muestras || []).map((m: any) => ({
            bodyRegion: m.region_cuerpo,
            tests: (m.pruebas || []).map((p: any) => ({ id: p.id, name: p.nombre || p.id, quantity: 1 }))
          }))
        }
        loaded.push(mapped)
      } catch (e) {
        console.error('Fallo cargando', code, e)
        fallidos.push(code)
      }
    }

    if (!loaded.length) {
      error.value = `No se cargó ningún caso: ${caseIds.join(', ')}`
      return
    }
    if (fallidos.length) {
      console.warn('Casos no cargados:', fallidos.join(', '))
    }
    cases.value = loaded
    console.log(`Casos cargados: ${loaded.length}/${caseIds.length}`)
    
  } catch (err) {
    console.error('Error cargando casos:', err)
    error.value = err instanceof Error ? err.message : 'Error desconocido al cargar casos'
  } finally {
    isLoading.value = false
  }
}

async function printAllCases() {
  if (!validCases.value.length || isPrinting.value) return
  
  isPrinting.value = true
  
  try {
    // Usar window.print() para imprimir toda la página
    window.print()
    console.log(`Impresión iniciada para ${validCases.value.length} casos`)
  } catch (err) {
    console.error('Error al imprimir:', err)
  } finally {
    isPrinting.value = false
  }
}

function goBack() {
  // Intentar volver a la página anterior
  if (window.history.length > 1) {
    router.back()
  } else {
    // Fallback a la lista de casos
    router.push('/cases')
  }
}

function handlePrintComplete(count: number) {
  console.log(`Impresión completada: ${count} casos`)
  // Aquí podrías mostrar una notificación de éxito
}

// Lifecycle
onMounted(() => {
  loadCases()
})
</script>

<style scoped>
.multiple-preview-view {
  min-height: 100vh;
  background-color: #f9fafb;
}

/* Mejoras para impresión */
@media print {
  .print-hidden {
    display: none !important;
  }
  
  .multiple-preview-view {
    background: white;
    min-height: auto;
  }
}
</style>
