<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="p-6">
      <div class="grid grid-cols-1 gap-6">
        <!-- Componente principal de Casos por Aprobar -->
        <CasesToApproveList />
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { AdminLayout } from '@/shared'
import { PageBreadcrumb } from '@/shared/components/navigation'
import CasesToApproveList from '../components/CasesToApproval/CasesToApproveList.vue'

// ============================================================================
// ESTADO DEL COMPONENTE
// ============================================================================

const currentPageTitle = ref('Casos por Aprobar')

// ============================================================================
// FUNCIONES PRINCIPALES (para futuro desarrollo)
// ============================================================================

// Aquí se agregarán las funciones para gestionar casos por aprobar
// cuando se desarrolle la funcionalidad completa
</script>

