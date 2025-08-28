<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />

    <div class="p-6">
      <!-- Permisos -->
      <AccessDeniedAlert v-if="!canAccessStatistics" />

      <!-- Contenido principal -->
      <div v-else class="space-y-6">
        <EntitiesReport />
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { AdminLayout } from '@/shared'
import { PageBreadcrumb, ComponentCard } from '@/shared/components/common'
import AccessDeniedAlert from '@/shared/components/feedback/AccessDeniedAlert.vue'
import EntitiesReport from '../components/entities/EntitiesReport.vue'
import { usePermissions } from '@/shared/composables/usePermissions'

const currentPageTitle = ref('Reportes de Entidades')
const { canAccessStatistics } = usePermissions()
</script>
