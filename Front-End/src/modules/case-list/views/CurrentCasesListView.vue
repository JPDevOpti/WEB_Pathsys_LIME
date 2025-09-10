<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="pageTitle" />
    <div class="space-y-4">


      <Card v-if="isLoading">
        <div class="p-8 text-center">
          <LoadingSpinner />
        </div>
      </Card>

      <Card v-else-if="error">
        <div class="p-8 text-center">
          <p class="text-red-600 mb-4">{{ error }}</p>
          <BaseButton size="sm" variant="primary" @click="reload">Reintentar</BaseButton>
        </div>
      </Card>

      <template v-else>
        <FiltersBar v-model="filters" :totalFiltered="filteredCases.length" :totalAll="cases.length"
          :isLoading="isLoading" :canExport="filteredCases.length > 0" @refresh="reload" @export="exportExcel" />

        <div class="bg-white rounded-xl border border-gray-200">
          <CasesTable :cases="paginatedCases" :selected-ids="selectedCaseIds" :is-all-selected="isAllSelected"
            :columns="columns" :sort-key="sortKey" :sort-order="sortOrder" :current-page="currentPage"
            :total-pages="totalPages" :items-per-page="itemsPerPage" :total-items="filteredCases.length"
            :no-results-message="hasActiveFilters ? 'No se encontraron casos con los filtros aplicados' : 'No hay casos disponibles'"
            @toggle-select="toggleSelect" @toggle-select-all="toggleSelectAll" @clear-selection="selectedCaseIds = []"
            @sort="(k: any) => sortBy(k)" @show-details="showDetails" @edit="editCase" @validate="validateCase"
            @perform="performCase" @update-items-per-page="(v: number) => itemsPerPage = v"
            @prev-page="() => currentPage--" @next-page="() => currentPage++" @refresh="reload" />
        </div>

        <CaseDetailsModal :case-item="selectedCase" @close="closeDetails" @edit="editCase" @preview="previewCase" @notes="handleNotesUpdate" />
      </template>
    </div>
  </AdminLayout>

</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { AdminLayout } from '@/shared/components/layout'
import { useRouter } from 'vue-router'
import PageBreadcrumb from '@/shared/components/navigation/PageBreadcrumb.vue'
import Card from '@/shared/components/layout/Card.vue'
import { BaseButton } from '@/shared/components'
import LoadingSpinner from '@/shared/components/feedback/LoadingSpinner.vue'

import FiltersBar from '../components/FiltersBar.vue'
import CasesTable from '../components/CasesTable.vue'
import CaseDetailsModal from '../components/CaseDetailsModal.vue'

import { useCaseList } from '../composables/useCaseList'
import { useExcelExport } from '../composables/useExcelExport'
import { signatureService } from '@/shared/services/signatureService'

const pageTitle = 'Casos Actuales'

const {
  // state
  cases,
  isLoading,
  error,
  filters,
  sortKey,
  sortOrder,
  currentPage,
  itemsPerPage,
  selectedCaseIds,
  selectedCase,
  // derived
  filteredCases,
  paginatedCases,
  totalPages,
  isAllSelected,
  // actions
  loadCases,
  toggleSelectAll,
  toggleSelect,
  sortBy,
  showDetails,
  closeDetails,
  validateCase,
} = useCaseList()

const { exportCasesToExcel } = useExcelExport()
const router = useRouter()

const columns = [
  { key: 'caseCode', label: 'Código Caso', class: 'w-[12%]' },
  { key: 'patient', label: 'Paciente', class: 'w-[18%]' },
  { key: 'entity', label: 'Entidad / Patólogo', class: 'w-[20%]' },
  { key: 'tests', label: 'Pruebas', class: 'w-[15%]' },
  { key: 'status', label: 'Estado', class: 'w-[10%]' },
  { key: 'dates', label: 'Creación/Firma', class: 'w-[12%]' },
  { key: 'priority', label: 'Prioridad/Días', class: 'w-[10%]' },
  { key: 'actions', label: 'Acciones', class: 'w-[8%]' },
]

const hasActiveFilters = computed(() => {
  return !!(
    filters.value.searchQuery ||
    filters.value.searchPathologist ||
    filters.value.dateFrom ||
    filters.value.dateTo ||
    filters.value.selectedEntity ||
    filters.value.selectedStatus ||
    filters.value.selectedTest
  )
})

function reload() { loadCases() }
function exportExcel() { exportCasesToExcel(filteredCases.value) }
function performCase(_c: any) { /* navegación se integrará luego */ }
function editCase(c: any) {
  const code = c?.caseCode || c?.id || ''
  if (!code) return
  // Navega a la vista de edición con el código en la URL
  router.push({ name: 'cases-edit-with-code', params: { code }, query: { auto: '1' } })
}

