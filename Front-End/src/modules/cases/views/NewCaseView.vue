<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="p-6">
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div class="space-y-6">
          <NewCase 
            ref="newCaseRef"
            @case-saved="handleCaseSaved"
            @patient-verified="handlePatientVerified"
          />
          
          <AssignPathologistToCase 
            :case-to-assign="currentCase"
          />
        </div>
        
        <div class="space-y-6">
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
import { NewPatient, NewCase, AssignPathologistToCase } from '../components'
import type { PatientData } from '../types'

const currentPageTitle = ref('Nuevo Caso Médico')
const newCaseRef = ref()
const currentCase = ref(null)
const currentPatient = ref<PatientData | null>(null)
const handlePatientSaved = (patientData: PatientData) => { currentPatient.value = patientData; newCaseRef.value?.handleNewPatient?.(patientData) }
const handlePatientDataUpdate = (_patientData: PatientData) => {}
const handlePatientVerified = (patientData: PatientData) => { currentPatient.value = patientData }

import { useCasesStore } from '@/stores/cases.store'

const casesStore = useCasesStore()
const handleCaseSaved = (caseData: any) => {
  currentCase.value = caseData
  casesStore.notifyCaseCreated()
  window.dispatchEvent(new CustomEvent('case-created', { detail: { case: caseData, timestamp: new Date().toISOString() } }))
}
</script>