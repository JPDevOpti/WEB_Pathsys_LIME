<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />

    <div class="p-6">
      <!-- Permisos -->
      <AccessDeniedAlert v-if="!canAccessStatistics" />

      <!-- Contenido principal -->
      <div v-else class="space-y-6">
        <TestsReport />
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { AdminLayout } from '@/shared'
import PageBreadcrumb from '@/shared/components/navigation/PageBreadcrumb.vue'
import ComponentCard from '@/shared/components/layout/ComponentCard.vue'
import AccessDeniedAlert from '@/shared/components/ui/feedback/AccessDeniedAlert.vue'
import TestsReport from '../components/tests/TestsReport.vue'
import { usePermissions } from '@/shared/composables/usePermissions'

const currentPageTitle = ref('Reportes de Pruebas')
const { canAccessStatistics } = usePermissions()
</script>
