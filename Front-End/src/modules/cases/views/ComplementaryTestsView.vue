<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="p-6">
      <div class="grid grid-cols-1 gap-6">
        <!-- Componente principal de Nueva Prueba Complementaria -->
        <NewComplementaryTest />
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { AdminLayout } from '@/shared'
import { PageBreadcrumb } from '@/shared/components/navigation'
import NewComplementaryTest from '../components/NewComplementaryTest.vue'

// ============================================================================
// ESTADO DEL COMPONENTE
// ============================================================================

const currentPageTitle = ref('Pruebas Complementarias')

// ============================================================================
// FUNCIONES PRINCIPALES (para futuro desarrollo)
// ============================================================================

// Aquí se agregarán las funciones para gestionar pruebas complementarias
// cuando se desarrolle la funcionalidad completa
</script>