// Listener para detectar cuando se crea un nuevo caso
const handleCaseCreated = (_event: CustomEvent) => {
  loadCases()
}

onMounted(() => {
  // Agregar listener para eventos de creación de casos
  window.addEventListener('case-created', handleCaseCreated as EventListener)
})

onUnmounted(() => {
  // Limpiar listener al desmontar el componente
  window.removeEventListener('case-created', handleCaseCreated as EventListener)
})

function previewCase(c: any) {
  // DEBUG: Ver datos originales del caso
  console.log('CurrentCasesListView - caso original:', c)
  console.log('CurrentCasesListView - patologo_asignado original:', c.patologo_asignado)
  console.log('CurrentCasesListView - pathologist:', c.pathologist)
  
  navigateToPreview(c)
}

function handleNotesUpdate(updatedCase: any) {
  // Buscar por caso_code si no hay caseCode
  const caseCode = updatedCase.caseCode || updatedCase.caso_code
  
  // Actualizar solo las notas adicionales en la lista local
  const caseIndex = cases.value.findIndex(c => (c.caseCode || c.caso_code) === caseCode)
  if (caseIndex !== -1) {
    // Solo actualizar las notas adicionales, mantener el resto del caso intacto
    cases.value[caseIndex] = {
      ...cases.value[caseIndex],
      notas_adicionales: updatedCase.notas_adicionales
    }
  }
  
  // Si el caso actual es el mismo que se actualizó, actualizar solo las notas en selectedCase
  if ((selectedCase.value?.caseCode || selectedCase.value?.caso_code) === caseCode) {
    selectedCase.value = {
      ...selectedCase.value,
      notas_adicionales: updatedCase.notas_adicionales
    }
  }
}

