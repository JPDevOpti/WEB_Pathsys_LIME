<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <div class="space-y-6">
        <ComponentCard 
          title="Modificar datos del caso"
          description="Actualice la información del caso existente."
        >
          <template #icon>
            <EditCaseIcon class="w-5 h-5 mr-2 text-blue-600" />
          </template>
          <EditCaseForm 
            :case-code-prop="caseCodeFromRoute"
            @case-updated="handleCaseUpdated"
          />
        </ComponentCard>
      </div>
      
      <div class="space-y-6">
        <ComponentCard 
          title="Modificar los datos del paciente"
          description="Edite los datos demográficos del paciente asociado."
        >
          <template #icon>
            <EditPatientIcon class="w-5 h-5 mr-2 text-blue-600" />
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
import { EditCaseIcon, EditPatientIcon } from '@/assets/icons'
import { EditCaseForm, EditPatientForm } from '../components'
import type { CaseModel, PatientData } from '../types'

const currentPageTitle = ref('Modificar Caso Médico')
const route = useRoute()
const caseCodeFromRoute = computed(() => (Array.isArray(route.params.code) ? route.params.code[0] || '' : (route.params.code as string) || ''))
const currentCase = ref<CaseModel | null>(null)
const currentPatient = ref<PatientData | null>(null)
const handleCaseUpdated = (updatedCase: CaseModel) => { currentCase.value = updatedCase }
const handlePatientUpdated = (patientData: PatientData) => { currentPatient.value = patientData }
</script> 