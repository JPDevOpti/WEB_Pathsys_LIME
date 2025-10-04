<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="pb-6">
      <NewCase 
        ref="newCaseRef"
        @case-saved="handleCaseSaved"
        @patient-verified="handlePatientVerified"
      />
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { AdminLayout } from '@/shared'
import { PageBreadcrumb } from '@/shared/components/navigation'
import { NewCase } from '../components'

const currentPageTitle = ref('Nuevo Caso Médico')
const newCaseRef = ref()
const currentCase = ref(null)
const handlePatientVerified = (_patientData: any) => { /* Handle patient verification if needed */ }

import { useCasesStore } from '@/stores/cases.store'

const casesStore = useCasesStore()
const handleCaseSaved = (caseData: any) => {
  currentCase.value = caseData
  casesStore.notifyCaseCreated()
  window.dispatchEvent(new CustomEvent('case-created', { detail: { case: caseData, timestamp: new Date().toISOString() } }))
}
</script>