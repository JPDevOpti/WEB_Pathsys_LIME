<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <div class="space-y-6">
        <!-- Componente de Modificar Caso -->
        <ComponentCard 
          title="Modificar datos del caso"
          description="Actualice la información del caso existente."
        >
          <template #icon>
            <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </template>
          <EditCaseForm 
            :case-code-prop="caseCodeFromRoute"
            @case-updated="handleCaseUpdated"
          />
        </ComponentCard>
      </div>
      
      <div class="space-y-6">
        <!-- Componente de Modificar Datos del Paciente -->
        <ComponentCard 
          title="Modificar los datos del paciente"
          description="Edite los datos demográficos del paciente asociado."
        >
          <template #icon>
            <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </template>
          <EditPatientForm 
            :case-code-prop="caseCodeFromRoute"
            @patient-updated="handlePatientUpdated"
          />
        </ComponentCard>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { AdminLayout } from '@/shared'
import { PageBreadcrumb, ComponentCard } from '@/shared/components/common'
import { EditCaseForm, EditPatientForm } from '../components'
import type { CaseModel, PatientData } from '../types'

// ============================================================================
// ESTADO DEL COMPONENTE
// ============================================================================

const currentPageTitle = ref('Modificar Caso Médico')

// Obtener el código del caso desde la ruta
const route = useRoute()
const caseCodeFromRoute = computed(() => {
  const code = route.params.code
  return Array.isArray(code) ? code[0] || '' : code || ''
})

// Estado para el caso actual
const currentCase = ref<CaseModel | null>(null)
const currentPatient = ref<PatientData | null>(null)

// ============================================================================
// FUNCIONES PRINCIPALES
// ============================================================================

/**
 * Maneja la actualización exitosa del caso
 */
const handleCaseUpdated = (updatedCase: CaseModel) => {
  currentCase.value = updatedCase
  
  // Aquí puedes agregar lógica adicional como:
  // - Mostrar notificación de éxito
  // - Actualizar estado global
  // - Sincronizar con otros componentes
}

/**
 * Maneja la actualización exitosa del paciente
 */
const handlePatientUpdated = (patientData: PatientData) => {
  currentPatient.value = patientData
  
  // Aquí puedes agregar lógica adicional como:
  // - Mostrar notificación de éxito
  // - Actualizar información del caso si es necesario
  // - Validar consistencia de datos
}
</script> 