async function navigateToPreview(c: any) {
  
  // Obtener la firma del patólogo - usar directamente la que viene del backend
  let patologoFirma = undefined
  const patologoCode = c.patologo_asignado?.codigo || c.pathologist?.codigo || c.patologo_asignado?.patologo_code
  
  // DEBUG: Log completo del caso para entender la estructura
  console.log('CurrentCasesListView - DEBUG caso completo:', c)
  console.log('CurrentCasesListView - DEBUG patologo_asignado:', c.patologo_asignado)
  console.log('CurrentCasesListView - DEBUG patologoCode:', patologoCode)
  console.log('CurrentCasesListView - DEBUG fecha_firma:', c.signedAt || (c as any).fecha_firma)
  console.log('CurrentCasesListView - DEBUG estado:', c.status)
  
  // Usar la firma que viene directamente del backend
  if (c.patologo_asignado?.firma) {
    patologoFirma = c.patologo_asignado.firma
    console.log('CurrentCasesListView - FIRMA ENCONTRADA EN EL CASO:', patologoFirma ? 'SÍ' : 'NO')
  } else {
    console.log('CurrentCasesListView - NO HAY FIRMA EN EL CASO')
  }
  
  const payload = {
    sampleId: c.caseCode || c.caso_code || c.id,
    patient: {
      document: c.patient?.dni || c.paciente?.cedula || '',
      fullName: c.patient?.fullName || c.paciente?.nombre || '',
      age: c.patient?.age || c.paciente?.edad || '',
      gender: c.patient?.sex || c.paciente?.sexo || '',
      entity: c.patient?.entity || c.paciente?.entidad_info?.nombre || ''
    },
    caseDetails: {
      caso_code: c.caseCode || c.caso_code || c.id || '',
      fecha_creacion: c.receivedAt || (c as any).fecha_creacion || '',
      fecha_entrega: c.deliveredAt || (c as any).fecha_entrega || '',
      fecha_firma: (c as any).signedAt || c.deliveredAt || (c as any).fecha_firma || null,
      patologo_asignado: c.pathologist ? { 
        nombre: c.pathologist,
        // Buscar firma en múltiples posibles ubicaciones
        firma: (c as any).patologo_asignado?.firma || (c as any).pathologist_signature || (c as any).firma || undefined
      } : (c.patologo_asignado ? {
        ...c.patologo_asignado,
        firma: (c.patologo_asignado as any)?.firma || (c as any).pathologist_signature || (c as any).firma || undefined
      } : undefined),
      medico_solicitante: c.requester ? { nombre: c.requester } : c.medico_solicitante || undefined,
      entidad_info: c.patient?.entity ? { nombre: c.patient.entity } : c.paciente?.entidad_info || undefined,
      muestras: Array.isArray(c.subsamples) ? c.subsamples.map((s: any) => ({
        region_cuerpo: s.bodyRegion,
        pruebas: Array.isArray(s.tests) ? s.tests.map((t: any) => ({
          id: t.id,
          nombre: t.name || t.id
        })) : []
      })) : Array.isArray(c.muestras) ? c.muestras.map((m: any) => ({
        region_cuerpo: m.region_cuerpo,
        pruebas: Array.isArray(m.pruebas) ? m.pruebas.map((p: any) => ({
          id: p.id,
          nombre: p.nombre || p.id
        })) : []
      })) : []
    },
    sections: {
      method: c.result?.method || c.resultado?.metodo || '',
      macro: c.result?.macro || c.resultado?.resultado_macro || '',
      micro: c.result?.micro || c.resultado?.resultado_micro || '',
      diagnosis: c.result?.diagnosis || c.resultado?.diagnostico || ''
    },
    diagnosis: {
      cie10: c.result?.diagnostico_cie10 ? {
        primary: c.result.diagnostico_cie10,
        formatted: c.result.diagnostico_cie10?.codigo && c.result.diagnostico_cie10?.nombre
          ? `${c.result.diagnostico_cie10.codigo} - ${c.result.diagnostico_cie10.nombre}`
          : ''
      } : undefined,
      cieo: c.result?.diagnostico_cieo ? {
        primary: c.result.diagnostico_cieo,
        formatted: c.result.diagnostico_cieo?.codigo && c.result.diagnostico_cieo?.nombre
          ? `${c.result.diagnostico_cieo.codigo} - ${c.result.diagnostico_cieo.nombre}`
          : ''
      } : undefined,
      formatted: c.result?.diagnostico_cie10?.codigo && c.result?.diagnostico_cie10?.nombre
        ? `${c.result.diagnostico_cie10.codigo} - ${c.result.diagnostico_cie10.nombre}`
        : (c.result?.diagnosis || c.resultado?.diagnostico || '')
    },
    generatedAt: new Date().toISOString()
  }
  
  const completePayload = {
    sampleId: payload.sampleId,
    patient: {
      document: payload.patient.document,
      fullName: payload.patient.fullName,
      age: payload.patient.age,
      gender: payload.patient.gender,
      entity: payload.patient.entity
    },
    caseDetails: {
      caso_code: payload.caseDetails.caso_code,
      fecha_creacion: payload.caseDetails.fecha_creacion,
      fecha_entrega: payload.caseDetails.fecha_entrega,
      fecha_firma: payload.caseDetails.fecha_firma,
      patologo_asignado: payload.caseDetails.patologo_asignado ? {
        ...payload.caseDetails.patologo_asignado,
        // Usar la firma que viene del backend
        firma: patologoFirma || undefined
      } : undefined,
      medico_solicitante: payload.caseDetails.medico_solicitante,
      entidad_info: payload.caseDetails.entidad_info,
      muestras: payload.caseDetails.muestras,
      paciente: {
        codigo: c.patient?.id || c.paciente?.codigo || '',
        nombre: c.patient?.fullName || c.paciente?.nombre || '',
        edad: c.patient?.age || c.paciente?.edad || 0,
        sexo: c.patient?.sex || c.paciente?.sexo || '',
        entidad_info: c.patient?.entity ? {
          codigo: c.paciente?.entidad_info?.codigo || '',
          nombre: c.patient.entity
        } : c.paciente?.entidad_info || undefined,
        tipo_atencion: c.patient?.attentionType || c.paciente?.tipo_atencion || '',
        cedula: c.patient?.dni || c.paciente?.cedula || '',
        observaciones: c.patient?.notes || c.paciente?.observaciones || '',
        fecha_actualizacion: c.patient?.updatedAt || c.paciente?.fecha_actualizacion || new Date().toISOString()
      },
      servicio: c.servicio || c.paciente?.servicio || undefined,
      estado: c.status || c.estado || '',
  fecha_ingreso: c.receivedAt || (c as any).fecha_creacion || '',
      fecha_actualizacion: c.patient?.updatedAt || c.paciente?.fecha_actualizacion || new Date().toISOString(),
      observaciones_generales: c.notes || c.observaciones_generales || '',
      is_active: c.is_active ?? true,
      actualizado_por: c.actualizado_por || 'sistema'
    },
    sections: payload.sections,
    diagnosis: payload.diagnosis,
    generatedAt: payload.generatedAt
  }
  
  // DEBUG: Ver payload final antes de guardarlo
  console.log('CurrentCasesListView - payload final completo:', completePayload)
  console.log('CurrentCasesListView - patologo_asignado en payload final:', completePayload.caseDetails.patologo_asignado)
  console.log('CurrentCasesListView - firma en payload final:', completePayload.caseDetails.patologo_asignado?.firma)
  
  try {
    sessionStorage.setItem('results_preview_payload', JSON.stringify(completePayload))
  } catch { }
  router.push({ name: 'results-preview' })
}

</script>
