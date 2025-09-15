<template>
  <AdminLayout>
    <div class="grid grid-cols-12 gap-4 md:gap-6 p-4 md:p-6 bg-gray-50">
      <div class="col-span-12 space-y-4 xl:col-span-7">
        <MetricsBlocks />
        <CasesByMonth />
      </div>

      <div class="col-span-12 xl:col-span-5">
        <OportunityPercentage />
      </div>

      <div class="col-span-12">
        <UrgentCases @show-details="handleShowDetails" />
      </div>
    </div>

    <UrgentCaseDetailsModal :case-item="selectedUrgentCase" @close="closeUrgentCaseDetails" />
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AdminLayout from '@/shared/layouts/AdminLayout.vue'
import MetricsBlocks from '../components/MetricsBlocks.vue'
import CasesByMonth from '../components/CasesByMonth.vue'
import UrgentCases from '../components/UrgentCases.vue'
import OportunityPercentage from '../components/OportunityPercentage.vue'
import UrgentCaseDetailsModal from '../components/UrgentCaseDetailsModal.vue'
import type { CasoUrgente } from '../types/dashboard.types'

const selectedUrgentCase = ref<CasoUrgente | null>(null)

function handleShowDetails(caso: CasoUrgente) {
  selectedUrgentCase.value = caso
}

function closeUrgentCaseDetails() {
  selectedUrgentCase.value = null
}
</script>

<style scoped>
@media (max-width: 768px) {
  .grid {
    gap: 1rem;
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .grid {
    gap: 0.75rem;
    padding: 0.75rem;
  }
}
</style>