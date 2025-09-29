<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="currentPageTitle" />
    
    <div class="space-y-6">
      <ComponentCard 
        title="Técnicas Complementarias"
        description="Gestión y seguimiento de técnicas complementarias para casos patológicos."
      >
        <template #icon>
          <TestIcon size="20" color="#2563eb" />
        </template>
        
        <ComplementaryTechniquesList 
          @show-details="handleShowDetails"
          @edit-technique="handleEditTechnique"
        />
      </ComponentCard>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { AdminLayout } from '@/shared'
import { PageBreadcrumb, ComponentCard } from '@/shared/components/common'
import { TestIcon } from '@/assets/icons'
import ComplementaryTechniquesList from '../components/ComplementaryTechniques/ComplementaryTechniquesList.vue'
import type { TecnicaComplementaria } from '../types/complementaryTechniques.types'

const currentPageTitle = ref('Técnicas Complementarias')

const handleShowDetails = (tecnica: TecnicaComplementaria) => {
  console.log('Mostrar detalles de técnica:', tecnica)
  // TODO: Abrir modal o navegar a página de detalles
}

const handleEditTechnique = (tecnica: TecnicaComplementaria) => {
  console.log('Editar técnica:', tecnica)
  // TODO: Navegar a página de edición
}
</script>

<style scoped>
/* Estilos específicos si es necesario */
</style>
