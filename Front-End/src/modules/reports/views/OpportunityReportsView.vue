<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />

    <div class="p-6">
      <!-- Permisos -->
      <AccessDeniedAlert v-if="!canAccessStatistics" />

      <!-- Contenido principal -->
      <div v-else class="space-y-6">
        <OpportunityReport />
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { AdminLayout } from '@/shared'
import { PageBreadcrumb } from '@/shared/components/common'
import AccessDeniedAlert from '@/shared/components/ui/feedback/AccessDeniedAlert.vue'
import OpportunityReport from '../components/opportunity/OpportunityReport.vue'
import { usePermissions } from '@/shared/composables/usePermissions'

const currentPageTitle = ref('Reportes de Oportunidad')
const { canAccessStatistics } = usePermissions()
</script>


