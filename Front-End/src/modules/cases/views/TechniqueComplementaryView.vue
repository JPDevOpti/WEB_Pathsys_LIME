<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    <div class="p-6">
      <div class="grid grid-cols-1 gap-6">
        <!-- Componente principal de Nueva técnica complementaria -->
        <!-- Placeholder: componente no disponible tras reorganización -->
        <div class="p-4 bg-yellow-50 border border-yellow-200 rounded text-yellow-800">
          Pending: Complementary Technique form component
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { AdminLayout } from '@/shared'
import { PageBreadcrumb } from '@/shared/components/navigation'
// import NewTechniqueComplementary from '../components/create/NewTechniqueComplementary.vue'

// ============================================================================
// ESTADO DEL COMPONENTE
// ============================================================================

const currentPageTitle = ref('Técnicas Complementarias')

// ============================================================================
// FUNCIONES PRINCIPALES (para futuro desarrollo)
// ============================================================================

// Aquí se agregarán las funciones para gestionar técnicas complementarias
// cuando se desarrolle la funcionalidad completa
</script>
