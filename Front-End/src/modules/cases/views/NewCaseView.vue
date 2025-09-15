<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="p-6">
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div class="space-y-6">
          <!-- Componente de Nuevo Caso -->
          <NewCase 
            ref="newCaseRef"
            @case-saved="handleCaseSaved"
            @patient-verified="handlePatientVerified"
          />
          
          <!-- Componente de Asignar Patólogo -->
          <CasePathologist 
            :case-to-assign="currentCase"
          />
        </div>
        
        <div class="space-y-6">
          <!-- Componente de Nuevo Paciente -->
          <NewPatient 
            @patient-saved="handlePatientSaved"
            @update-patient-data="handlePatientDataUpdate"
          />
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { AdminLayout } from '@/shared'
import { PageBreadcrumb } from '@/shared/components/navigation'
import { NewPatient, NewCase, CasePathologist } from '../components'
import type { PatientData } from '../types'

// ============================================================================
// ESTADO DEL COMPONENTE
// ============================================================================

const currentPageTitle = ref('Nuevo Caso Médico')

// Referencias a los componentes
const newCaseRef = ref()

// Estado para el caso actual
const currentCase = ref(null)
const currentPatient = ref<PatientData | null>(null)

// ============================================================================
// FUNCIONES PRINCIPALES
// ============================================================================

/**
 * Función que se ejecuta cuando se guarda un nuevo paciente
 */
const handlePatientSaved = (patientData: PatientData) => {
  // Actualizar paciente actual
  currentPatient.value = patientData
  
  // Notificar al componente NewCase para que use este paciente
  if (newCaseRef.value && newCaseRef.value.handleNewPatient) {
    newCaseRef.value.handleNewPatient(patientData)
  }
}

/**
 * Función para manejar actualizaciones de datos del paciente
 */
const handlePatientDataUpdate = (patientData: PatientData) => {
  // Aquí podrías agregar lógica como:
  // - Sincronizar con otros componentes
  // - Validar datos en tiempo real
  // - Actualizar vista previa de datos
}

/**
 * Función que se ejecuta cuando se verifica un paciente en NewCase
 */
const handlePatientVerified = (patientData: PatientData) => {
  currentPatient.value = patientData
}

import { useCasesStore } from '@/stores/cases.store'

// Store para sincronización de casos
const casesStore = useCasesStore()

/**
 * Función que se ejecuta cuando se guarda un nuevo caso
 */
const handleCaseSaved = (caseData: any) => {
  // Actualizar caso actual para poder asignar patólogo
  currentCase.value = caseData
  
  // Notificar al store que se ha creado un nuevo caso
  casesStore.notifyCaseCreated()
  
  // También mantener el evento para compatibilidad
  window.dispatchEvent(new CustomEvent('case-created', {
    detail: {
      case: caseData,
      timestamp: new Date().toISOString()
    }
  }))
  
  // Aquí podrías agregar lógica adicional como:
  // - Notificar a otros componentes
  // - Actualizar el estado global
  // - Mostrar notificaciones adicionales
  // - Redirigir a otra vista si es necesario
}
</script>