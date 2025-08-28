<template>
  <AdminLayout>
    <div class="grid grid-cols-12 gap-4 md:gap-6 p-6 bg-gray-50 min-h-screen">
      <div class="col-span-12 space-y-4 xl:col-span-7">
        <div class="flex-shrink-0">
          <MetricsBlocks />
        </div>

        <div class="flex-1">
          <CasesByMonth />
        </div>
      </div>

      <div class="col-span-12 xl:col-span-5">
        <div class="h-full">
          <ProgressPercentage />
        </div>
      </div>

      <div class="col-span-12">
        <UrgentCases @show-details="handleShowDetails" @edit="handleEdit" @perform="handlePerform"
          @validate="handleValidate" />
      </div>
    </div>

    <UrgentCaseDetailsModal :case-item="selectedUrgentCase" @close="closeUrgentCaseDetails" @edit="handleEdit"
      @preview="handlePerform" />
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AdminLayout from '@/shared/layouts/AdminLayout.vue'
import MetricsBlocks from '../components/MetricsBlocks.vue'
import CasesByMonth from '../components/CasesByMonth.vue'
import UrgentCases from '../components/UrgentCases.vue'
import ProgressPercentage from '../components/ProgressPercentage.vue'
import UrgentCaseDetailsModal from '../components/UrgentCaseDetailsModal.vue'
import type { CasoUrgente } from '../types/dashboard.types'

const router = useRouter()
const selectedUrgentCase = ref<CasoUrgente | null>(null)

function handleShowDetails(caso: CasoUrgente) {
  selectedUrgentCase.value = caso
}

function closeUrgentCaseDetails() {
  selectedUrgentCase.value = null
}

function handleEdit(caso: CasoUrgente) {
  router.push(`/cases/edit/${caso.codigo}`)
}

function handlePerform(caso: CasoUrgente) {
  router.push(`/results/perform?case=${caso.codigo}`)
}

function handleValidate(caso: CasoUrgente) {
  router.push(`/results/sign?case=${caso.codigo}`)
}
</script>

<style scoped>
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

  .xl\:col-span-7 .flex-shrink-0 {
    flex: 0 0 auto;
  }

  .xl\:col-span-7 .flex-1 {
    flex: 1 1 auto;
    min-height: 0;
  }

  .xl\:col-span-5>* {
    flex: 1;
  }
}

.grid {
  transition: all 0.3s ease-in-out;
}

.grid>div>* {
  transition: transform 0.2s ease-in-out;
}

.grid>div>*:hover {
  transform: translateY(-2px);
}
</style>